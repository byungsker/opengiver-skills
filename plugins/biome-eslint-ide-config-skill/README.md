# Biome · ESLint IDE Configuration

Version: 1.0.0

Configure project-specific Biome import organization, ESLint Tailwind class wrapping and canonical-class checks, and save actions in Zed or VS Code. The Skill inspects the existing project before proposing settings and asks before applying fixes across the repository.

This package contains two agent-neutral Skills:

- biome-eslint-ide-config-skill: configure and verify project rules and editor settings.
- biome-eslint-ide-config-apply: apply the configured autofix rules across eligible source files.

Codex, Claude Code, Hermes Agent, and OpenClaw can load the same SKILL.md guidance through their native plugin or shared Skill installation. Each agent uses its own Skill invocation syntax; natural-language triggers are included in the Skill descriptions.

## Installation

### 1. Shared Skills for all agents (npx skills)

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
for skill in biome-eslint-ide-config-apply biome-eslint-ide-config-skill; do
  npx skills add "$REMOTE_REPO" --skill "$skill" \
    --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
done
~~~

### 2. Native Codex plugins

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "biome-eslint-ide-config-skill@opengiver-skills"
codex plugin add "biome-eslint-ide-config-apply@opengiver-skills"
~~~

### 3. Native Claude Code plugins

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "biome-eslint-ide-config-skill@opengiver-skills"
claude plugin install "biome-eslint-ide-config-apply@opengiver-skills"
~~~

### 4. Native Hermes Agent Skills

~~~bash
RAW_REPO="${RAW_REPO:-https://raw.githubusercontent.com/byungsker/opengiver-skills/main}"
for skill in biome-eslint-ide-config-apply biome-eslint-ide-config-skill; do
  hermes skills install "$RAW_REPO/plugins/$skill/skills/$skill/SKILL.md" --yes
done
~~~

### 5. Native OpenClaw Skills

~~~bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
for skill in biome-eslint-ide-config-apply biome-eslint-ide-config-skill; do
  target="$HOME/.openclaw/skills/$skill"
  mkdir -p "$target"
  cp -R "$repo_dir/plugins/$skill/skills/$skill/." "$target/"
done
openclaw skills list
~~~

## Use

Invoke biome-eslint-ide-config-skill through the current agent's Skill interface to configure a project. After the initial setup and representative-file checks, it asks whether to apply the selected rules across all eligible files.

For a later full application, invoke biome-eslint-ide-config-apply or ask: “Apply the configured Biome and ESLint autofixes across the whole project.”
