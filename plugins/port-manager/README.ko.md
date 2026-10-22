# Port Manager

[영문](README.md) | [한국어](README.ko.md)

| | |
|---|---|
| **이름** | port-manager |
| **설명** | 로컬 개발 서버의 TCP 포트와 linked worktree를 안전하게 조회·관리하는 Skill |
| **버전** | 1.1.0 |
| **트리거** | `/port-manger:all`, `/port-manger:detail`, `/port-manger:repo`, `/port-manger:delete`, `/port-manger:replace`, `/port-manger:delete:worktree`, `$port-manager` |

---

로컬 TCP 리스너를 조회하고 프로젝트·Git 워크트리 기준으로 개발 서버를 식별합니다. 사용자가 명시한 포트의 확인된 개발 서버만 정상 종료하거나 교체합니다. 명시적으로 요청하면 안전 검사를 거쳐 연결된 clean Git linked worktree도 제거할 수 있습니다. macOS 우선이며 반복 실행 가능한 CLI 헬퍼와 회귀 테스트를 포함합니다.

## 안전 기준

- `all`, `detail`, `repo`는 읽기 전용입니다. 확인된 개발 서버와 나머지 TCP 리스너를 구분하며 DB·시스템 서비스·분류가 불확실한 프로세스를 개발 서버라고 단정하지 않습니다.
- OS 리스너 정보만으로 유휴 상태를 알 수 없으면 `알 수 없음`으로 표시합니다. CPU 사용량 0이나 연결 없음만으로 유휴라고 결론 내리지 않습니다.
- `delete`, `replace`는 신호를 보내기 전에 PID, 시작 시각, 계정, 작업 경로, 소켓 식별자와 현재 포트 소유자를 다시 확인합니다. 기본은 정상 종료이며 `--force`는 명시적으로 요청한 경우에만 사용합니다.
- 기본 `delete`와 `replace`는 워크트리를 제거하지 않습니다. `delete PORT... --remove-worktree`로 명시해야 제거를 시도합니다. main·현재·잠금·분리 HEAD·수정·미추적·무시 파일·소속이 모호한 워크트리는 거부합니다. 같은 워크트리의 다른 리스너도 제거를 막습니다. 신호 전과 일반 `git worktree remove` 직전에 프로세스와 Git 등록을 재확인하며, 브랜치를 보존합니다. Git에는 `--force`를 전달하지 않습니다.
- `replace`는 현재 프로젝트의 package manifest와 lockfile을 읽어 개발 스크립트를 시작한 뒤 요청한 포트를 실제로 점유했는지 검증합니다. 다음 포트로 자동 이동하지 않습니다. 다른 프로세스가 포트를 점유하면 그 프로세스를 건드리지 않고 실패합니다.
- 프로세스 환경 변수는 읽지 않습니다. 새 서버의 stdout/stderr는 버리고 `CODEX_HOME/port-manager/servers` 또는 `CODEX_HOME`이 없을 때 `~/.codex/port-manager/servers`에 최소 메타데이터만 저장합니다.

## 요청 커맨드

사용자-facing 기본 별칭 철자는 `port-manger`이며, 설치 가능한 패키지와 Skill의 정식 이름은 `port-manager`입니다. 아래 slash 모양 문자열은 Skill이 해석하는 요청 의도 표기이며 Codex 자동완성에 등록된 사용자 명령이 아닙니다. 입력창이 이 문자열을 지원되지 않는 slash 명령으로 처리하면 자연어 예시나 `$port-manager` 호출을 사용하세요. Codex는 Skill 선택과 활성 Skill의 slash 목록 표시를 지원하지만, 공식 문서에는 이 colon 형식 별칭을 등록하는 방법이 설명되어 있지 않습니다.

| 기능 | 요청한 스킬 커맨드 | 자연어 예시 | 동작과 주의사항 |
|---|---|---|---|
| 로컬 포트 전체 조회 | [`/port-manger:all`](skills/port-manager/SKILL.md) | “로컬 개발 서버 포트 전부 표로 보여줘.” | 읽기 전용. 확정 개발 서버와 나머지 TCP 리스너를 구분하고 DB·시스템 서비스는 개발 서버로 단정하지 않습니다. |
| 포트 상세 조회 | [`/port-manger:detail 5173`](skills/port-manager/SKILL.md) | “5173 포트 상세 정보 보여줘.” | 리스너, 프로세스, 프로젝트와 워크트리 경로를 읽기 전용으로 조회합니다. |
| 저장소별 조회 | [`/port-manger:repo:정확한레포이름`](skills/port-manager/SKILL.md) | “frontend 레포에서 쓰는 포트를 워크트리별로 보여줘.” | 로컬 Git 저장소 이름과 정확히 일치시켜 조회하고 동명이인 경로를 구분합니다. |
| 서버 하나 또는 여러 개 종료 | [`/port-manger:delete 5173`](skills/port-manager/SKILL.md)<br>[`/port-manger:delete 3000 5173`](skills/port-manager/SKILL.md) | “5173 포트 내려.”<br>“3000과 5173 포트 내려.” | 명시한 포트의 확정 개발 서버만 종료합니다. 기본은 정상 종료이며 워크트리는 남습니다. |
| 현재 프로젝트 서버 교체 | [`/port-manger:replace 5173`](skills/port-manager/SKILL.md) | “현재 프로젝트 개발 서버를 5173 포트로 띄워.” | 현재 프로젝트의 manifest·lockfile·프레임워크를 확인하고 요청 포트 점유를 검증합니다. 다음 포트를 자동 선택하지 않습니다. |
| 서버 종료와 linked worktree 제거 | [`/port-manger:delete:worktree 5173`](skills/port-manager/SKILL.md) | “5173 포트랑 워크트리 제거해.” | 명시적으로 요청한 경우에만 수행합니다. main·현재·잠금·분리 HEAD·dirty·untracked·ignored·소속 불명은 거부하고 같은 워크트리의 다른 리스너도 제거를 막습니다. 브랜치는 보존하며 Git에 `--force`를 전달하지 않습니다. |

기존 `$port-manager` Skill 호출도 계속 지원합니다. 이 표는 요청 형식이며 `/port-manger:*` 자동완성 항목을 만들지는 않습니다.

## CLI 헬퍼 (내부 실행 수단)

`npx skills`로 Codex 공용 Skill을 설치했을 때 기본 헬퍼 경로는 `~/.agents/skills/port-manager/scripts/port-manager`입니다.

```bash
"$HOME/.agents/skills/port-manager/scripts/port-manager" all
"$HOME/.agents/skills/port-manager/scripts/port-manager" detail 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" repo frontend
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 3000 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 5173 --remove-worktree
"$HOME/.agents/skills/port-manager/scripts/port-manager" replace 4173
```

Codex 네이티브 플러그인의 캐시 경로는 Codex가 관리합니다. Codex에서 Skill을 호출하거나 Skill 패키지의 `scripts/` 디렉터리에 있는 헬퍼를 실행하세요. `replace`에는 `python3`, `git`, `lsof`, `ps`와 프로젝트 package manifest 및 lockfile이 선택한 패키지 관리자·런타임이 필요합니다.

아래 CLI 명령은 내부 구현 및 직접 실행용이며, 사용자-facing 호출은 위 표의 요청 문자열입니다.

## 설치

설치 문서는 공용 Skill, Codex 플러그인, Claude Code 플러그인, Hermes Agent, OpenClaw 순서입니다. 공용 설치는 `--copy`를 사용하며 Codex 기본 경로는 `~/.agents/skills/port-manager`입니다. `CODEX_HOME`은 헬퍼의 메타데이터 경로에 영향을 주지만 `npx skills` 설치 위치는 바꾸지 않습니다. 설치 명령은 자동 백업하지 않습니다. 같은 이름의 파일을 직접 수정했다면 업데이트 전에 백업하세요. `--yes`는 설치 확인 프롬프트를 자동 승인합니다.

### 1. 공용 Skill (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill port-manager \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

Codex에만 설치하려면 `--agent codex`를 사용합니다. Codex의 공용 기본 경로는 `~/.agents/skills/port-manager`입니다.

### 2. Codex 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "port-manager@opengiver-skills"
```

설치 후 새 Codex 세션에서 `$port-manager`와 원하는 하위 명령 또는 자연어 요청을 사용합니다.

### 3. Claude Code 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "port-manager@opengiver-skills"
```

### 4. Hermes Agent

Hermes URL 설치 명령은 `SKILL.md` 하나를 받지만 Port Manager에는 헬퍼 스크립트가 필요합니다. 전체 파일을 복사하는 위의 공용 `npx skills` 설치를 사용하세요. 수동 설치 시에는 `plugins/port-manager/skills/port-manager` 디렉터리 전체를 `~/.hermes/skills/port-manager`에 복사해야 합니다.

### 5. OpenClaw

현재 OpenClaw CLI에는 Skill 설치 명령이 없습니다. 전체 Skill 디렉터리를 복사한 뒤 `openclaw skills list`로 확인합니다.

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/port-manager"
mkdir -p "$target"
cp -R "$repo_dir/plugins/port-manager/skills/port-manager/." "$target/"
openclaw skills list
```

복사 명령은 자동 백업하지 않고 기존 파일을 병합합니다. 직접 수정한 파일이 있으면 복사 전에 백업하세요.

## 테스트

회귀 테스트는 임시 Git 저장소·워크트리와 테스트가 만든 더미 리스너만 사용합니다.

```bash
python3 -m unittest discover -s plugins/port-manager/tests -v
```
