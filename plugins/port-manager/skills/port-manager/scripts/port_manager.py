#!/usr/bin/env python3
"""로컬 개발 서버 TCP 포트 조회와 안전한 종료·교체 도구."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple


LISTENER_PATTERN = re.compile(r"\bTCP\s+(.+):(\d+)\s+\(LISTEN\)")
DATABASE_EXECUTABLES = {
    "postgres", "postgresql", "mysqld", "mariadbd", "redis-server",
    "mongod", "couchdb", "influxd", "clickhouse-server", "rabbitmq-server",
}
SENSITIVE_FLAG = re.compile(
    r"(?i)(?:token|secret|password|passwd|api[-_]?key|authorization|cookie|"
    r"credential|client[-_]?secret|access[-_]?key|private[-_]?key)"
)
DEV_NAME = re.compile(r"(?i)(?:^|[/\\])dev[-_]?server(?:\.(?:py|js|mjs|cjs|ts))?$")
KNOWN_DEV_TOOLS = {
    "vite", "webpack-dev-server", "parcel", "react-scripts", "astro", "nuxt",
    "wrangler", "svelte-kit", "ng", "http.server", "uvicorn", "flask",
}
KNOWN_SCRIPT_WORDS = {"dev", "start", "serve", "preview", "run", "-m"}
SAFE_VALUE_FLAGS = {"--port", "-p", "--host", "--hostname"}


class PortManagerError(RuntimeError):
    pass


@dataclass
class Listener:
    port: int
    pid: int
    user: str
    command: str
    endpoints: Set[str] = field(default_factory=set)
    socket_ids: Set[str] = field(default_factory=set)


@dataclass
class RepoInfo:
    root: str
    name: str
    branch: str


@dataclass
class ProcessInfo:
    pid: int
    ppid: int
    user: str
    started: str
    elapsed: str
    cpu_time: str
    cpu_percent: str
    rss_kb: Optional[int]
    comm: str
    command: str
    cwd: Optional[str]
    repo: Optional[RepoInfo]
    classification: str
    is_dev_server: bool
    reason: str


@dataclass
class LaunchPlan:
    repo: RepoInfo
    package_root: Path
    package_manager: str
    manager_binary: str
    script_name: str
    framework: str
    args: List[str]
    use_port_environment: bool


@dataclass(frozen=True)
class WorktreeRecord:
    path: Path
    head: str
    branch: Optional[str]
    locked: bool
    prunable: bool
    is_main: bool


@dataclass
class WorktreeRemovalPlan:
    repository: Path
    records: Dict[Path, WorktreeRecord]
    ports_by_worktree: Dict[Path, Set[int]]
    allowed_listener_pairs: Dict[Path, Set[Tuple[int, int]]]
    process_by_pid: Dict[int, ProcessInfo]


def run_readonly(command: Sequence[str], timeout: float = 3.0) -> subprocess.CompletedProcess:
    """읽기 전용 명령을 실행하되 원문 stderr를 내보내지 않는다."""
    try:
        return subprocess.run(
            list(command), capture_output=True, text=True, check=False, timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PortManagerError(f"필요한 로컬 명령을 실행하지 못했습니다: {Path(command[0]).name}") from exc


def parse_lsof_listeners(output: str) -> List[Listener]:
    """lsof의 기본 표 출력을 PID와 포트 기준으로 묶어 IPv4/IPv6 중복을 제거한다."""
    grouped: Dict[Tuple[int, int], Listener] = {}
    for line in output.splitlines():
        match = LISTENER_PATTERN.search(line)
        if not match:
            continue
        columns = line.split()
        if len(columns) < 3 or not columns[1].isdigit():
            continue
        pid = int(columns[1])
        port = int(match.group(2))
        family = columns[4] if len(columns) > 4 else "TCP"
        endpoint = f"{family} {match.group(1)}"
        # macOS lsof의 DEVICE 열은 TCP 소켓마다 고유한 커널 식별자를 제공한다.
        socket_id = columns[5] if len(columns) > 5 else ""
        key = (pid, port)
        if key not in grouped:
            grouped[key] = Listener(
                port=port, pid=pid, user=columns[2], command=columns[0], endpoints=set(), socket_ids=set()
            )
        grouped[key].endpoints.add(endpoint)
        if socket_id:
            grouped[key].socket_ids.add(socket_id)
    return sorted(grouped.values(), key=lambda item: (item.port, item.pid))


def list_listeners() -> List[Listener]:
    binary = shutil.which("lsof")
    if not binary:
        raise PortManagerError("macOS의 `lsof`를 찾을 수 없습니다. PATH와 macOS 명령 도구를 확인하세요.")
    result = run_readonly([binary, "-nP", "-iTCP", "-sTCP:LISTEN"], timeout=10.0)
    # lsof는 권한이 없는 프로세스를 일부 생략할 수 있다. stderr는 환경 정보를 포함할 수 있어 출력하지 않는다.
    if result.returncode not in (0, 1):
        raise PortManagerError("`lsof`가 리스너 목록을 완전히 읽지 못했습니다.")
    return parse_lsof_listeners(result.stdout)


def read_ps_stats(pid: int) -> Optional[dict]:
    result = run_readonly(
        ["ps", "-ww", "-p", str(pid), "-o", "pid=,ppid=,lstart=,etime=,time=,%cpu=,rss="],
        timeout=3.0,
    )
    fields = result.stdout.split()
    if result.returncode != 0 or len(fields) < 11 or not fields[0].isdigit():
        return None
    try:
        rss_kb = int(fields[10])
    except ValueError:
        rss_kb = None
    return {
        "pid": int(fields[0]),
        "ppid": int(fields[1]),
        "started": " ".join(fields[2:7]),
        "elapsed": fields[7],
        "cpu_time": fields[8],
        "cpu_percent": fields[9],
        "rss_kb": rss_kb,
    }


def read_ps_field(pid: int, field_name: str) -> str:
    result = run_readonly(["ps", "-ww", "-p", str(pid), "-o", f"{field_name}="], timeout=3.0)
    return result.stdout.strip()


def read_process_cwd(pid: int) -> Optional[str]:
    binary = shutil.which("lsof")
    if not binary:
        return None
    result = run_readonly([binary, "-a", "-nP", "-p", str(pid), "-d", "cwd", "-Fn"], timeout=3.0)
    for line in result.stdout.splitlines():
        if line.startswith("n") and len(line) > 1:
            return line[1:]
    return None


def git_output(cwd: str, *args: str) -> Optional[str]:
    try:
        result = run_readonly(["git", "-C", cwd, "rev-parse", *args], timeout=2.0)
    except PortManagerError:
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def identify_repo(cwd: Optional[str]) -> Optional[RepoInfo]:
    if not cwd:
        return None
    try:
        path = Path(cwd).resolve()
        if not any((candidate / ".git").exists() for candidate in (path, *path.parents)):
            return None
    except OSError:
        return None
    root_value = git_output(cwd, "--show-toplevel")
    common_value = git_output(cwd, "--git-common-dir")
    if not root_value or not common_value:
        return None
    try:
        root = Path(root_value).resolve()
        common = Path(common_value)
        if not common.is_absolute():
            common = (Path(cwd) / common).resolve()
        else:
            common = common.resolve()
        # worktree의 .git 파일이 가리키는 공통 Git 디렉터리의 부모가 저장소 정식 이름이다.
        canonical_root = common.parent if common.name == ".git" else common
        name = canonical_root.name or root.name
    except OSError:
        return None
    branch = git_output(cwd, "--abbrev-ref", "HEAD") or "(분리된 HEAD)"
    if branch == "HEAD":
        branch = "(분리된 HEAD)"
    return RepoInfo(root=str(root), name=name, branch=branch)


def parent_command_chain(ppid: int, limit: int = 6) -> List[str]:
    commands: List[str] = []
    seen: Set[int] = set()
    current = ppid
    while current > 1 and current not in seen and len(commands) < limit:
        seen.add(current)
        stats = read_ps_stats(current)
        if not stats:
            break
        command = read_ps_field(current, "command")
        if command:
            commands.append(command)
        current = stats["ppid"]
    return commands


def executable_name(comm: str, raw_command: str) -> str:
    candidate = comm.strip() or (shlex.split(raw_command)[0] if raw_command else "")
    return Path(candidate).name.casefold()


def classify_process(comm: str, raw_command: str, parents: Iterable[str], in_repo: bool) -> Tuple[str, bool, str]:
    """개발 서버만 보수적으로 확정하고 DB·시스템 프로세스는 별도 분류한다."""
    executable = executable_name(comm, raw_command)
    if executable in DATABASE_EXECUTABLES:
        return "DB/서비스 프로세스", False, "실행 파일이 DB 또는 서비스로 식별됨"

    command_chain = " ".join([raw_command, *parents]).casefold()
    tokens: List[str] = []
    for value in [raw_command, *parents]:
        try:
            tokens.extend(shlex.split(value))
        except ValueError:
            tokens.extend(value.split())
    lowered = [Path(token).name.casefold() for token in tokens]

    explicit_patterns = (
        r"\bvite(?:\s|$)", r"\bwebpack-dev-server\b", r"\bwebpack\s+serve\b",
        r"\bparcel(?:\s|$)", r"\breact-scripts\s+start\b", r"\bnext\s+dev\b",
        r"\bnuxt\s+dev\b", r"\bastro\s+dev\b", r"\bastro\s+preview\b",
        r"\bwrangler\s+dev\b", r"\bsvelte-kit\s+dev\b", r"\bng\s+serve\b",
        r"\bpython(?:\d(?:\.\d+)?)?\s+-m\s+http\.server\b",
    )
    if any(re.search(pattern, command_chain) for pattern in explicit_patterns):
        return "개발 서버", True, "프런트엔드 개발 서버 실행 명령 확인"
    if any(token in KNOWN_DEV_TOOLS for token in lowered):
        return "개발 서버", True, "프로세스 인수에서 알려진 개발 서버 도구 확인"
    if in_repo and any(DEV_NAME.search(token) for token in tokens):
        return "개발 서버", True, "저장소 안의 dev-server 스크립트 확인"
    if in_repo and executable in {"node", "nodejs", "python", "python3", "bun", "deno"}:
        if re.search(r"\b(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?dev\b", command_chain):
            return "개발 서버", True, "저장소에서 패키지 관리자의 dev 스크립트로 실행됨"
    if executable in {"launchd", "mdnsresponder", "controlcenter", "sharingd", "rapportd"}:
        return "시스템 서비스", False, "macOS 시스템 프로세스"
    if in_repo and executable in {"node", "nodejs", "bun", "deno", "python", "python3"}:
        return "개발 서버 후보", False, "저장소의 런타임 프로세스지만 개발 서버 실행 인수가 확인되지 않음"
    return "미분류", False, "명령만으로 개발 서버라고 확인할 수 없음"


def safe_command_summary(comm: str, raw_command: str) -> str:
    """명령 인수는 allowlist만 보여 민감 인수·인라인 코드를 출력하지 않는다."""
    executable = Path(comm.strip() or "프로세스").name
    try:
        tokens = shlex.split(raw_command)
    except ValueError:
        tokens = raw_command.split()
    summary: List[str] = [executable]
    framework_words = KNOWN_DEV_TOOLS | {"next", "python", "python3", "node", "nodejs", "npm", "pnpm", "yarn", "bun"}
    i = 0
    while i < len(tokens) and len(summary) < 14:
        token = tokens[i]
        low = Path(token).name.casefold()
        if SENSITIVE_FLAG.search(token):
            if token.startswith("-"):
                summary.extend([token.split("=", 1)[0], "[민감값 숨김]"])
                if "=" not in token and i + 1 < len(tokens):
                    i += 1
            i += 1
            continue
        if token in SAFE_VALUE_FLAGS:
            summary.append(token)
            if i + 1 < len(tokens) and re.fullmatch(r"[A-Za-z0-9.:-]+", tokens[i + 1]):
                summary.append(tokens[i + 1])
                i += 1
            i += 1
            continue
        if low in {"--strictport", "--strict-port", "--strict"}:
            summary.append(low)
        elif low in framework_words or low in KNOWN_SCRIPT_WORDS:
            summary.append(low)
        elif low == "http.server":
            summary.append(low)
        elif token in {"-m"} and i + 1 < len(tokens) and tokens[i + 1] == "http.server":
            summary.extend(["-m", "http.server"])
            i += 1
        elif re.search(r"\.(?:py|mjs|cjs|js|ts)$", low) and not SENSITIVE_FLAG.search(low):
            summary.append(Path(token).name)
        elif token in {"-e", "--eval"}:
            summary.extend([token, "[인라인 코드 생략]"])
            if i + 1 < len(tokens):
                i += 1
        i += 1
    # 중복 토큰은 첫 등장만 남긴다.
    return " ".join(dict.fromkeys(summary))[:220]


def inspect_process(listener: Listener) -> Optional[ProcessInfo]:
    stats = read_ps_stats(listener.pid)
    if not stats:
        return None
    comm = read_ps_field(listener.pid, "comm") or listener.command
    raw_command = read_ps_field(listener.pid, "command")
    cwd = read_process_cwd(listener.pid)
    repo = identify_repo(cwd)
    parents = parent_command_chain(stats["ppid"])
    classification, is_dev, reason = classify_process(comm, raw_command, parents, repo is not None)
    return ProcessInfo(
        pid=listener.pid,
        ppid=stats["ppid"],
        user=listener.user,
        started=stats["started"],
        elapsed=stats["elapsed"],
        cpu_time=stats["cpu_time"],
        cpu_percent=stats["cpu_percent"],
        rss_kb=stats["rss_kb"],
        comm=comm,
        command=safe_command_summary(comm, raw_command),
        cwd=cwd,
        repo=repo,
        classification=classification,
        is_dev_server=is_dev,
        reason=reason,
    )


def discover() -> List[Tuple[Listener, Optional[ProcessInfo]]]:
    process_cache: Dict[int, Optional[ProcessInfo]] = {}
    rows: List[Tuple[Listener, Optional[ProcessInfo]]] = []
    for listener in list_listeners():
        if listener.pid not in process_cache:
            process_cache[listener.pid] = inspect_process(listener)
        rows.append((listener, process_cache[listener.pid]))
    return rows


def port_is_valid(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("포트는 숫자여야 합니다.") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("포트는 1~65535 범위여야 합니다.")
    return port


def idle_label() -> str:
    return "알 수 없음 (OS 리스너 정보로 요청 상태 판정 불가)"


def repo_matches(info: Optional[ProcessInfo], repo_name: str) -> bool:
    return bool(info and info.repo and info.repo.name == repo_name)


def project_label(info: Optional[ProcessInfo]) -> str:
    if not info:
        return "(프로세스 정보 접근 불가)"
    if info.repo:
        return f"{info.repo.name} [{info.repo.branch}] · {info.repo.root}"
    if info.cwd:
        return f"(저장소 아님) {info.cwd}"
    return "(작업 경로 접근 불가)"


def memory_label(info: Optional[ProcessInfo]) -> str:
    if not info or info.rss_kb is None:
        return "—"
    return f"{info.rss_kb / 1024:.1f} MB"


def format_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    values = [[str(value) for value in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in values:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))
    line = "-+-".join("-" * width for width in widths)
    output = [" | ".join(header.ljust(widths[index]) for index, header in enumerate(headers)), line]
    output.extend(" | ".join(row[index].ljust(widths[index]) for index in range(len(headers))) for row in values)
    return "\n".join(output)


def row_for(listener: Listener, info: Optional[ProcessInfo]) -> List[str]:
    return [
        str(listener.port), project_label(info), str(listener.pid),
        f"{info.started} ({info.elapsed})" if info else "—",
        idle_label(), memory_label(info),
    ]


def print_all() -> None:
    rows = discover()
    confirmed = [(listener, info) for listener, info in rows if info and info.is_dev_server]
    other = [(listener, info) for listener, info in rows if not (info and info.is_dev_server)]
    print("확인된 로컬 개발 서버")
    print(format_table(
        ["포트", "프로젝트 / 워크트리", "PID", "시작 시각 (경과)", "유휴 판단", "RSS"],
        [row_for(listener, info) for listener, info in confirmed] or [["—", "없음", "—", "—", "—", "—"]],
    ))
    print("\n전체 TCP LISTEN 중 개발 서버로 확인되지 않은 리스너 (자동 종료 보호 대상)")
    print(format_table(
        ["포트", "분류", "프로세스", "PID", "소유자", "상세 경로", "명령 요약"],
        [[
            str(listener.port), info.classification if info else "미분류", listener.command,
            str(listener.pid), listener.user, info.cwd or "(접근 불가)", info.command if info else "—",
        ] for listener, info in other] or [["—", "없음", "—", "—", "—", "—", "—"]],
    ))
    print("\n유휴 여부는 애플리케이션 요청 상태를 확인할 수 없어 알 수 없음으로 표시합니다.")


def print_detail(port: int) -> None:
    rows = [(listener, info) for listener, info in discover() if listener.port == port]
    if not rows:
        print(f"TCP LISTEN 중인 프로세스가 포트 {port}에서 발견되지 않았습니다.")
        return
    for index, (listener, info) in enumerate(rows, start=1):
        if index > 1:
            print()
        print(f"포트 {port} · 리스너 {index}/{len(rows)}")
        print(f"분류: {info.classification if info else '미분류'}{(' — ' + info.reason) if info else ''}")
        print(f"프로젝트/워크트리: {project_label(info)}")
        print(f"PID / PPID: {listener.pid} / {info.ppid if info else '—'}")
        print(f"소유자: {listener.user}")
        print(f"시작 시각 / 경과: {info.started} / {info.elapsed}" if info else "시작 시각 / 경과: 접근 불가")
        print(f"유휴 판단: {idle_label()}")
        print(f"메모리 RSS: {memory_label(info)}")
        print(f"상세 경로: {info.cwd if info and info.cwd else '(접근 불가)'}")
        print(f"명령 요약: {info.command if info else '—'}")
        print(f"LISTEN 주소: {', '.join(sorted(listener.endpoints))}")
        if info and not info.is_dev_server:
            print("안전: 개발 서버로 확정되지 않아 종료/교체 대상으로 삼지 않습니다.")


def print_repo(repo_name: str) -> None:
    matching = [(listener, info) for listener, info in discover() if repo_matches(info, repo_name)]
    print(f"저장소 이름 정확 일치: {repo_name}")
    if not matching:
        print("일치하는 Git 저장소의 TCP LISTEN 프로세스가 없습니다.")
        return
    roots = sorted({info.repo.root for _, info in matching if info and info.repo})
    if len(roots) > 1:
        print("동일한 저장소 이름을 가진 서로 다른 경로를 별도로 표시합니다.")
    print(format_table(
        ["포트", "분류", "프로젝트 / 워크트리 경로", "PID", "시작 시각 (경과)", "명령 요약"],
        [[
            str(listener.port), info.classification if info else "미분류", project_label(info),
            str(listener.pid), f"{info.started} ({info.elapsed})" if info else "—",
            info.command if info else "—",
        ] for listener, info in matching],
    ))


def identity(info: ProcessInfo) -> Tuple[int, int, str, str, Optional[str], str]:
    return (info.pid, info.ppid, info.started, Path(info.comm).name, info.cwd, info.user)


def listeners_by_port(listeners: Sequence[Listener]) -> Dict[int, Set[int]]:
    grouped: Dict[int, Set[int]] = {}
    for listener in listeners:
        grouped.setdefault(listener.port, set()).add(listener.pid)
    return grouped


def socket_ids_by_port(listeners: Sequence[Listener]) -> Dict[int, Dict[int, Set[str]]]:
    grouped: Dict[int, Dict[int, Set[str]]] = {}
    for listener in listeners:
        grouped.setdefault(listener.port, {}).setdefault(listener.pid, set()).update(listener.socket_ids)
    return grouped


def _git_text(cwd: Path, *args: str) -> Optional[str]:
    try:
        result = run_readonly(["git", "-C", str(cwd), *args], timeout=5.0)
    except PortManagerError:
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _absolute_git_path(cwd: Path, value: str) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else cwd / path).resolve()


def _read_worktrees(repository: Path) -> List[WorktreeRecord]:
    try:
        result = run_readonly(
            ["git", "-C", str(repository), "worktree", "list", "--porcelain", "-z"], timeout=5.0
        )
    except PortManagerError as exc:
        raise PortManagerError("Git 워크트리 등록을 확인하지 못했습니다.") from exc
    if result.returncode != 0:
        raise PortManagerError("Git 워크트리 등록을 확인하지 못했습니다.")

    records: List[WorktreeRecord] = []
    for section in result.stdout.split("\0\0"):
        if not section:
            continue
        fields: Dict[str, str] = {}
        for item in section.split("\0"):
            key, separator, value = item.partition(" ")
            fields[key] = value if separator else ""
        if not fields.get("worktree") or not fields.get("HEAD"):
            raise PortManagerError("Git 워크트리 목록 형식을 확인하지 못했습니다.")
        path = Path(fields["worktree"]).resolve()
        git_dir_value = _git_text(path, "rev-parse", "--git-dir")
        common_dir_value = _git_text(path, "rev-parse", "--git-common-dir")
        if not git_dir_value or not common_dir_value:
            raise PortManagerError(f"워크트리 Git 등록 경로를 확인하지 못했습니다: {path}")
        git_dir = _absolute_git_path(path, git_dir_value)
        common_dir = _absolute_git_path(path, common_dir_value)
        records.append(WorktreeRecord(
            path=path,
            head=fields["HEAD"],
            branch=fields.get("branch") or None,
            locked="locked" in fields,
            prunable="prunable" in fields,
            is_main=git_dir == common_dir,
        ))
    if not records:
        raise PortManagerError("등록된 Git 워크트리를 찾지 못했습니다.")
    return records


def _path_is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _worktree_safety_error(record: WorktreeRecord, execution_directory: Path) -> Optional[str]:
    if record.is_main:
        return f"기본 워크트리는 제거하지 않습니다: {record.path}"
    if _path_is_within(execution_directory, record.path):
        return f"현재 Codex 실행 디렉터리가 포함된 워크트리는 제거하지 않습니다: {record.path}"
    if record.locked:
        return f"잠금된 워크트리는 제거하지 않습니다: {record.path}"
    if record.prunable:
        return f"prunable 상태의 워크트리는 등록이 모호해 제거하지 않습니다: {record.path}"
    if not record.path.is_dir():
        return f"워크트리 경로가 없어 제거하지 않습니다: {record.path}"
    if not record.branch or not record.branch.startswith("refs/heads/"):
        return f"브랜치가 연결되지 않은 워크트리는 제거하지 않습니다: {record.path}"
    branch_head = _git_text(record.path, "rev-parse", "--verify", f"{record.branch}^{{commit}}")
    current_head = _git_text(record.path, "rev-parse", "--verify", "HEAD^{commit}")
    if not branch_head or branch_head != record.head or current_head != record.head:
        return f"워크트리 HEAD와 보존할 브랜치가 일치하지 않아 제거하지 않습니다: {record.path}"
    try:
        status = run_readonly([
            "git", "-C", str(record.path), "status", "--porcelain=v1",
            "--untracked-files=all", "--ignored=matching",
        ], timeout=10.0)
    except PortManagerError:
        return f"워크트리의 변경·미추적·무시 파일을 확인하지 못해 제거하지 않습니다: {record.path}"
    if status.returncode != 0:
        return f"워크트리 상태를 확인하지 못해 제거하지 않습니다: {record.path}"
    if status.stdout.strip():
        return f"변경·미추적·무시 파일이 있는 워크트리는 제거하지 않습니다: {record.path}"
    return None


def _record_for_path(records: Sequence[WorktreeRecord], path: Path) -> Optional[WorktreeRecord]:
    resolved = path.resolve()
    matches = [record for record in records if record.path == resolved]
    return matches[0] if len(matches) == 1 else None


def _worktree_listener_conflict(
    record: WorktreeRecord, allowed_pairs: Set[Tuple[int, int]]
) -> Optional[str]:
    for listener in list_listeners():
        if (listener.pid, listener.port) in allowed_pairs:
            continue
        info = inspect_process(listener)
        if not info or not info.cwd:
            if listener.user == getpass.getuser() or (info and info.is_dev_server):
                return f"PID {listener.pid} 포트 {listener.port}의 워크트리 소속을 확인할 수 없어 제거를 보류합니다."
            continue
        try:
            process_cwd = Path(info.cwd).resolve()
        except OSError:
            return f"PID {listener.pid} 포트 {listener.port}의 작업 경로가 모호해 제거를 보류합니다."
        if _path_is_within(process_cwd, record.path):
            return f"선택하지 않은 PID {listener.pid} 포트 {listener.port}가 워크트리에서 실행 중입니다."
    return None


def prepare_worktree_removal(ports: Sequence[int]) -> WorktreeRemovalPlan:
    selected_ports = set(ports)
    initial = list_listeners()
    owner_map = listeners_by_port(initial)
    records_by_path: Dict[Path, WorktreeRecord] = {}
    ports_by_worktree: Dict[Path, Set[int]] = {}
    allowed_pairs: Dict[Path, Set[Tuple[int, int]]] = {}
    process_by_pid: Dict[int, ProcessInfo] = {}
    repository_anchor: Optional[Path] = None
    common_directories: Set[Path] = set()
    execution_directory = Path.cwd().resolve()

    for port in sorted(selected_ports):
        owners = owner_map.get(port, set())
        if not owners:
            raise PortManagerError(f"포트 {port}에 실행 중인 리스너가 없어 워크트리 소속을 확인할 수 없습니다.")
        port_records: Set[Path] = set()
        for listener in (item for item in initial if item.port == port):
            info = process_by_pid.get(listener.pid)
            if info is None:
                info = inspect_process(listener)
                if info:
                    process_by_pid[listener.pid] = info
            if not info or not info.is_dev_server or info.user != getpass.getuser():
                raise PortManagerError(
                    f"포트 {port}의 모든 소유자를 현재 계정의 개발 서버로 확인하지 못했습니다. 종료하지 않았습니다."
                )
            if not info.cwd or not info.repo:
                raise PortManagerError(f"PID {listener.pid}의 작업 경로와 저장소를 확인하지 못했습니다.")
            worktree_path = Path(info.repo.root).resolve()
            if not _path_is_within(Path(info.cwd), worktree_path):
                raise PortManagerError(f"PID {listener.pid}의 작업 경로가 저장소 루트와 맞지 않습니다.")
            current_records = _read_worktrees(worktree_path)
            record = _record_for_path(current_records, worktree_path)
            if not record:
                raise PortManagerError(f"PID {listener.pid}의 경로가 등록된 Git 워크트리가 아닙니다.")
            safety_error = _worktree_safety_error(record, execution_directory)
            if safety_error:
                raise PortManagerError(safety_error)
            common_value = _git_text(record.path, "rev-parse", "--git-common-dir")
            if not common_value:
                raise PortManagerError("Git 공통 디렉터리를 확인하지 못했습니다.")
            common_directory = _absolute_git_path(record.path, common_value)
            common_directories.add(common_directory)
            main_records = [candidate for candidate in current_records if candidate.is_main]
            if len(main_records) != 1:
                raise PortManagerError("기본 워크트리를 하나로 확인하지 못해 제거를 보류합니다.")
            if repository_anchor is None:
                repository_anchor = main_records[0].path
            records_by_path[record.path] = record
            port_records.add(record.path)
            ports_by_worktree.setdefault(record.path, set()).add(port)
            allowed_pairs.setdefault(record.path, set()).add((listener.pid, port))
        if len(port_records) != 1:
            raise PortManagerError(f"포트 {port} 소유자들이 서로 다른 워크트리에 있어 제거 대상을 특정하지 못했습니다.")

    if len(common_directories) != 1 or not repository_anchor:
        raise PortManagerError("선택 포트들이 서로 다른 Git 저장소에 있어 한 번에 워크트리를 제거하지 않습니다.")
    plan = WorktreeRemovalPlan(
        repository=repository_anchor,
        records=records_by_path,
        ports_by_worktree=ports_by_worktree,
        allowed_listener_pairs=allowed_pairs,
        process_by_pid=process_by_pid,
    )
    for path, record in plan.records.items():
        conflict = _worktree_listener_conflict(record, plan.allowed_listener_pairs[path])
        if conflict:
            raise PortManagerError(conflict)
    return plan


def _recheck_worktree_plan(
    plan: WorktreeRemovalPlan,
    path: Path,
    allowed_pairs: Set[Tuple[int, int]],
) -> Tuple[bool, str]:
    expected = plan.records[path]
    try:
        current_records = _read_worktrees(plan.repository)
    except PortManagerError as exc:
        return False, str(exc)
    current = _record_for_path(current_records, path)
    if current != expected:
        return False, f"워크트리 등록·HEAD·브랜치가 사전 확인 후 바뀌었습니다: {path}"
    safety_error = _worktree_safety_error(current, Path.cwd().resolve())
    if safety_error:
        return False, safety_error
    conflict = _worktree_listener_conflict(current, allowed_pairs)
    if conflict:
        return False, conflict
    return True, ""


def delete_ports_and_worktrees(
    ports: Sequence[int], force: bool = False, grace_seconds: float = 4.0
) -> Tuple[bool, List[str]]:
    """명시된 포트만 종료한 뒤, 모든 안전 조건을 다시 확인하고 연결 워크트리를 제거한다."""
    plan = prepare_worktree_removal(ports)

    def check_before_signal(pid: int, current: ProcessInfo) -> Tuple[bool, str]:
        if not current.repo:
            return False, "프로세스 저장소를 다시 확인하지 못했습니다."
        path = Path(current.repo.root).resolve()
        record = plan.records.get(path)
        if not record or not current.cwd or not _path_is_within(Path(current.cwd), path):
            return False, "프로세스의 cwd와 워크트리 소속이 사전 확인과 다릅니다."
        return _recheck_worktree_plan(plan, path, plan.allowed_listener_pairs[path])

    stopped, messages = terminate_ports(
        ports, force=force, grace_seconds=grace_seconds, pre_signal_check=check_before_signal
    )
    if not stopped:
        for port in sorted(set(ports)):
            remaining = sorted({item.pid for item in list_listeners() if item.port == port})
            messages.append(
                f"포트 {port}: " + (f"현재 리스너 PID {', '.join(map(str, remaining))}" if remaining else "현재 리스너 없음")
            )
        messages.append("워크트리 유지: 모든 대상 서버의 종료를 확인하지 못했습니다.")
        return False, messages

    current_listeners = list_listeners()
    occupied_ports = sorted(set(ports).intersection(item.port for item in current_listeners))
    if occupied_ports:
        messages.append(
            "워크트리 유지: 종료 후 선택 포트를 다른 프로세스가 점유했습니다 (포트 "
            + ", ".join(map(str, occupied_ports)) + ")."
        )
        return False, messages

    for path, record in plan.records.items():
        expected_pids = {
            pid for pid, info in plan.process_by_pid.items()
            if info.repo and Path(info.repo.root).resolve() == path
        }
        still_running = []
        for pid in sorted(expected_pids):
            stats = read_ps_stats(pid)
            if stats and stats["started"] == plan.process_by_pid[pid].started:
                still_running.append(pid)
        if still_running:
            messages.append(
                f"PID {', '.join(map(str, still_running))}: 포트 해제 후에도 같은 프로세스가 실행 중입니다."
            )
            messages.append(f"워크트리 유지: {path}")
            return False, messages

        ok, reason = _recheck_worktree_plan(plan, path, set())
        if not ok:
            messages.append(f"워크트리 삭제 직전 재확인 실패: {reason}")
            messages.append(f"서버는 종료됐고 워크트리는 유지했습니다: {path}")
            return False, messages

        def removal_state() -> Optional[str]:
            try:
                registered = _record_for_path(_read_worktrees(plan.repository), path) is not None
            except PortManagerError:
                return None
            exists = path.exists()
            if not registered and not exists:
                return "removed"
            if registered and exists:
                return "retained"
            return "inconsistent"

        def report_removed() -> bool:
            branch_head = _git_text(plan.repository, "rev-parse", "--verify", f"{record.branch}^{{commit}}")
            if branch_head != record.head:
                messages.append(f"워크트리는 제거됐지만 브랜치 보존 검증에 실패했습니다: {path} ({record.branch})")
                return False
            messages.append(f"워크트리 제거 완료, 브랜치 보존 확인: {path} ({record.branch})")
            return True

        try:
            result = subprocess.run(
                ["git", "-C", str(plan.repository), "worktree", "remove", str(path)],
                capture_output=True, text=True, check=False, timeout=15.0,
            )
        except (OSError, subprocess.TimeoutExpired):
            state = removal_state()
            if state == "removed":
                report_removed()
                messages.append("git worktree remove 결과가 시간 초과 뒤 확인됐습니다.")
            elif state == "retained":
                messages.append(f"서버는 종료됐고 워크트리는 유지했습니다: {path} (git worktree remove 실행 실패)")
            else:
                messages.append(f"서버는 종료됐습니다. 워크트리 제거 결과는 확인할 수 없습니다: {path}")
            return False, messages
        if result.returncode != 0:
            state = removal_state()
            if state == "removed":
                report_removed()
                messages.append("Git 명령은 실패를 반환했지만 실제 제거는 확인했습니다.")
            elif state == "retained":
                messages.append(f"서버는 종료됐고 워크트리는 유지했습니다: {path} (Git이 일반 제거를 거부했습니다)")
            else:
                messages.append(f"서버는 종료됐습니다. 워크트리 제거 결과는 확인할 수 없습니다: {path}")
            return False, messages
        if removal_state() != "removed":
            messages.append(f"Git 명령이 성공을 반환했지만 워크트리 제거 상태가 일치하지 않습니다: {path}")
            return False, messages
        if not report_removed():
            return False, messages
    return True, messages


def _process_info_for_pid(pid: int, user: Optional[str] = None) -> Optional[ProcessInfo]:
    current = [listener for listener in list_listeners() if listener.pid == pid]
    selected = next((item for item in current if user is None or item.user == user), None)
    if selected:
        return inspect_process(selected)
    stats = read_ps_stats(pid)
    if not stats:
        return None
    comm = read_ps_field(pid, "comm") or "프로세스"
    command = read_ps_field(pid, "command")
    cwd = read_process_cwd(pid)
    repo = identify_repo(cwd)
    parents = parent_command_chain(stats["ppid"])
    classification, is_dev, reason = classify_process(comm, command, parents, repo is not None)
    return ProcessInfo(
        pid=pid, ppid=stats["ppid"], user=user or "(확인 불가)",
        started=stats["started"], elapsed=stats["elapsed"], cpu_time=stats["cpu_time"],
        cpu_percent=stats["cpu_percent"], rss_kb=stats["rss_kb"], comm=comm,
        command=safe_command_summary(comm, command), cwd=cwd, repo=repo,
        classification=classification, is_dev_server=is_dev, reason=reason,
    )


def _wait_for_release(pid: int, target_ports: Set[int], grace_seconds: float) -> bool:
    deadline = time.monotonic() + grace_seconds
    while time.monotonic() < deadline:
        owner_map = listeners_by_port(list_listeners())
        still_listening = any(pid in owner_map.get(port, set()) for port in target_ports)
        if not still_listening or read_ps_stats(pid) is None:
            return True
        time.sleep(0.2)
    owner_map = listeners_by_port(list_listeners())
    return not any(pid in owner_map.get(port, set()) for port in target_ports)


def _verified_before_signal(
    pid: int,
    expected: ProcessInfo,
    ports: Set[int],
    expected_by_port: Dict[int, Set[int]],
    gone_pids: Set[int],
    expected_socket_ids_by_port: Optional[Dict[int, Dict[int, Set[str]]]] = None,
) -> Tuple[bool, str]:
    current = _process_info_for_pid(pid, expected.user)
    if not current or identity(current) != identity(expected):
        return False, "PID가 사라졌거나 시작 시각·실행 파일·경로·소유자가 바뀌었습니다."
    if not current.is_dev_server or current.user != getpass.getuser():
        return False, "현재 프로세스를 개발 서버·현재 계정 소유로 다시 확인하지 못했습니다."
    current_listeners = list_listeners()
    owner_map = listeners_by_port(current_listeners)
    current_socket_ids = socket_ids_by_port(current_listeners)
    found_owner = False
    for port in ports:
        expected_owners = expected_by_port.get(port, set()) - gone_pids
        current_owners = owner_map.get(port, set())
        if current_owners != expected_owners:
            return False, f"포트 {port} 소유자가 조회 후 바뀌었습니다. 어떤 프로세스도 종료하지 않았습니다."
        expected_socket_ids = (expected_socket_ids_by_port or {}).get(port, {})
        if expected_socket_ids:
            expected_socket_ids = {owner: ids for owner, ids in expected_socket_ids.items() if owner not in gone_pids}
            observed_socket_ids = {
                owner: ids for owner, ids in current_socket_ids.get(port, {}).items() if owner in expected_owners
            }
            if any(expected_socket_ids.values()) and observed_socket_ids != expected_socket_ids:
                return False, f"포트 {port}의 소켓 식별자가 바뀌었습니다(PID 재사용 또는 재점유 가능성). 종료하지 않았습니다."
        found_owner = found_owner or pid in current_owners
    if not found_owner:
        return False, "대상 프로세스가 지정 포트의 현재 소유자가 아닙니다."
    return True, ""


def terminate_ports(
    ports: Sequence[int],
    force: bool = False,
    grace_seconds: float = 4.0,
    pre_signal_check: Optional[Callable[[int, ProcessInfo], Tuple[bool, str]]] = None,
) -> Tuple[bool, List[str]]:
    """포트 소유자를 재확인한 후 현재 사용자의 확정 개발 서버만 종료한다."""
    initial = list_listeners()
    initial_map = listeners_by_port(initial)
    expected_by_port: Dict[int, Set[int]] = {}
    expected_socket_ids_by_port: Dict[int, Dict[int, Set[str]]] = {}
    process_by_pid: Dict[int, ProcessInfo] = {}
    pid_ports: Dict[int, Set[int]] = {}
    messages: List[str] = []
    all_safe = True

    for port in sorted(set(ports)):
        owner_pids = initial_map.get(port, set())
        if not owner_pids:
            messages.append(f"포트 {port}: TCP LISTEN 없음")
            continue
        port_listeners = [item for item in initial if item.port == port]
        records: Dict[int, Optional[ProcessInfo]] = {}
        for listener in port_listeners:
            if listener.pid not in records:
                records[listener.pid] = inspect_process(listener)
        unsafe = [
            item.pid for item in port_listeners
            if not records.get(item.pid)
            or not records[item.pid].is_dev_server
            or records[item.pid].user != getpass.getuser()
        ]
        if unsafe:
            labels = ", ".join(f"PID {pid}" for pid in sorted(set(unsafe)))
            messages.append(f"포트 {port}: 개발 서버·현재 계정 소유로 확정되지 않아 보호했습니다 ({labels}).")
            all_safe = False
            continue
        expected_by_port[port] = set(owner_pids)
        expected_socket_ids_by_port[port] = {}
        for listener in port_listeners:
            expected_socket_ids_by_port[port].setdefault(listener.pid, set()).update(listener.socket_ids)
        for pid, info in records.items():
            if info:
                process_by_pid[pid] = info
                pid_ports.setdefault(pid, set()).add(port)

    gone_pids: Set[int] = set()
    for pid in sorted(process_by_pid):
        expected = process_by_pid[pid]
        target_ports = pid_ports[pid]
        ok, reason = _verified_before_signal(
            pid, expected, target_ports, expected_by_port, gone_pids, expected_socket_ids_by_port
        )
        if not ok:
            messages.append(f"PID {pid}: {reason}")
            all_safe = False
            continue
        if pre_signal_check:
            ok, reason = pre_signal_check(pid, expected)
            if not ok:
                messages.append(f"PID {pid}: 종료 직전 워크트리 재확인 실패 — {reason}")
                all_safe = False
                continue
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            messages.append(f"PID {pid}: 종료 직전에 이미 끝났습니다.")
            gone_pids.add(pid)
            continue
        except PermissionError:
            messages.append(f"PID {pid}: 정상 종료 신호를 보낼 권한이 없습니다.")
            all_safe = False
            continue
        if _wait_for_release(pid, target_ports, grace_seconds):
            messages.append(f"PID {pid}: SIGTERM 후 지정 포트 해제를 확인했습니다.")
            gone_pids.add(pid)
            remove_metadata_for_pid(pid, target_ports)
            continue
        if not force:
            messages.append(
                f"PID {pid}: SIGTERM 후에도 지정 포트를 유지합니다. 강제 종료는 하지 않았습니다."
            )
            all_safe = False
            continue
        ok, reason = _verified_before_signal(
            pid, expected, target_ports, expected_by_port, gone_pids, expected_socket_ids_by_port
        )
        if not ok:
            messages.append(f"PID {pid}: 강제 종료 전 재확인 실패 — {reason}")
            all_safe = False
            continue
        if pre_signal_check:
            ok, reason = pre_signal_check(pid, expected)
            if not ok:
                messages.append(f"PID {pid}: 강제 종료 직전 워크트리 재확인 실패 — {reason}")
                all_safe = False
                continue
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError) as exc:
            messages.append(f"PID {pid}: 강제 종료 신호를 보낼 수 없습니다 ({type(exc).__name__}).")
            all_safe = False
            continue
        if _wait_for_release(pid, target_ports, grace_seconds):
            messages.append(f"PID {pid}: SIGKILL 후 지정 포트 해제를 확인했습니다.")
            gone_pids.add(pid)
            remove_metadata_for_pid(pid, target_ports)
        else:
            messages.append(f"PID {pid}: SIGKILL 뒤에도 포트 해제를 확인하지 못했습니다.")
            all_safe = False
    return all_safe, messages


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def metadata_directory() -> Path:
    return codex_home() / "port-manager" / "servers"


def remove_metadata_for_pid(pid: int, ports: Iterable[int]) -> None:
    for port in ports:
        path = metadata_directory() / f"{port}.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("pid") == pid:
                path.unlink(missing_ok=True)
        except (OSError, ValueError, TypeError):
            continue


def find_package_root(cwd: Path, repo_root: Path) -> Optional[Path]:
    current = cwd.resolve()
    root = repo_root.resolve()
    try:
        current.relative_to(root)
    except ValueError:
        return None
    while True:
        if (current / "package.json").is_file():
            return current
        if current == root:
            break
        if root not in current.parents:
            break
        current = current.parent
    return None


def lockfile_managers(directory: Path) -> Set[str]:
    found: Set[str] = set()
    if (directory / "package-lock.json").exists() or (directory / "npm-shrinkwrap.json").exists():
        found.add("npm")
    if (directory / "pnpm-lock.yaml").exists():
        found.add("pnpm")
    if (directory / "yarn.lock").exists():
        found.add("yarn")
    if (directory / "bun.lock").exists() or (directory / "bun.lockb").exists():
        found.add("bun")
    return found


def resolve_package_manager(package: dict, package_root: Path, repo_root: Path) -> str:
    explicit = package.get("packageManager")
    if explicit:
        manager = str(explicit).split("@", 1)[0]
        if manager not in {"npm", "pnpm", "yarn", "bun"}:
            raise PortManagerError(f"package.json의 packageManager를 지원하지 않습니다: {manager}")
    else:
        manager = ""
    current = package_root.resolve()
    root = repo_root.resolve()
    nearest_lockfiles: Set[str] = set()
    while True:
        lockfiles = lockfile_managers(current)
        if lockfiles:
            nearest_lockfiles = lockfiles
            break
        if current == root or root not in current.parents:
            break
        current = current.parent
    if explicit:
        if nearest_lockfiles and manager not in nearest_lockfiles:
            raise PortManagerError("package.json의 packageManager와 가장 가까운 lockfile이 서로 다릅니다.")
        return manager
    if len(nearest_lockfiles) > 1:
        raise PortManagerError("같은 디렉터리에 여러 패키지 관리자 lockfile이 있어 실행 도구를 결정할 수 없습니다.")
    if len(nearest_lockfiles) == 1:
        return next(iter(nearest_lockfiles))
    return "npm"


def detect_framework(package: dict) -> str:
    dependencies = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package.get(key, {})
        if isinstance(value, dict):
            dependencies.update(value)
    if "react-scripts" in dependencies:
        return "react-scripts"
    for name in ("vite", "next", "nuxt", "astro", "@angular/cli", "parcel", "webpack-dev-server", "svelte-kit"):
        if name in dependencies:
            return {"@angular/cli": "angular", "webpack-dev-server": "webpack-dev-server", "svelte-kit": "svelte-kit"}.get(name, name)
    return "unknown"


def resolve_launch_plan(cwd: str) -> LaunchPlan:
    repo = identify_repo(cwd)
    if not repo:
        raise PortManagerError("현재 폴더가 Git 저장소 또는 워크트리 안이 아닙니다.")
    package_root = find_package_root(Path(cwd), Path(repo.root))
    if not package_root:
        raise PortManagerError("현재 저장소 경로에서 사용할 package.json을 찾지 못했습니다.")
    try:
        package = json.loads((package_root / "package.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PortManagerError("package.json을 읽거나 해석하지 못했습니다.") from exc
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict):
        raise PortManagerError("package.json의 scripts가 객체가 아닙니다.")
    framework = detect_framework(package)
    if "dev" in scripts:
        script_name = "dev"
    elif framework == "react-scripts" and "start" in scripts:
        script_name = "start"
    else:
        choices = ", ".join(str(name) for name in scripts.keys()) or "없음"
        raise PortManagerError(f"개발 서버 스크립트를 자동 선택할 수 없습니다. scripts: {choices}")
    manager = resolve_package_manager(package, package_root, Path(repo.root))
    binary = shutil.which(manager)
    if not binary:
        raise PortManagerError(f"package.json/lockfile에서 {manager}를 선택했지만 실행 파일을 찾지 못했습니다.")

    if framework == "react-scripts":
        args: List[str] = []
        use_port_environment = True
    elif framework == "vite" or framework == "svelte-kit":
        args = ["--port", "{port}", "--strictPort"]
        use_port_environment = True
    elif framework in {"next", "nuxt", "astro", "angular", "parcel", "webpack-dev-server"}:
        args = ["--port", "{port}"]
        use_port_environment = True
    else:
        args = ["--port", "{port}"]
        use_port_environment = True
    return LaunchPlan(
        repo=repo, package_root=package_root, package_manager=manager,
        manager_binary=binary, script_name=script_name, framework=framework,
        args=args, use_port_environment=use_port_environment,
    )


def launch_argv(plan: LaunchPlan, port: int) -> List[str]:
    env_binary = shutil.which("env") or "/usr/bin/env"
    command = [env_binary, f"PORT={port}", plan.manager_binary, "run", plan.script_name]
    args = [arg.format(port=port) for arg in plan.args]
    if plan.package_manager == "npm":
        if args:
            command.extend(["--", *args])
    elif plan.package_manager == "yarn":
        command.extend(args)
    else:
        if args:
            command.extend(["--", *args])
    return command


def process_group_id(pid: int) -> Optional[int]:
    try:
        return os.getpgid(pid)
    except (OSError, ProcessLookupError):
        return None


def stop_own_launch_group(process: subprocess.Popen, timeout: float = 2.0) -> None:
    """이번 실행이 만든 프로세스 그룹만 종료한다. 기존 포트 소유자는 신호하지 않는다."""
    pgid = process_group_id(process.pid)
    if pgid is None:
        return
    if pgid != process.pid:
        # 새 세션/그룹이 확인되지 않으면 광범위한 신호를 보내지 않는다.
        if process.poll() is not None:
            return
        try:
            process.terminate()
            process.wait(timeout=timeout)
        except (OSError, subprocess.TimeoutExpired):
            return
        return
    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        # 새 프로세스 그룹으로 분리한 이 실행만 대상으로 한다.
        if process_group_id(process.pid) == pgid:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            pass


def wait_for_launch(process: subprocess.Popen, port: int, repo_root: str, timeout: float = 20.0) -> Tuple[bool, str, List[Listener]]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False, "개발 서버 실행 명령이 포트를 열기 전에 종료됐습니다.", []
        listeners = list_listeners()
        port_listeners = [listener for listener in listeners if listener.port == port]
        group_matches = [listener for listener in port_listeners if process_group_id(listener.pid) == process.pid]
        foreign = [listener for listener in port_listeners if process_group_id(listener.pid) != process.pid]
        if foreign:
            return False, "시작 도중 다른 프로세스가 요청 포트를 점유했습니다. 그 프로세스는 건드리지 않았습니다.", []
        if group_matches:
            return True, "요청 포트를 이번 실행이 실제로 점유했습니다.", group_matches
        # 자동 포트 변경 감지: 새 프로세스 그룹이 다른 포트를 열면 성공으로 간주하지 않는다.
        group_ports = [listener for listener in listeners if process_group_id(listener.pid) == process.pid]
        alternate = sorted({listener.port for listener in group_ports if listener.port != port})
        if alternate:
            return False, f"개발 서버가 다른 포트({', '.join(map(str, alternate))})로 시작됐습니다. 요청 포트를 고정하지 못했습니다.", []
        time.sleep(0.25)
    return False, "제한 시간 안에 요청 포트의 LISTEN 소켓을 확인하지 못했습니다.", []


def write_metadata(port: int, listener: Listener, plan: LaunchPlan) -> None:
    directory = metadata_directory()
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        directory.chmod(0o700)
    except OSError:
        pass
    data = {
        "port": port,
        "pid": listener.pid,
        "repo_root": plan.repo.root,
        "package_manager": plan.package_manager,
        "script": plan.script_name,
        "framework": plan.framework,
        "started_at": datetime.now().astimezone().isoformat(timespec="microseconds"),
    }
    path = directory / f"{port}.json"
    temporary = directory / f".{port}.{os.getpid()}.tmp"
    temporary.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    try:
        temporary.chmod(0o600)
    except OSError:
        pass
    os.replace(temporary, path)


def replace_port(port: int, force: bool = False, grace_seconds: float = 4.0) -> bool:
    try:
        plan = resolve_launch_plan(os.getcwd())
    except PortManagerError as exc:
        print(f"교체 실패: {exc}")
        return False
    print(
        f"대상: {plan.repo.name} [{plan.repo.branch}] · {plan.repo.root}\n"
        f"실행 계획: {plan.package_manager} {plan.script_name} ({plan.framework}) · 포트 {port}"
    )
    existing = [listener for listener in list_listeners() if listener.port == port]
    if existing:
        print("기존 포트 소유자를 검증하고 정상 종료를 요청합니다.")
        stopped, messages = terminate_ports([port], force=force, grace_seconds=grace_seconds)
        for message in messages:
            print(message)
        if not stopped:
            print("교체 실패: 기존 서버가 안전하게 종료되지 않아 새 서버를 시작하지 않았습니다.")
            return False
    if any(listener.port == port for listener in list_listeners()):
        print(f"교체 실패: 요청 포트 {port}가 아직 사용 중입니다. 포트 소유자를 건드리지 않았습니다.")
        return False

    command = launch_argv(plan, port)
    try:
        process = subprocess.Popen(
            command,
            cwd=str(plan.package_root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
        )
    except OSError as exc:
        print(f"교체 실패: 패키지 스크립트를 시작하지 못했습니다 ({type(exc).__name__}).")
        return False
    ok, message, owners = wait_for_launch(process, port, plan.repo.root)
    if not ok:
        print(f"교체 실패: {message}")
        stop_own_launch_group(process)
        return False
    try:
        write_metadata(port, owners[0], plan)
    except OSError:
        print("경고: 서버는 요청 포트에서 시작했지만 관리 메타데이터를 저장하지 못했습니다.")
    print(f"교체 완료: 포트 {port}를 PID {owners[0].pid}가 점유 중입니다.")
    print(f"프로젝트/워크트리: {plan.repo.name} [{plan.repo.branch}] · {plan.repo.root}")
    print("서버 stdout/stderr는 저장하거나 출력하지 않습니다.")
    return True


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="port_manager.py",
        description="로컬 개발 서버 포트를 조회하고, 지정한 개발 서버만 안전하게 종료·교체합니다.",
    )
    commands = result.add_subparsers(dest="action", required=True)
    commands.add_parser("all", help="개발 서버와 전체 TCP LISTEN을 분리해 표시")
    detail = commands.add_parser("detail", help="포트 하나의 리스너 상세 정보")
    detail.add_argument("port", type=port_is_valid)
    repo = commands.add_parser("repo", help="저장소 이름이 정확히 일치하는 모든 워크트리 조회")
    repo.add_argument("repo_name", help="Git 저장소 이름(정확 일치)")
    delete = commands.add_parser("delete", help="포트의 개발 서버를 종료하고, 옵션으로 연결 워크트리를 제거")
    delete.add_argument("ports", nargs="+", type=port_is_valid)
    delete.add_argument("--force", action="store_true", help="정상 종료 후에도 남은 대상 서버에 SIGKILL")
    delete.add_argument("--grace-seconds", type=float, default=4.0, help="SIGTERM 후 확인할 시간(기본 4초)")
    delete.add_argument(
        "--remove-worktree", action="store_true",
        help="명시 포트 종료 후 안전 조건을 통과한 연결 Git linked worktree도 제거",
    )
    replace = commands.add_parser("replace", help="현재 저장소의 개발 서버를 포트에 다시 실행")
    replace.add_argument("port", type=port_is_valid)
    replace.add_argument("--force", action="store_true", help="기존 개발 서버가 SIGTERM에 응답하지 않을 때만 강제 종료")
    replace.add_argument("--grace-seconds", type=float, default=4.0, help="기존 서버 SIGTERM 후 확인할 시간(기본 4초)")
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.action == "all":
            print_all()
            return 0
        if args.action == "detail":
            print_detail(args.port)
            return 0
        if args.action == "repo":
            print_repo(args.repo_name)
            return 0
        if args.action == "delete":
            if args.grace_seconds < 0:
                print("실패: grace-seconds는 0 이상이어야 합니다.")
                return 2
            if args.remove_worktree:
                ok, messages = delete_ports_and_worktrees(
                    args.ports, force=args.force, grace_seconds=args.grace_seconds
                )
            else:
                ok, messages = terminate_ports(args.ports, force=args.force, grace_seconds=args.grace_seconds)
            for message in messages:
                print(message)
            return 0 if ok else 1
        if args.action == "replace":
            if args.grace_seconds < 0:
                print("교체 실패: grace-seconds는 0 이상이어야 합니다.")
                return 2
            return 0 if replace_port(args.port, force=args.force, grace_seconds=args.grace_seconds) else 1
    except PortManagerError as exc:
        print(f"실패: {exc}")
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
