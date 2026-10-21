# Biome · ESLint IDE 설정

버전: 1.1.0

프로젝트별 Biome import 정렬, ESLint Tailwind 클래스 줄바꿈과 표준 클래스 검사, Zed·VS Code 저장 동작을 설정합니다. 기존 프로젝트 설정을 조사해 변경안을 제시하고, 저장소 전체 자동 수정은 별도로 확인한 뒤 적용합니다. 전체 적용 절차도 같은 Skill이 소유합니다.

이 패키지는 에이전트와 무관한 Skill 하나와 전체 적용용 슬래시 명령을 제공합니다.

- `/biome-eslint-ide-config-skill:apply`: 설정된 자동 수정 규칙을 대상 소스 전체에 적용합니다.

Codex, Claude Code, Hermes Agent, OpenClaw는 같은 SKILL.md 지침을 각자의 플러그인 또는 공용 Skill 설치 방식으로 사용합니다. Skill 호출 문법은 에이전트마다 다르며 자연어 트리거는 Skill 설명에 포함되어 있습니다.

## 설치

### 1. 네 에이전트 공용 Skill (npx skills)

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill biome-eslint-ide-config-skill \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
~~~

### 2. Codex 네이티브 플러그인

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "biome-eslint-ide-config-skill@opengiver-skills"
~~~

### 3. Claude Code 네이티브 플러그인

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "biome-eslint-ide-config-skill@opengiver-skills"
~~~

### 4. Hermes Agent 네이티브 Skill

~~~bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/biome-eslint-ide-config-skill/skills/biome-eslint-ide-config-skill/SKILL.md" --yes
~~~

### 5. OpenClaw 네이티브 Skill

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/biome-eslint-ide-config-skill"
mkdir -p "$target"
cp -R "$repo_dir/plugins/biome-eslint-ide-config-skill/skills/biome-eslint-ide-config-skill/." "$target/"
openclaw skills list
~~~

## 사용

프로젝트 규칙 설정은 현재 에이전트의 Skill 호출 방식으로 biome-eslint-ide-config-skill을 실행합니다. 초기 설정과 대표 파일 검증이 끝나면 대상 파일 전체에 규칙을 적용할지 묻습니다. 네이티브 Claude Code 플러그인을 설치하면 `/biome-eslint-ide-config-skill:apply`로 나중에 전체 적용할 수 있습니다. 공용 Skill 설치에서는 “저장소 전체에 설정된 Biome·ESLint 자동 수정 규칙을 적용해”라고 요청해도 됩니다.
