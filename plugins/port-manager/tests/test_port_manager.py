"""임시 데이터와 더미 리스너만 사용하는 회귀 테스트."""

from __future__ import annotations

import importlib.util
import json
import os
import getpass
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).parents[1] / "skills" / "port-manager" / "scripts" / "port_manager.py"
SPEC = importlib.util.spec_from_file_location("port_manager", SCRIPT)
pm = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pm
SPEC.loader.exec_module(pm)


def make_info(pid: int, repo_root: str, repo_name: str, branch: str) -> pm.ProcessInfo:
    return pm.ProcessInfo(
        pid=pid, ppid=1, user="tester", started="Wed Oct 22 09:00:00 2026",
        elapsed="00:20", cpu_time="00:00.02", cpu_percent="0.0", rss_kb=1024,
        comm="node", command="node vite --port 5173", cwd=repo_root,
        repo=pm.RepoInfo(root=repo_root, name=repo_name, branch=branch),
        classification="개발 서버", is_dev_server=True, reason="fixture",
    )


class ListenerParsingTests(unittest.TestCase):
    def test_merges_ipv4_and_ipv6_rows_for_same_pid_and_port(self) -> None:
        output = """COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
node 431 tester 12u IPv4 0x1 0t0 TCP *:5173 (LISTEN)
node 431 tester 14u IPv6 0x2 0t0 TCP *:5173 (LISTEN)
postgres 900 tester 9u IPv6 0x3 0t0 TCP [::1]:5432 (LISTEN)
"""
        listeners = pm.parse_lsof_listeners(output)
        self.assertEqual({(item.pid, item.port) for item in listeners}, {(900, 5432), (431, 5173)})
        vite = next(item for item in listeners if item.port == 5173)
        self.assertEqual(len(vite.endpoints), 2)
        self.assertEqual(vite.endpoints, {"IPv4 *", "IPv6 *"})
        self.assertEqual(vite.socket_ids, {"0x1", "0x2"})

    def test_same_port_on_distinct_pids_remains_distinct(self) -> None:
        output = """node 431 tester 12u IPv4 0x1 0t0 TCP 127.0.0.1:4173 (LISTEN)
node 432 tester 13u IPv6 0x2 0t0 TCP [::1]:4173 (LISTEN)
"""
        listeners = pm.parse_lsof_listeners(output)
        self.assertEqual({item.pid for item in listeners}, {431, 432})


class ClassificationTests(unittest.TestCase):
    def test_database_is_not_a_development_server(self) -> None:
        label, is_dev, _ = pm.classify_process("/opt/postgres/bin/postgres", "postgres -D data", [], True)
        self.assertEqual(label, "DB/서비스 프로세스")
        self.assertFalse(is_dev)

    def test_repository_dev_script_is_classified(self) -> None:
        label, is_dev, _ = pm.classify_process(
            "python3", "python3 /tmp/dev-server.py --port 41231", ["npm run dev"], True
        )
        self.assertEqual(label, "개발 서버")
        self.assertTrue(is_dev)

    def test_unmarked_node_server_in_repo_is_only_a_candidate(self) -> None:
        label, is_dev, _ = pm.classify_process("node", "node index.js", [], True)
        self.assertEqual(label, "개발 서버 후보")
        self.assertFalse(is_dev)

    def test_idle_is_never_inferred_from_process_metrics(self) -> None:
        self.assertTrue(pm.idle_label().startswith("알 수 없음"))

    def test_command_summary_does_not_emit_secret_arguments_or_inline_code(self) -> None:
        summary = pm.safe_command_summary(
            "node",
            "node /repo/node_modules/.bin/vite dev --port 5173 --api-token=not-for-output -e 'secret code'",
        )
        self.assertIn("vite", summary)
        self.assertIn("5173", summary)
        self.assertNotIn("not-for-output", summary)
        self.assertNotIn("secret code", summary)


class RepositoryAndPlanTests(unittest.TestCase):
    def test_repo_filter_is_exact_and_paths_disambiguate_same_name(self) -> None:
        first = make_info(101, "/tmp/one/frontend", "frontend", "main")
        worktree = make_info(102, "/tmp/one/frontend-feature", "frontend", "feature")
        similar = make_info(103, "/tmp/one/frontend-ui", "frontend-ui", "main")
        rows = [(pm.Listener(5173, 101, "tester", "node"), first),
                (pm.Listener(5174, 102, "tester", "node"), worktree),
                (pm.Listener(5175, 103, "tester", "node"), similar)]
        exact = [(listener, info) for listener, info in rows if pm.repo_matches(info, "frontend")]
        self.assertEqual([item[1].repo.root for item in exact], ["/tmp/one/frontend", "/tmp/one/frontend-feature"])
        self.assertFalse(pm.repo_matches(similar, "front"))
        self.assertNotEqual(pm.project_label(exact[0][1]), pm.project_label(exact[1][1]))

    def test_independent_repositories_with_same_name_keep_full_paths(self) -> None:
        first = make_info(201, "/tmp/first/frontend", "frontend", "main")
        second = make_info(202, "/tmp/second/frontend", "frontend", "main")
        self.assertTrue(pm.repo_matches(first, "frontend"))
        self.assertTrue(pm.repo_matches(second, "frontend"))
        self.assertNotEqual(pm.project_label(first), pm.project_label(second))
        self.assertIn("/tmp/first/frontend", pm.project_label(first))
        self.assertIn("/tmp/second/frontend", pm.project_label(second))

    def test_conflicting_lockfiles_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package-lock.json").write_text("{}", encoding="utf-8")
            (root / "pnpm-lock.yaml").write_text("lockfileVersion: '9'\n", encoding="utf-8")
            with self.assertRaises(pm.PortManagerError):
                pm.resolve_package_manager({}, root, root)

    def test_framework_uses_fixed_vite_port(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text(json.dumps({"dependencies": {"vite": "5"}}), encoding="utf-8")
            plan = pm.LaunchPlan(
                repo=pm.RepoInfo(str(root), root.name, "main"), package_root=root,
                package_manager="npm", manager_binary="/usr/bin/npm", script_name="dev",
                framework="vite", args=["--port", "{port}", "--strictPort"], use_port_environment=True,
            )
            argv = pm.launch_argv(plan, 4173)
            self.assertEqual(argv[-3:], ["--port", "4173", "--strictPort"])
            self.assertIn("PORT=4173", argv)


class OwnershipRaceTests(unittest.TestCase):
    def test_port_reoccupation_aborts_before_signaling(self) -> None:
        original = make_info(431, "/tmp/project", "project", "main")
        original.user = getpass.getuser()
        changed = pm.Listener(port=5173, pid=432, user="tester", command="node", endpoints={"127.0.0.1"})
        with mock.patch.object(pm, "_process_info_for_pid", return_value=original), \
             mock.patch.object(pm, "list_listeners", return_value=[changed]):
            ok, reason = pm._verified_before_signal(431, original, {5173}, {5173: {431}}, set())
        self.assertFalse(ok)
        self.assertIn("소유자가", reason)

    def test_startup_fails_if_another_process_claims_requested_port(self) -> None:
        fake_process = mock.Mock()
        fake_process.pid = 50000
        fake_process.poll.return_value = None
        outsider = pm.Listener(port=4173, pid=60000, user="tester", command="unknown", endpoints={"*"})
        with mock.patch.object(pm, "process_group_id", side_effect=lambda pid: 50000 if pid == 50000 else 60000), \
             mock.patch.object(pm, "list_listeners", return_value=[outsider]):
            ok, reason, _ = pm.wait_for_launch(fake_process, 4173, "/tmp/project", timeout=0.1)
        self.assertFalse(ok)
        self.assertIn("다른 프로세스", reason)

    def test_startup_fails_if_new_server_falls_back_to_next_port(self) -> None:
        fake_process = mock.Mock()
        fake_process.pid = 50000
        fake_process.poll.return_value = None
        alternate = pm.Listener(port=4174, pid=50001, user="tester", command="node", endpoints={"127.0.0.1"})
        with mock.patch.object(pm, "process_group_id", side_effect=lambda pid: 50000 if pid in {50000, 50001} else None), \
             mock.patch.object(pm, "list_listeners", return_value=[alternate]):
            ok, reason, _ = pm.wait_for_launch(fake_process, 4173, "/tmp/project", timeout=0.1)
        self.assertFalse(ok)
        self.assertIn("다른 포트(4174)", reason)

    def test_pid_reuse_with_a_new_socket_identity_aborts(self) -> None:
        original = make_info(431, "/tmp/project", "project", "main")
        original.user = getpass.getuser()
        rebound_socket = pm.Listener(
            port=5173, pid=431, user=getpass.getuser(), command="node",
            endpoints={"IPv4 127.0.0.1"}, socket_ids={"0xnew"},
        )
        with mock.patch.object(pm, "_process_info_for_pid", return_value=original), \
             mock.patch.object(pm, "list_listeners", return_value=[rebound_socket]):
            ok, reason = pm._verified_before_signal(
                431, original, {5173}, {5173: {431}}, set(), {5173: {431: {"0xold"}}}
            )
        self.assertFalse(ok)
        self.assertIn("PID 재사용", reason)

    def test_worktree_registration_guard_runs_before_any_signal(self) -> None:
        listener = pm.Listener(5173, 431, getpass.getuser(), "python3", {"IPv4 127.0.0.1"}, {"0x1"})
        info = make_info(431, "/tmp/project-feature", "project", "feature")
        info.user = getpass.getuser()
        with mock.patch.object(pm, "list_listeners", return_value=[listener]), \
             mock.patch.object(pm, "inspect_process", return_value=info), \
             mock.patch.object(pm, "_verified_before_signal", return_value=(True, "")), \
             mock.patch.object(pm.os, "kill") as kill:
            ok, messages = pm.terminate_ports(
                [5173], pre_signal_check=lambda _pid, _info: (False, "워크트리 등록 변경")
            )
        self.assertFalse(ok)
        self.assertTrue(any("워크트리 등록 변경" in message for message in messages))
        kill.assert_not_called()


def free_test_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def run_cli(action: str, *args: str, cwd: Optional[Path] = None, codex_home: Optional[Path] = None) -> subprocess.CompletedProcess:
    environment = None
    if codex_home:
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(codex_home)
    return subprocess.run(
        [sys.executable, str(SCRIPT), action, *args], cwd=str(cwd) if cwd else None,
        env=environment, capture_output=True, text=True, timeout=35,
    )


@unittest.skipUnless(sys.platform == "darwin" and shutil.which("lsof") and shutil.which("npm"), "macOS, lsof, npm 필요")
class MacIntegrationTests(unittest.TestCase):
    """테스트가 만든 저장소와 리스너에만 CLI의 실제 종료·교체를 수행한다."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="port-manager-test-")
        self.root = Path(self.temp.name)
        self.codex_home = self.root / "codex-home"
        self.expected_ports = set()
        self.created_processes = {}
        self.repo_parent = self.root / "one"
        self.repo = self.repo_parent / "frontend"
        self.repo.mkdir(parents=True)
        (self.repo / "package.json").write_text(json.dumps({
            "name": "port-manager-fixture",
            "packageManager": "npm@10.0.0",
            "scripts": {"dev": "python3 dev-server.py"},
            "devDependencies": {"vite": "5.0.0"},
        }), encoding="utf-8")
        (self.repo / "package-lock.json").write_text("{}", encoding="utf-8")
        (self.repo / "dev-server.py").write_text(
            "import argparse, http.server, signal\n"
            "p=argparse.ArgumentParser()\n"
            "p.add_argument('--port', type=int, required=True)\n"
            "p.add_argument('--strictPort', action='store_true')\n"
            "p.add_argument('--ignore-term', action='store_true')\n"
            "p.add_argument('--write-on-term', action='store_true')\n"
            "a=p.parse_args()\n"
            "if a.ignore_term: signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "if a.write_on_term:\n"
            " def stop(*_args):\n"
            "  open('term-marker', 'w').write('fixture')\n"
            "  raise SystemExit(0)\n"
            " signal.signal(signal.SIGTERM, stop)\n"
            "http.server.ThreadingHTTPServer(('127.0.0.1', a.port), http.server.SimpleHTTPRequestHandler).serve_forever()\n",
            encoding="utf-8",
        )
        self.run_git("init", "-b", "main", str(self.repo))
        self.run_git("-C", str(self.repo), "config", "user.name", "Port Manager Test")
        self.run_git("-C", str(self.repo), "config", "user.email", "port-manager-test@example.invalid")
        self.run_git("-C", str(self.repo), "add", ".")
        self.run_git("-C", str(self.repo), "commit", "-m", "test fixture")
        self.worktree = self.repo_parent / "frontend-feature"
        self.run_git("-C", str(self.repo), "worktree", "add", "-b", "feature", str(self.worktree))

    def tearDown(self) -> None:
        # 기록해 둔 더미 PID·시작 시각·테스트 포트가 모두 맞을 때만 정리한다.
        for pid, (port, started) in list(self.created_processes.items()):
            listener_exists = any(item.pid == pid and item.port == port for item in pm.list_listeners())
            stats = pm.read_ps_stats(pid)
            if not listener_exists or not stats or stats["started"] != started:
                continue
            try:
                os.kill(pid, 15)
            except ProcessLookupError:
                continue
            deadline = time.monotonic() + 1.0
            while time.monotonic() < deadline:
                if not any(item.pid == pid and item.port == port for item in pm.list_listeners()):
                    break
                time.sleep(0.05)
            current = pm.read_ps_stats(pid)
            if current and current["started"] == started and any(
                item.pid == pid and item.port == port for item in pm.list_listeners()
            ):
                os.kill(pid, 9)
        self.temp.cleanup()

    def run_git(self, *args: str) -> None:
        result = subprocess.run(["git", *args], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

    def new_port(self) -> int:
        port = free_test_port()
        self.assertFalse([item for item in pm.list_listeners() if item.port == port])
        self.expected_ports.add(port)
        return port

    def remember_listener(self, port: int) -> pm.Listener:
        listener = next(item for item in pm.list_listeners() if item.port == port)
        stats = pm.read_ps_stats(listener.pid)
        self.assertIsNotNone(stats)
        self.created_processes[listener.pid] = (port, stats["started"])
        return listener

    def test_worktree_mapping_replace_multiport_delete_and_exact_repo(self) -> None:
        first_port = self.new_port()
        second_port = self.new_port()
        first = run_cli("replace", str(first_port), cwd=self.repo, codex_home=self.codex_home)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertIn(f"포트 {first_port}", first.stdout)
        first_listener = self.remember_listener(first_port)
        first_metadata = json.loads((self.codex_home / "port-manager" / "servers" / f"{first_port}.json").read_text())

        replaced = run_cli("replace", str(first_port), cwd=self.repo, codex_home=self.codex_home)
        self.assertEqual(replaced.returncode, 0, replaced.stdout + replaced.stderr)
        new_first_listener = self.remember_listener(first_port)
        metadata = json.loads((self.codex_home / "port-manager" / "servers" / f"{first_port}.json").read_text())
        self.assertTrue(
            new_first_listener.pid != first_listener.pid
            or metadata["started_at"] != first_metadata["started_at"]
        )
        self.assertEqual(metadata["port"], first_port)
        self.assertEqual(metadata["repo_root"], str(self.repo.resolve()))
        self.assertEqual(set(metadata), {"port", "pid", "repo_root", "package_manager", "script", "framework", "started_at"})

        second = run_cli("replace", str(second_port), cwd=self.worktree, codex_home=self.codex_home)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.remember_listener(second_port)
        detail = run_cli("detail", str(second_port), cwd=self.worktree, codex_home=self.codex_home)
        self.assertEqual(detail.returncode, 0, detail.stdout + detail.stderr)
        self.assertIn("feature", detail.stdout)
        self.assertIn(str(self.worktree.resolve()), detail.stdout)

        repo = run_cli("repo", "frontend", cwd=self.repo, codex_home=self.codex_home)
        self.assertIn(str(self.repo.resolve()), repo.stdout)
        self.assertIn(str(self.worktree.resolve()), repo.stdout)
        exact = run_cli("repo", "front", cwd=self.repo, codex_home=self.codex_home)
        self.assertNotIn(str(self.repo.resolve()), exact.stdout)
        self.assertNotIn(str(self.worktree.resolve()), exact.stdout)

        all_output = run_cli("all", cwd=self.repo, codex_home=self.codex_home)
        self.assertIn(str(first_port), all_output.stdout)
        self.assertIn(str(second_port), all_output.stdout)
        self.assertIn("알 수 없음", all_output.stdout)

        before_delete = {item.pid for port in (first_port, second_port) for item in pm.list_listeners() if item.port == port}
        deleted = run_cli("delete", str(first_port), str(second_port), cwd=self.repo, codex_home=self.codex_home)
        self.assertEqual(deleted.returncode, 0, deleted.stdout + deleted.stderr)
        self.assertTrue(any("SIGTERM" in line for line in deleted.stdout.splitlines()))
        self.assertFalse([item for item in pm.list_listeners() if item.port in {first_port, second_port}])
        self.assertTrue(before_delete)
        self.assertTrue(self.worktree.exists(), "일반 delete는 워크트리를 제거하지 않아야 합니다")

    def test_explicit_delete_removes_clean_linked_worktree_and_preserves_branch(self) -> None:
        port = self.new_port()
        started = run_cli("replace", str(port), cwd=self.worktree, codex_home=self.codex_home)
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        self.remember_listener(port)
        branch_before = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-parse", "refs/heads/feature^{commit}"], text=True
        ).strip()

        removed = run_cli(
            "delete", str(port), "--remove-worktree", cwd=self.repo, codex_home=self.codex_home
        )
        self.assertEqual(removed.returncode, 0, removed.stdout + removed.stderr)
        self.assertFalse(self.worktree.exists(), removed.stdout + removed.stderr)
        branch_after = subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-parse", "refs/heads/feature^{commit}"], text=True
        ).strip()
        self.assertEqual(branch_after, branch_before)
        self.assertFalse([item for item in pm.list_listeners() if item.port == port])

    def test_main_worktree_is_never_removed_or_signaled(self) -> None:
        port = self.new_port()
        started = run_cli("replace", str(port), cwd=self.repo, codex_home=self.codex_home)
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        listener = self.remember_listener(port)

        result = run_cli("delete", str(port), "--remove-worktree", cwd=self.repo, codex_home=self.codex_home)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("기본 워크트리", result.stdout)
        self.assertTrue(self.repo.exists())
        self.assertIn(listener.pid, {item.pid for item in pm.list_listeners() if item.port == port})

    def test_current_execution_worktree_is_never_removed_or_signaled(self) -> None:
        port = self.new_port()
        started = run_cli("replace", str(port), cwd=self.worktree, codex_home=self.codex_home)
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        listener = self.remember_listener(port)

        result = run_cli(
            "delete", str(port), "--remove-worktree", cwd=self.worktree, codex_home=self.codex_home
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("현재 Codex 실행 디렉터리", result.stdout)
        self.assertTrue(self.worktree.exists())
        self.assertIn(listener.pid, {item.pid for item in pm.list_listeners() if item.port == port})

    def test_detached_head_worktree_is_never_removed_or_signaled(self) -> None:
        self.run_git("-C", str(self.worktree), "checkout", "--detach")
        port = self.new_port()
        started = run_cli("replace", str(port), cwd=self.worktree, codex_home=self.codex_home)
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        listener = self.remember_listener(port)

        result = run_cli(
            "delete", str(port), "--remove-worktree", cwd=self.repo, codex_home=self.codex_home
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("브랜치가 연결되지 않은", result.stdout)
        self.assertTrue(self.worktree.exists())
        self.assertIn(listener.pid, {item.pid for item in pm.list_listeners() if item.port == port})

    def test_locked_dirty_untracked_and_ignored_worktrees_are_preserved(self) -> None:
        cases = ("locked", "tracked", "untracked", "ignored")
        for case in cases:
            with self.subTest(case=case):
                # 각 하위 사례는 같은 fixture 워크트리를 재사용하므로 잠금만 마지막에 수행한다.
                port = self.new_port()
                started = run_cli("replace", str(port), cwd=self.worktree, codex_home=self.codex_home)
                self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
                listener = self.remember_listener(port)
                if case == "locked":
                    self.run_git("-C", str(self.repo), "worktree", "lock", str(self.worktree))
                elif case == "tracked":
                    with (self.worktree / "dev-server.py").open("a", encoding="utf-8") as stream:
                        stream.write("# dirty fixture\n")
                elif case == "untracked":
                    (self.worktree / "untracked-fixture").write_text("keep", encoding="utf-8")
                else:
                    exclude = subprocess.check_output(
                        ["git", "-C", str(self.worktree), "rev-parse", "--git-path", "info/exclude"],
                        text=True,
                    ).strip()
                    exclude_path = Path(exclude)
                    if not exclude_path.is_absolute():
                        exclude_path = self.worktree / exclude_path
                    with exclude_path.open("a", encoding="utf-8") as stream:
                        stream.write("\n/ignored-fixture\n")
                    (self.worktree / "ignored-fixture").write_text("keep", encoding="utf-8")

                result = run_cli(
                    "delete", str(port), "--remove-worktree", cwd=self.repo, codex_home=self.codex_home
                )
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(self.worktree.exists())
                self.assertIn(listener.pid, {item.pid for item in pm.list_listeners() if item.port == port})
                # dirty/ignored fixture 상태와 실행 PID는 다음 하위 사례를 위해 원상 복구한다.
                if case == "tracked":
                    self.run_git("-C", str(self.worktree), "checkout", "--", "dev-server.py")
                elif case == "untracked":
                    (self.worktree / "untracked-fixture").unlink()
                elif case == "ignored":
                    (self.worktree / "ignored-fixture").unlink()
                elif case == "locked":
                    self.run_git("-C", str(self.repo), "worktree", "unlock", str(self.worktree))
                stopped = run_cli("delete", str(port), cwd=self.repo, codex_home=self.codex_home)
                self.assertEqual(stopped.returncode, 0, stopped.stdout + stopped.stderr)

    def test_another_server_in_same_worktree_blocks_removal_before_signals(self) -> None:
        first_port, second_port = self.new_port(), self.new_port()
        for port in (first_port, second_port):
            started = run_cli("replace", str(port), cwd=self.worktree, codex_home=self.codex_home)
            self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
            self.remember_listener(port)
        before = {item_port: {item.pid for item in pm.list_listeners() if item.port == item_port}
                  for item_port in (first_port, second_port)}

        result = run_cli(
            "delete", str(first_port), "--remove-worktree", cwd=self.repo, codex_home=self.codex_home
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("선택하지 않은", result.stdout)
        self.assertTrue(self.worktree.exists())
        for port in (first_port, second_port):
            self.assertEqual({item.pid for item in pm.list_listeners() if item.port == port}, before[port])

    def test_explicit_multiport_delete_removes_one_linked_worktree(self) -> None:
        ports = (self.new_port(), self.new_port())
        for port in ports:
            started = run_cli("replace", str(port), cwd=self.worktree, codex_home=self.codex_home)
            self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
            self.remember_listener(port)
        result = run_cli(
            "delete", *(str(port) for port in ports), "--remove-worktree",
            cwd=self.repo, codex_home=self.codex_home,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.worktree.exists())

    def test_sigterm_timeout_keeps_worktree_and_does_not_force_kill(self) -> None:
        package_path = self.worktree / "package.json"
        package = json.loads(package_path.read_text(encoding="utf-8"))
        package["scripts"]["dev"] = "python3 dev-server.py --ignore-term"
        package_path.write_text(json.dumps(package), encoding="utf-8")
        # 이 변경 자체가 dirty이므로 먼저 임시 브랜치 커밋에 포함해 안전 조건을 통과시킨다.
        self.run_git("-C", str(self.worktree), "add", "package.json")
        self.run_git("-C", str(self.worktree), "commit", "-m", "fixture ignores SIGTERM")
        port = self.new_port()
        started = run_cli("replace", str(port), cwd=self.worktree, codex_home=self.codex_home)
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        listener = self.remember_listener(port)

        result = run_cli(
            "delete", str(port), "--remove-worktree", "--grace-seconds", "0.2",
            cwd=self.repo, codex_home=self.codex_home,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SIGTERM", result.stdout)
        self.assertTrue(self.worktree.exists())
        self.assertIn(listener.pid, {item.pid for item in pm.list_listeners() if item.port == port})

    def test_server_exit_that_dirties_worktree_is_reported_as_partial_failure(self) -> None:
        package_path = self.worktree / "package.json"
        package = json.loads(package_path.read_text(encoding="utf-8"))
        package["scripts"]["dev"] = "python3 dev-server.py --write-on-term"
        package_path.write_text(json.dumps(package), encoding="utf-8")
        self.run_git("-C", str(self.worktree), "add", "package.json")
        self.run_git("-C", str(self.worktree), "commit", "-m", "fixture writes on shutdown")
        port = self.new_port()
        started = run_cli("replace", str(port), cwd=self.worktree, codex_home=self.codex_home)
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        self.remember_listener(port)

        result = run_cli(
            "delete", str(port), "--remove-worktree", cwd=self.repo, codex_home=self.codex_home
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("서버는 종료됐고 워크트리는 유지했습니다", result.stdout)
        self.assertTrue(self.worktree.exists())
        self.assertTrue((self.worktree / "term-marker").exists())
        self.assertFalse([item for item in pm.list_listeners() if item.port == port])

    def test_replace_refuses_unclassified_existing_listener(self) -> None:
        port = self.new_port()
        fake_script = self.root / "postgres-mock.py"
        fake_script.write_text(
            "import http.server, sys\n"
            "http.server.ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1])), http.server.SimpleHTTPRequestHandler).serve_forever()\n",
            encoding="utf-8",
        )
        fake = subprocess.Popen([sys.executable, str(fake_script), str(port)], cwd=str(self.root), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and not [item for item in pm.list_listeners() if item.port == port]:
                time.sleep(0.05)
            self.assertTrue([item for item in pm.list_listeners() if item.port == port])
            result = run_cli("replace", str(port), cwd=self.repo, codex_home=self.codex_home)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("종료", result.stdout)
            self.assertIsNone(fake.poll())
        finally:
            fake.terminate()
            try:
                fake.wait(timeout=3)
            except subprocess.TimeoutExpired:
                fake.kill()
                fake.wait(timeout=3)

    def test_normal_delete_does_not_escalate_but_explicit_force_does(self) -> None:
        package_path = self.repo / "package.json"
        package = json.loads(package_path.read_text(encoding="utf-8"))
        package["scripts"]["dev"] = "python3 dev-server.py --ignore-term"
        package_path.write_text(json.dumps(package), encoding="utf-8")
        port = self.new_port()
        started = run_cli("replace", str(port), cwd=self.repo, codex_home=self.codex_home)
        self.assertEqual(started.returncode, 0, started.stdout + started.stderr)
        listener = self.remember_listener(port)
        held_pid = listener.pid

        graceful = run_cli(
            "delete", str(port), "--grace-seconds", "0.2", cwd=self.repo, codex_home=self.codex_home
        )
        self.assertNotEqual(graceful.returncode, 0)
        self.assertIn("강제 종료는 하지 않았습니다", graceful.stdout)
        self.assertIn(held_pid, {item.pid for item in pm.list_listeners() if item.port == port})

        forced = run_cli(
            "delete", str(port), "--force", "--grace-seconds", "0.2", cwd=self.repo, codex_home=self.codex_home
        )
        self.assertEqual(forced.returncode, 0, forced.stdout + forced.stderr)
        self.assertIn("SIGKILL", forced.stdout)
        self.assertFalse([item for item in pm.list_listeners() if item.port == port])


if __name__ == "__main__":
    unittest.main(verbosity=2)
