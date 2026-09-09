# Mac 저장 공간 관리

버전: `1.0.0`

읽기 전용 근거로 Mac 저장 공간을 조사하고, 정리 위험을 분류하고, 삭제 작업에는 명시적 선택을 요구하며, 결과를 검증합니다. 개인 경로나 개인별 상시 승인을 포함하지 않습니다.

## 설치

### 1. 네 에이전트 공용 Skill 설치 (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill mac-storage-steward \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Codex 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "mac-storage-steward@opengiver-skills"
```

### 3. Claude Code 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "mac-storage-steward@opengiver-skills"
```

### 4. Hermes Agent 네이티브 Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/mac-storage-steward/skills/mac-storage-steward/SKILL.md" --yes
```

### 5. OpenClaw 네이티브 Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/mac-storage-steward"
mkdir -p "$target"
cp -R "$repo_dir/plugins/mac-storage-steward/skills/mac-storage-steward/." "$target/"
openclaw skills list
```

현재 OpenClaw CLI에는 Skill 설치 하위 명령이 없으므로 위 명령은 관리되는 전역 Skill 디렉터리에 복사합니다. 포함된 인벤토리 스크립트는 읽기 전용이며, 정리 전에 `references/cleanup-policy.md`를 읽습니다.
