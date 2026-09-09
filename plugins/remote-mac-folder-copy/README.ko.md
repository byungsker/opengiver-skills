# 원격 Mac 폴더 복사

버전: `1.0.0`

사용자가 지정한 로컬 폴더를 SSH로 지정한 원격 Mac에 복사하고, 원본을 보존하며, 체크섬 기반 dry-run으로 결과를 검증합니다. 호스트·계정·경로·자격 증명·삭제 범위를 추측하지 않습니다.

Skill을 공유할 때는 검토한 `SKILL.md`, 참조 파일, 스크립트만 전송합니다. 비밀값처럼 보이는 파일은 거부하며 `rsync --delete`는 사용하지 않습니다.

## 설치

### 1. 공용 Skill 설치 (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill remote-mac-folder-copy \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Codex 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "remote-mac-folder-copy@opengiver-skills"
```

### 3. Claude Code 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "remote-mac-folder-copy@opengiver-skills"
```

### 4. Hermes Agent 네이티브 Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/remote-mac-folder-copy/skills/remote-mac-folder-copy/SKILL.md" --yes
```

### 5. OpenClaw 네이티브 Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/remote-mac-folder-copy"
mkdir -p "$target"
cp -R "$repo_dir/plugins/remote-mac-folder-copy/skills/remote-mac-folder-copy/." "$target/"
openclaw skills list
```

현재 OpenClaw CLI에는 Skill 설치 하위 명령이 없으므로 위 명령은 관리되는 전역 Skill 디렉터리에 복사합니다. 복사 전에 `SOURCE_DIR`, `REMOTE_HOST`, `REMOTE_USER`, `REMOTE_DEST_DIR`를 명시적으로 지정하세요. SSH 연결 성공만으로 복사 완료라고 판단하지 않습니다.
