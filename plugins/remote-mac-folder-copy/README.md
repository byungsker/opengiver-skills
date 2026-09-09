# Remote Mac Folder Copy

Version: `1.0.0`

Copy a user-selected local folder to a specified remote Mac over SSH, preserve the source, and verify the result with a checksum-based dry run. The Skill never guesses hosts, accounts, paths, credentials, or deletion scope.

When sharing a Skill, it transfers only the reviewed `SKILL.md`, references, and scripts. It refuses secret-like files and never uses `rsync --delete`.

## Installation

### 1. Shared Skill (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill remote-mac-folder-copy \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Native Codex plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "remote-mac-folder-copy@opengiver-skills"
```

### 3. Native Claude Code plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "remote-mac-folder-copy@opengiver-skills"
```

### 4. Native Hermes Agent Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/remote-mac-folder-copy/skills/remote-mac-folder-copy/SKILL.md" --yes
```

### 5. Native OpenClaw Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/remote-mac-folder-copy"
mkdir -p "$target"
cp -R "$repo_dir/plugins/remote-mac-folder-copy/skills/remote-mac-folder-copy/." "$target/"
openclaw skills list
```

The current OpenClaw CLI has no Skill install subcommand; the copy above uses its managed global Skill directory. Before running a copy, provide `SOURCE_DIR`, `REMOTE_HOST`, `REMOTE_USER`, and `REMOTE_DEST_DIR` explicitly. A successful SSH connection alone is not proof that the copy is complete.
