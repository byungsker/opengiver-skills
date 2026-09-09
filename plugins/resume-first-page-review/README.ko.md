# 이력서 첫 페이지 검토

버전: `1.0.0`

이력서 첫 페이지 또는 첫 화면의 첫인상 명확성, 목표 직무 적합성, 근거 밀도, 고정 레이아웃 가독성을 검토합니다. 첫 페이지 발견 사항을 전체 이력서·사실성·제출·렌더링 산출물의 판정과 분리합니다.

정량 수치, 소유 범위, 날짜, 직급을 만들어내지 않으며, 사용자가 명시적으로 요청하지 않으면 이력서를 수정하거나 제출하지 않습니다.

## 설치

### 1. 공용 Skill 설치 (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill resume-first-page-review \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Codex 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "resume-first-page-review@opengiver-skills"
```

### 3. Claude Code 네이티브 플러그인

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "resume-first-page-review@opengiver-skills"
```

### 4. Hermes Agent 네이티브 Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/resume-first-page-review/skills/resume-first-page-review/SKILL.md" --yes
```

### 5. OpenClaw 네이티브 Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/resume-first-page-review"
mkdir -p "$target"
cp -R "$repo_dir/plugins/resume-first-page-review/skills/resume-first-page-review/." "$target/"
openclaw skills list
```

현재 OpenClaw CLI에는 Skill 설치 하위 명령이 없으므로 위 명령은 관리되는 전역 Skill 디렉터리에 복사합니다. 제한된 검토 기준은 `references/first-page-rubric.md`에서 확인하세요. 목표 직무 적합성을 검토하려면 첫 페이지 산출물과 목표 직무를 함께 제공해야 합니다.
