# Mac Storage Steward

Version: `1.0.0`

Audit Mac storage with read-only evidence, classify cleanup risk, require explicit selection for destructive actions, and verify the result. It does not encode personal paths or standing approvals.

## Installation

### 1. Shared Skill (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill mac-storage-steward \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Native Codex plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "mac-storage-steward@opengiver-skills"
```

### 3. Native Claude Code plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "mac-storage-steward@opengiver-skills"
```

### 4. Native Hermes Agent Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/mac-storage-steward/skills/mac-storage-steward/SKILL.md" --yes
```

### 5. Native OpenClaw Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/mac-storage-steward"
mkdir -p "$target"
cp -R "$repo_dir/plugins/mac-storage-steward/skills/mac-storage-steward/." "$target/"
openclaw skills list
```

The current OpenClaw CLI has no Skill install subcommand; the copy above uses its managed global Skill directory. The bundled inventory script is read-only. Review `references/cleanup-policy.md` before a cleanup.
