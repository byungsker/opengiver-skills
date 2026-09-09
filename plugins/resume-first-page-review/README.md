# Resume First-Page Review

Version: `1.0.0`

Review the first page or first screen of a resume for opening clarity, target-role fit, evidence density, and fixed-layout readability. The Skill keeps first-page findings separate from whole-resume, factual, submission, and rendered-artifact verdicts.

It does not invent metrics, ownership, dates, or seniority, and it does not modify or submit a resume unless explicitly asked.

## Installation

### 1. Shared Skill (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill resume-first-page-review \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Native Codex plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "resume-first-page-review@opengiver-skills"
```

### 3. Native Claude Code plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "resume-first-page-review@opengiver-skills"
```

### 4. Native Hermes Agent Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/resume-first-page-review/skills/resume-first-page-review/SKILL.md" --yes
```

### 5. Native OpenClaw Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/resume-first-page-review"
mkdir -p "$target"
cp -R "$repo_dir/plugins/resume-first-page-review/skills/resume-first-page-review/." "$target/"
openclaw skills list
```

The current OpenClaw CLI has no Skill install subcommand; the copy above uses its managed global Skill directory. Read `references/first-page-rubric.md` for the bounded review criteria. Provide the first-page artifact and target role when target fit is part of the request.
