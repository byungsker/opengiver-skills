# Port Manager

[English](README.md) | [한국어](README.ko.md)

| | |
|---|---|
| **Name** | port-manager |
| **Description** | Safely inspect and manage local development-server TCP ports and linked worktrees |
| **Version** | 1.1.0 |
| **Triggers** | `/port-manger:all`, `/port-manger:detail`, `/port-manger:repo`, `/port-manger:delete`, `/port-manger:replace`, `/port-manger:delete:worktree`, `$port-manager` |

---

Inspect local TCP listeners and identify likely development servers by project and Git worktree. Stop or replace only a confirmed development server on a port the user explicitly selected. When explicitly requested, it can also remove that server's clean linked Git worktree after safety checks. The Skill is macOS-first and includes a repeatable CLI helper and regression tests.

## Safety

- `all`, `detail`, and `repo` are read-only. They distinguish confirmed development servers from other TCP listeners; databases, system services, and uncertain processes are not called development servers.
- Idle state is reported as unknown from OS listener data alone. CPU usage or an empty connection list is not proof of idleness.
- `delete` and `replace` recheck the PID, process start time, user, working directory, socket identity, and current port owner before signaling. Normal termination is the default. Forced termination requires an explicit `--force` request.
- `delete` and `replace` never remove a worktree by default. `delete PORT... --remove-worktree` opts in to removal. It refuses main, current, locked, detached, dirty, untracked, ignored, or ambiguous worktrees; any other active listener in the same worktree blocks removal. It rechecks process and Git registration before signaling and immediately before running ordinary `git worktree remove`. The branch is preserved, and `--force` is never passed to Git.
- `replace` reads the current project's package manifest and lockfile, starts its dev script, and verifies it acquired the requested port. It never silently moves to another port. If another process claims the port, it fails without signaling that process.
- The helper never reads process environment variables. It discards new server stdout/stderr and stores only minimal process metadata under `CODEX_HOME/port-manager/servers` or `~/.codex/port-manager/servers` when `CODEX_HOME` is unset.

## Request commands

The requested user-facing alias is spelled `port-manger`; the installable package and Skill name remains `port-manager`. The slash-shaped strings below are intent labels for the Skill, not custom commands registered in Codex autocomplete. Use them when the composer passes them as message text. If the composer treats one as an unsupported slash command, use the natural-language example or invoke `$port-manager`. Codex supports skill selection and shows enabled skills in its slash menu, but the official docs do not describe a way to register these exact colon forms as aliases.

| Feature | Requested skill command | Natural-language example | Behavior and cautions |
|---|---|---|---|
| List all local ports | [`/port-manger:all`](skills/port-manager/SKILL.md) | “Show all local development server ports in a table.” | Read-only. Separates confirmed dev servers from other TCP listeners; databases and system services are not mislabeled. |
| Inspect one port | [`/port-manger:detail 5173`](skills/port-manager/SKILL.md) | “Show details for port 5173.” | Read-only details for the listener, process, project, and worktree. |
| Filter by repository | [`/port-manger:repo:정확한레포이름`](skills/port-manager/SKILL.md) | “Show ports used by the exact `frontend` repo, grouped by worktree.” | Matches the local Git repository name exactly and distinguishes duplicate repo paths. |
| Stop one or more servers | [`/port-manger:delete 5173`](skills/port-manager/SKILL.md)<br>[`/port-manger:delete 3000 5173`](skills/port-manager/SKILL.md) | “Stop port 5173.”<br>“Stop ports 3000 and 5173.” | Stops only confirmed development servers on the explicitly selected ports. Normal termination is the default. Worktrees remain. |
| Replace current project's server | [`/port-manger:replace 5173`](skills/port-manager/SKILL.md) | “Start this project's dev server on port 5173.” | Inspects the current project's manifest, lockfile, and framework; verifies the requested port. It does not silently pick another port. |
| Stop server and remove its linked worktree | [`/port-manger:delete:worktree 5173`](skills/port-manager/SKILL.md) | “Stop port 5173 and remove its worktree.” | Explicit opt-in. Refuses main, current, locked, detached, dirty, untracked, ignored, or ambiguous worktrees. Another active listener in the same worktree blocks removal. The branch is preserved; Git is called without `--force`. |

The existing `$port-manager` skill invocation remains supported. These strings describe the requested interaction; they do not create `/port-manger:*` autocomplete entries.

## CLI helper (internal implementation)

For the shared Codex Skill installed by `npx skills`, the documented default helper path is `~/.agents/skills/port-manager/scripts/port-manager`:

```bash
"$HOME/.agents/skills/port-manager/scripts/port-manager" all
"$HOME/.agents/skills/port-manager/scripts/port-manager" detail 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" repo frontend
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 3000 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 5173 --remove-worktree
"$HOME/.agents/skills/port-manager/scripts/port-manager" replace 4173
```

For a native Codex plugin install, the plugin cache path is managed by Codex. Invoke the Skill in Codex, or run the helper from this Skill package's `scripts/` directory. These direct CLI commands are implementation details; the table above is the user-facing request syntax. `replace` needs `python3`, `git`, `lsof`, `ps`, and the package manager/runtime selected by the project's `package.json` and lockfile.

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
