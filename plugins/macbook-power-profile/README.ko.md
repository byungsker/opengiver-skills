# MacBook 전원 프로필

버전: `1.0.0`

macOS의 잠자기 방지, 뚜껑 닫힘 실행, 기본 충전 한도, 배터리 건강 상태를 각각의 근거로 확인하고 설정합니다. 읽기 전용 상태 확인과 설정 변경을 분리하며, 서드파티 배터리 도구를 설치하거나 제어하지 않습니다.

설정 변경은 사용자가 명시적으로 요청한 경우에만 수행합니다. 배터리 전원에서 뚜껑을 닫은 채 실행하는 모드는 암묵적으로 켜지 않으며, 복원할 때는 기록한 스냅샷을 사용하고 기본값을 추측하지 않습니다.

## 설치

### 1. 공용 Skill 설치 (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill macbook-power-profile \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Codex 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "macbook-power-profile@opengiver-skills"
```

### 3. Claude Code 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "macbook-power-profile@opengiver-skills"
```

### 4. Hermes Agent 네이티브 Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/macbook-power-profile/skills/macbook-power-profile/SKILL.md" --yes
```

### 5. OpenClaw 네이티브 Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/macbook-power-profile"
mkdir -p "$target"
cp -R "$repo_dir/plugins/macbook-power-profile/skills/macbook-power-profile/." "$target/"
openclaw skills list
```

현재 OpenClaw CLI에는 Skill 설치 하위 명령이 없으므로 위 명령은 관리되는 전역 Skill 디렉터리에 복사합니다. 포함된 배터리 건강 스크립트는 읽기 전용이며, `pmset` 값이나 충전 한도 UI를 바꾸기 전에 Skill의 안전 규칙을 확인하세요.
