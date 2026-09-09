# Form Validation Patterns

Version: `1.0.0`

Review or build web forms around the project's existing design system, state contract, API boundary, accessibility behavior, retry behavior, and stale-response protection. The Skill is framework-neutral and does not depend on a particular agent workflow.

## Installation

### 1. Shared Skill (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill form-validation-patterns \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Native Codex plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "form-validation-patterns@opengiver-skills"
```

### 3. Native Claude Code plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "form-validation-patterns@opengiver-skills"
```

### 4. Native Hermes Agent Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/form-validation-patterns/skills/form-validation-patterns/SKILL.md" --yes
```

### 5. Native OpenClaw Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/form-validation-patterns"
mkdir -p "$target"
cp -R "$repo_dir/plugins/form-validation-patterns/skills/form-validation-patterns/." "$target/"
openclaw skills list
```

The current OpenClaw CLI has no Skill install subcommand; the copy above uses its managed global Skill directory. Read `references/state-matrix.md` only for the states relevant to the current form.
