# Biome · ESLint 전체 자동 수정

버전: 1.0.0

프로젝트 Biome·ESLint 설정에 이미 활성화된 자동 수정 규칙을 적용 대상 소스 전체에 적용합니다. 린트 설정을 새로 만들거나 기존 값을 바꾸지 않습니다.

에이전트와 무관한 SKILL.md를 Codex, Claude Code, Hermes Agent, OpenClaw의 네이티브 플러그인 또는 공용 Skill 설치로 사용할 수 있습니다. 현재 에이전트의 Skill 선택 방식에서 biome-eslint-ide-config-apply를 호출하세요.

## 자연어 트리거

- “저장소 전체에 설정된 Biome·ESLint 자동 수정 규칙을 적용해.”
- “전체 소스에 import와 Tailwind 자동 수정을 적용해.”
- “프로젝트 전체 린트·포맷 수정을 실행해.”

## 설치

### 1. 네 에이전트 공용 Skill (npx skills)

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill biome-eslint-ide-config-apply \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
~~~

### 2. Codex 네이티브 플러그인

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "biome-eslint-ide-config-apply@opengiver-skills"
~~~

### 3. Claude Code 네이티브 플러그인

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "biome-eslint-ide-config-apply@opengiver-skills"
~~~

### 4. Hermes Agent 네이티브 Skill

~~~bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/biome-eslint-ide-config-apply/skills/biome-eslint-ide-config-apply/SKILL.md" --yes
~~~

### 5. OpenClaw 네이티브 Skill

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/biome-eslint-ide-config-apply"
mkdir -p "$target"
cp -R "$repo_dir/plugins/biome-eslint-ide-config-apply/skills/biome-eslint-ide-config-apply/." "$target/"
openclaw skills list
~~~

처음 규칙을 설정하고 전체 적용 여부를 확인하려면 biome-eslint-ide-config-skill도 설치해 사용하세요.
