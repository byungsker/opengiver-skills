# Biome · ESLint Full-Project Autofix

Version: 1.0.0

Apply the autofix rules already enabled in a project’s Biome and ESLint configuration across all eligible source files. This Skill does not create or change lint settings.

The agent-neutral SKILL.md works through Codex, Claude Code, Hermes Agent, and OpenClaw native plugin or shared Skill installation. Use the current agent's normal Skill invocation interface with the name biome-eslint-ide-config-apply.

## Natural-language triggers

- “Apply the configured Biome and ESLint autofixes across the whole project.”
- “Apply the import and Tailwind fixes to all source files.”
- “Run the full-project lint and formatting fixes.”

## Installation

### 1. Shared Skill (npx skills)

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill biome-eslint-ide-config-apply \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
~~~

### 2. Native Codex plugin

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "biome-eslint-ide-config-apply@opengiver-skills"
~~~

### 3. Native Claude Code plugin

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "biome-eslint-ide-config-apply@opengiver-skills"
~~~

### 4. Native Hermes Agent Skill

~~~bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
hermes skills install "$RAW_REPO/plugins/biome-eslint-ide-config-apply/skills/biome-eslint-ide-config-apply/SKILL.md" --yes
~~~

### 5. Native OpenClaw Skill

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/biome-eslint-ide-config-apply"
mkdir -p "$target"
cp -R "$repo_dir/plugins/biome-eslint-ide-config-apply/skills/biome-eslint-ide-config-apply/." "$target/"
openclaw skills list
~~~

For rule configuration before the first full application, install and use biome-eslint-ide-config-skill.
