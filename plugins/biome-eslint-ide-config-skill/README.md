# Biome · ESLint IDE Configuration

Version: 1.1.0

Configure project-specific Biome import organization, ESLint Tailwind class wrapping and canonical-class checks, and save actions in Zed or VS Code. The Skill inspects the existing project before proposing settings and asks before applying fixes across the repository. It also owns the full-project apply workflow.

This package contains one agent-neutral Skill and a project-wide apply slash command:

- `/biome-eslint-ide-config-skill:apply`: apply the configured autofix rules across eligible source files.

Codex, Claude Code, Hermes Agent, and OpenClaw can load the same SKILL.md guidance through their native plugin or shared Skill installation. Each agent uses its own Skill invocation syntax; natural-language triggers are included in the Skill descriptions.

## Installation

### 1. Shared Skills for all agents (npx skills)

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill biome-eslint-ide-config-skill \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
~~~

### 2. Native Codex plugins

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "biome-eslint-ide-config-skill@opengiver-skills"
~~~

### 3. Native Claude Code plugins

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "biome-eslint-ide-config-skill@opengiver-skills"
~~~

### 4. Native Hermes Agent Skills

~~~bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/biome-eslint-ide-config-skill/skills/biome-eslint-ide-config-skill/SKILL.md" --yes
~~~

### 5. Native OpenClaw Skills

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/biome-eslint-ide-config-skill"
mkdir -p "$target"
cp -R "$repo_dir/plugins/biome-eslint-ide-config-skill/skills/biome-eslint-ide-config-skill/." "$target/"
openclaw skills list
~~~

## Use

Invoke biome-eslint-ide-config-skill through the current agent's Skill interface to configure a project. After the initial setup and representative-file checks, it asks whether to apply the selected rules across all eligible files. After installing the native Claude Code plugin, use `/biome-eslint-ide-config-skill:apply` for a later full application. Shared Skill installations use the natural-language trigger: “Apply the configured Biome and ESLint autofixes across the whole project.”
