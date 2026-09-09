# MacBook Power Profile

Version: `1.0.0`

Inspect and configure macOS power behavior with separate evidence for sleep prevention, closed-lid operation, native charge limits, and battery health. The Skill keeps read-only status checks separate from configuration changes and does not install or control third-party battery tools.

Configuration changes require an explicit user request. Battery closed-lid mode is never enabled implicitly, and restoration uses a recorded snapshot rather than guessed defaults.

## Installation

### 1. Shared Skill (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill macbook-power-profile \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

### 2. Native Codex plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "macbook-power-profile@opengiver-skills"
```

### 3. Native Claude Code plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "macbook-power-profile@opengiver-skills"
```

### 4. Native Hermes Agent Skill

```bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/macbook-power-profile/skills/macbook-power-profile/SKILL.md" --yes
```

### 5. Native OpenClaw Skill

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/macbook-power-profile"
mkdir -p "$target"
cp -R "$repo_dir/plugins/macbook-power-profile/skills/macbook-power-profile/." "$target/"
openclaw skills list
```

The current OpenClaw CLI has no Skill install subcommand; the copy above uses its managed global Skill directory. The bundled battery-health script is read-only. Review the Skill's safety rules before changing `pmset` values or the charge-limit UI.
