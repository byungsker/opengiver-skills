# Business Messenger to Obsidian

Version: `1.0.0`

Turn work-messenger exports into evidence-bound Korean handoff history in a user-selected Obsidian vault. The Skill preserves source cutoffs, separates direct messages from mentions, and keeps uncertain current state explicit.

It never assumes a personal vault path and never copies credentials, customer data, private URLs, or raw secret-like attachments.

## Installation

### 1. Shared Skill (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill business-messenger-to-obsidian \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Native Codex plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "business-messenger-to-obsidian@opengiver-skills"
```

### 3. Native Claude Code plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "business-messenger-to-obsidian@opengiver-skills"
```

### 4. Native Hermes Agent Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/business-messenger-to-obsidian/skills/business-messenger-to-obsidian/SKILL.md" --yes
```

### 5. Native OpenClaw Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/business-messenger-to-obsidian"
mkdir -p "$target"
cp -R "$repo_dir/plugins/business-messenger-to-obsidian/skills/business-messenger-to-obsidian/." "$target/"
openclaw skills list
```

The current OpenClaw CLI has no Skill install subcommand; the copy above uses its managed global Skill directory. Select the vault and output subdirectory before creating a document.
