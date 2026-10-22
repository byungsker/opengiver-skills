# Port Manager

Version: `1.0.0`

Inspect local TCP listeners and identify likely development servers by project and Git worktree. Stop or replace only a confirmed development server on a port the user explicitly selected. The Skill is macOS-first and includes a repeatable CLI helper and regression tests.

## Safety

- `all`, `detail`, and `repo` are read-only. They distinguish confirmed development servers from other TCP listeners; databases, system services, and uncertain processes are not called development servers.
- Idle state is reported as unknown from OS listener data alone. CPU usage or an empty connection list is not proof of idleness.
- `delete` and `replace` recheck the PID, process start time, user, working directory, socket identity, and current port owner before signaling. Normal termination is the default. Forced termination requires an explicit `--force` request.
- `replace` reads the current project's package manifest and lockfile, starts its dev script, and verifies it acquired the requested port. It never silently moves to another port. If another process claims the port, it fails without signaling that process.
- The helper never reads process environment variables. It discards new server stdout/stderr and stores only minimal process metadata under `CODEX_HOME/port-manager/servers` or `~/.codex/port-manager/servers` when `CODEX_HOME` is unset.

## Use

In Codex, invoke `$port-manager all`, `$port-manager detail 5173`, `$port-manager repo frontend`, `$port-manager delete 3000 5173`, or `$port-manager replace 4173`. Natural-language requests work as well. There is no `/port-manager:all` slash command; the plugin registers a Skill without commands.

For the shared Codex Skill installed by `npx skills`, the documented default helper path is `~/.agents/skills/port-manager/scripts/port-manager`:

```bash
"$HOME/.agents/skills/port-manager/scripts/port-manager" all
"$HOME/.agents/skills/port-manager/scripts/port-manager" detail 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" repo frontend
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 3000 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" replace 4173
```

For a native Codex plugin install, the plugin cache path is managed by Codex. Invoke the Skill in Codex, or run the helper from this Skill package's `scripts/` directory. `replace` needs `python3`, `git`, `lsof`, `ps`, and the package manager/runtime selected by the project's `package.json` and lockfile.

## Installation

Install in this order: shared portable Skill, Codex plugin, Claude Code plugin, Hermes Agent, then OpenClaw. Shared installation uses `--copy`; its Codex destination is `~/.agents/skills/port-manager`. `CODEX_HOME` affects the helper's metadata directory, not the `npx skills` destination. No installation backup is created automatically. Back up hand-edited same-name files before updating; `--yes` accepts installer prompts.

### 1. Shared Skill (`npx skills`)

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
npx skills add "$REMOTE_REPO" --skill port-manager \
  --agent codex claude-code hermes-agent openclaw --global --copy --yes --full-depth
```

For Codex only, use `--agent codex`. The default shared Codex path is `~/.agents/skills/port-manager`.

### 2. Native Codex plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
codex plugin marketplace add "$REMOTE_REPO" --ref main
codex plugin add "port-manager@opengiver-skills"
```

Start a new Codex session, then invoke `$port-manager` with the requested subcommand or natural-language task.

### 3. Native Claude Code plugin

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
claude plugin marketplace add "$REMOTE_REPO"
claude plugin install "port-manager@opengiver-skills"
```

### 4. Hermes Agent

Hermes' URL installer takes a single `SKILL.md`, while Port Manager requires the bundled helper script. Use the shared `npx skills` method above to install the complete directory. If installing manually, copy the full `plugins/port-manager/skills/port-manager` directory into `~/.hermes/skills/port-manager`.

### 5. OpenClaw

The OpenClaw CLI currently has no Skill install subcommand. Copy the full Skill directory and verify it with `openclaw skills list`:

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/port-manager"
mkdir -p "$target"
cp -R "$repo_dir/plugins/port-manager/skills/port-manager/." "$target/"
openclaw skills list
```

Back up local edits before copying an update; this copy merges files and does not create a backup.

## Tests

The regression suite uses temporary Git repositories, worktrees, and dummy listeners only:

```bash
python3 -m unittest discover -s plugins/port-manager/tests -v
```
