# 업무 메신저를 Obsidian으로

버전: `1.0.0`

업무 메신저 export를 사용자가 지정한 Obsidian vault의 근거 기반 한글 인수인계 문서로 정리합니다. source cutoff를 보존하고, 직접 발신과 본문 언급을 분리하며, 확인되지 않은 현재 상태를 명확히 남깁니다.

개인 vault 경로를 가정하지 않으며, 자격 증명·고객 데이터·비공개 URL·secret-like 원문을 복사하지 않습니다.

## 설치

### 1. 네 에이전트 공용 Skill 설치 (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill business-messenger-to-obsidian \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Codex 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "business-messenger-to-obsidian@opengiver-skills"
```

### 3. Claude Code 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "business-messenger-to-obsidian@opengiver-skills"
```

### 4. Hermes Agent 네이티브 Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/business-messenger-to-obsidian/skills/business-messenger-to-obsidian/SKILL.md" --yes
```

### 5. OpenClaw 네이티브 Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/business-messenger-to-obsidian"
mkdir -p "$target"
cp -R "$repo_dir/plugins/business-messenger-to-obsidian/skills/business-messenger-to-obsidian/." "$target/"
openclaw skills list
```

현재 OpenClaw CLI에는 Skill 설치 하위 명령이 없으므로 위 명령은 관리되는 전역 Skill 디렉터리에 복사합니다. 문서를 만들기 전에 vault와 출력 하위 경로를 지정해야 합니다.
