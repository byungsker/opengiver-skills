# Port Manager

버전: `1.0.0`

로컬 TCP 리스너를 조회하고 프로젝트·Git 워크트리 기준으로 개발 서버를 식별합니다. 사용자가 명시한 포트의 확인된 개발 서버만 정상 종료하거나 교체합니다. macOS 우선이며 반복 실행 가능한 CLI 헬퍼와 회귀 테스트를 포함합니다.

## 안전 기준

- `all`, `detail`, `repo`는 읽기 전용입니다. 확인된 개발 서버와 나머지 TCP 리스너를 구분하며 DB·시스템 서비스·분류가 불확실한 프로세스를 개발 서버라고 단정하지 않습니다.
- OS 리스너 정보만으로 유휴 상태를 알 수 없으면 `알 수 없음`으로 표시합니다. CPU 사용량 0이나 연결 없음만으로 유휴라고 결론 내리지 않습니다.
- `delete`, `replace`는 신호를 보내기 전에 PID, 시작 시각, 계정, 작업 경로, 소켓 식별자와 현재 포트 소유자를 다시 확인합니다. 기본은 정상 종료이며 `--force`는 명시적으로 요청한 경우에만 사용합니다.
- `replace`는 현재 프로젝트의 package manifest와 lockfile을 읽어 개발 스크립트를 시작한 뒤 요청한 포트를 실제로 점유했는지 검증합니다. 다음 포트로 자동 이동하지 않습니다. 다른 프로세스가 포트를 점유하면 그 프로세스를 건드리지 않고 실패합니다.
- 프로세스 환경 변수는 읽지 않습니다. 새 서버의 stdout/stderr는 버리고 `CODEX_HOME/port-manager/servers` 또는 `CODEX_HOME`이 없을 때 `~/.codex/port-manager/servers`에 최소 메타데이터만 저장합니다.

## 사용

Codex에서 `$port-manager all`, `$port-manager detail 5173`, `$port-manager repo frontend`, `$port-manager delete 3000 5173`, `$port-manager replace 4173`처럼 요청하거나 자연어로 설명할 수 있습니다. `/port-manager:all` 슬래시 명령은 등록하지 않습니다. 이 플러그인은 명령어가 아닌 Skill을 제공합니다.

`npx skills`로 Codex 공용 Skill을 설치했을 때 기본 헬퍼 경로는 `~/.agents/skills/port-manager/scripts/port-manager`입니다.

```bash
"$HOME/.agents/skills/port-manager/scripts/port-manager" all
"$HOME/.agents/skills/port-manager/scripts/port-manager" detail 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" repo frontend
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 3000 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" replace 4173
```

Codex 네이티브 플러그인의 캐시 경로는 Codex가 관리합니다. Codex에서 Skill을 호출하거나 Skill 패키지의 `scripts/` 디렉터리에 있는 헬퍼를 실행하세요. `replace`에는 `python3`, `git`, `lsof`, `ps`와 프로젝트 package manifest 및 lockfile이 선택한 패키지 관리자·런타임이 필요합니다.

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
