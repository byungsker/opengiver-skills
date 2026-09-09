# 웹 UI 폼 검증 패턴

버전: `1.0.0`

프로젝트의 기존 디자인 시스템, 상태 계약, API 경계, 접근성 동작, 재시도 동작과 오래된 응답 방지를 기준으로 웹 폼을 검토하거나 구현합니다. 특정 에이전트 워크플로우에 의존하지 않는 프레임워크 중립 Skill입니다.

## 설치

### 1. 네 에이전트 공용 Skill 설치 (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill form-validation-patterns \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Codex 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "form-validation-patterns@opengiver-skills"
```

### 3. Claude Code 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "form-validation-patterns@opengiver-skills"
```

### 4. Hermes Agent 네이티브 Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/form-validation-patterns/skills/form-validation-patterns/SKILL.md" --yes
```

### 5. OpenClaw 네이티브 Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/form-validation-patterns"
mkdir -p "$target"
cp -R "$repo_dir/plugins/form-validation-patterns/skills/form-validation-patterns/." "$target/"
openclaw skills list
```

현재 OpenClaw CLI에는 Skill 설치 하위 명령이 없으므로 위 명령은 관리되는 전역 Skill 디렉터리에 복사합니다. 현재 폼에 필요한 상태만 `references/state-matrix.md`에서 읽습니다.
