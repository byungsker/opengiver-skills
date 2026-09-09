# Opengiver Skills

[English](README.md) | [Korean](README.ko.md)

Opengiver Skills is a place where good ways of working, useful knowledge, and practical tools are refined and given forward. It keeps what one person has learned from stopping with that person, and helps the next person use it, improve it, and pass it on again.

The core of each Skill lives in a reusable `SKILL.md` and the references it needs. Codex, Claude Code, Hermes Agent, and OpenClaw receive runtime-native installation and discovery paths, while the Skill's meaning stays portable. We connect summaries to source evidence and conditions of use so an agent opens only what the current task requires.

**Contributions welcome!** Found a way to improve a plugin or have a new one to add? [Open a PR](#contributing).

## The Opengiver Philosophy: Refine Good Things, Then Give Them Forward

Opengiver begins with a simple belief: good work should not stop with the person who figured it out. A better way to work, knowledge worth keeping, or a tool that removes friction creates more value when someone else can understand it and use it.

We are not building a one-way download shelf. We refine what we give so it is useful in real work, and we give it in a form that the receiver can adapt, improve, and pass on. A Skill is not complete when it works once. It is complete when another person can understand it, apply it, make it better, and become the next giver.

- **Give something usable:** Turn experience into clear guidance, working tools, and references that can survive outside the original context.
- **Give without creating dependence:** Explain the reasoning and boundaries so people can continue without needing the original author.
- **Create the next giver:** Make every contribution easy to adapt, extend, and return to the commons.
- **Keep the door open:** Welcome anyone who can benefit, improve the work, or share something better.

## What Is a Plugin?

A plugin packages a portable Skill so a specific agent can discover, install, and invoke it. In this repository, the Skill contains the agent-neutral operating guidance while the plugin supplies commands, manifests, workflows, and runtime integration. A Skill can therefore be installed on its own, or delivered through the native packaging of the agent you use.

## Available Plugins

| Plugin | Version | Description | Commands |
|--------|---------|-------------|----------|
| [linear-simple](plugins/linear-simple) | `1.1.6` | Linear GraphQL API for issue management | `/linear-simple:setup`, `/linear-simple:get`, `/linear-simple:create` |
| [git-worktree](plugins/git-worktree) | `1.0.0` | Git worktree protocol for parallel development with isolated workspaces | Skill-only (no commands) |
| [db-safety](plugins/db-safety) | `1.0.0` | Database safety protocol to prevent accidental data loss | Skill-only (no commands) |
| [toss-frontend-fundamentals](plugins/toss-frontend-fundamentals) | `1.0.0` | Source-backed Toss code-quality review for React and TypeScript | Skill-only (no commands) |

## Installation

### Method 1: Install a shared Skill for your agents (`npx skills`)

The following command copies the portable `SKILL.md` files and their references into the user Skill directories for your agents. The installation order is always Codex, Claude Code, Hermes Agent, and OpenClaw. Plugin commands and marketplace features are not included.

```bash
for skill in linear-simple db-safety git-worktree toss-frontend-fundamentals; do
  npx skills add https://github.com/byungsker/opengiver-skills \
    --skill "$skill" \
    --agent codex claude-code hermes-agent openclaw \
    --global --copy --yes --full-depth
done
```

To install for only one agent, leave a single value after `--agent`.

```bash
npx skills add https://github.com/byungsker/opengiver-skills \
  --skill toss-frontend-fundamentals \
  --agent codex --global --copy --yes --full-depth
```

The default destinations are:

| Agent | `--agent` value | Default path |
|---|---|---|
| Codex | `codex` | `~/.agents/skills/<skill>` |
| Claude Code | `claude-code` | `~/.claude/skills/<skill>` |
| Hermes Agent | `hermes-agent` | `~/.hermes/skills/<skill>` |
| OpenClaw | `openclaw` | `~/.openclaw/skills/<skill>` |

The paths above are the shared installation paths currently reported by `npx skills`. Native Codex plugins use plugin configuration and caches, while TFF's separate `install.sh --target codex` uses `CODEX_HOME` or `~/.codex/skills`.

### Method 2: Install the native Codex plugin

```bash
codex plugin marketplace add byungsker/opengiver-skills --ref main
for plugin in linear-simple db-safety git-worktree toss-frontend-fundamentals; do
  codex plugin add "$plugin@opengiver-skills"
done
```

Start a new Codex session after installation. Unlike a portable Skill, a Codex plugin also installs its manifest and connected components.

### Method 3: Install the native Claude Code plugin

```bash
claude plugin marketplace add byungsker/opengiver-skills
for plugin in linear-simple db-safety git-worktree toss-frontend-fundamentals; do
  claude plugin install "$plugin@opengiver-skills"
done
```

Plugins with slash commands must be installed this way. For example, `linear-simple` provides `/linear-simple:setup`.

### Method 4: Install a native Hermes Agent Skill

The Hermes Agent Skill installer accepts a direct `SKILL.md` URL.

```bash
for skill in linear-simple db-safety git-worktree toss-frontend-fundamentals; do
  hermes skills install \
    "https://raw.githubusercontent.com/byungsker/opengiver-skills/main/plugins/$skill/skills/$skill/SKILL.md" \
    --yes
done
```

This is the Hermes Agent native installation path. For Skills with many references, prefer Method 1 so the complete directory is preserved.

### Method 5: Install a native OpenClaw Skill

OpenClaw installs a local Skill directory whose root contains `SKILL.md`. Because this repository contains multiple Skills, clone it and pass each Skill subdirectory to the installer.

```bash
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 https://github.com/byungsker/opengiver-skills.git "$repo_dir"
for skill in linear-simple db-safety git-worktree toss-frontend-fundamentals; do
  openclaw skills install "$repo_dir/plugins/$skill/skills/$skill" \
    --as "$skill" --global
done
```

`--global` installs to `~/.openclaw/skills`. If your OpenClaw version does not provide `openclaw skills install`, update OpenClaw or place the same Skill directory under `skills/<skill>` in the active workspace.

### Optional: Claude Code UI or repository clone

In Claude Code, run `/plugin`, add `byungsker/opengiver-skills` from the `Marketplaces` tab, and install a plugin from `Discover`. To download the repository directly, use:

```bash
git clone https://github.com/byungsker/opengiver-skills.git
cp -r opengiver-skills/plugins/* ~/.claude/plugins/
```

## Plugin Details

### linear-simple

Direct Linear GraphQL API calls without MCP, improving token efficiency by 50-70%.

**Features:**
- Issue CRUD (Create, Read, Update, Delete)
- Comment management
- Status updates
- PR + Linear sync

**Setup:**
```bash
/linear-simple:setup
```

[View full documentation →](plugins/linear-simple/README.md)

### git-worktree

Git Worktree Protocol for safe parallel development with isolated workspaces.

**Features:**
- Isolated workspaces for each feature/fix branch
- Automatic environment file management (.env, secrets)
- Dev server management with `wt` CLI
- Flutter worktree switcher (`wtf`) for mobile development
- Disk optimization with shared build caches
- Automatic cleanup after PR merge

**Triggers:**
```
"worktree"
"wt"
"Start implementing"
"start working"
"parallel development"
"feature branch"
```

[View full documentation →](plugins/git-worktree/README.md)

---

### db-safety

Database Safety Protocol to prevent accidental data loss and enforce safe migrations.

**Features:**
- Dangerous operation blocking (DROP, ALTER, DELETE, TRUNCATE)
- SQL query safety guide with safe vs. unsafe patterns
- Safe migration patterns (3-step deletion, Expand-Contract)
- Risk level classification (LOW, MEDIUM, HIGH, CRITICAL)
- Environment separation (Dev DB vs. Prod DB)
- Rollback procedures for migration failures

**Triggers:**
```
"DROP TABLE"
"ALTER COLUMN"
"DELETE FROM"
"migration"
"SQL"
"dangerous operation"
```

[View full documentation →](plugins/db-safety/README.md)

---

### toss-frontend-fundamentals

Reviews React and TypeScript frontend code using the source-backed Toss Frontend Fundamentals principles: readability, predictability, cohesion, and coupling. The package includes the mapped source documents instead of only a summary, so the agent can read the relevant original document before reporting a finding.

Use Method 1 for the shared agent installation. TFF includes a source snapshot, so native Codex and Claude Code plugins also install the source references. The Hermes Agent URL installation installs the entry Skill; use Method 1 when you need the complete source snapshot.

```bash
git clone https://github.com/byungsker/opengiver-skills.git
cd opengiver-skills
./plugins/toss-frontend-fundamentals/install.sh --target all
```

After cloning the repository, use `--target all` to place the complete TFF package for every agent. Use one of `--target codex`, `--target claude`, `--target hermes`, or `--target openclaw` for a single agent.

## Repository Structure

```
opengiver-skills/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace registry
├── plugins/
│   ├── linear-simple/            # Linear API plugin
│   │   ├── .claude-plugin/
│   │   ├── commands/
│   │   ├── skills/
│   │   └── README.md
│   ├── git-worktree/             # Git worktree protocol plugin
│   │   ├── .claude-plugin/
│   │   ├── skills/
│   │   └── README.md
│   ├── db-safety/                # Database safety protocol plugin
│   │   ├── .claude-plugin/
│   │   ├── skills/
│   │   └── README.md
│   └── toss-frontend-fundamentals/ # Toss source-backed frontend code-quality review
│       ├── .claude-plugin/
│       ├── install.sh
│       ├── skills/
│       └── README.md
├── README.md
└── README.ko.md
```

## Contributing

Found a way to improve a plugin? Have a new plugin to suggest? PRs and issues welcome!

**Ideas for contributions:**
- Improve existing plugin instructions
- Add new features to existing plugins
- Fix bugs or clarify documentation
- Suggest new plugins (open an issue first to discuss)

**How to contribute:**

1. Fork the repo
2. Create a new branch
3. Make your changes
4. Submit a PR with a clear description

### Plugin Structure

Each plugin follows this structure:

```
plugins/
  plugin-name/
    .claude-plugin/
      plugin.json           # Plugin manifest
    commands/
      setup.md              # /plugin-name:setup
      command.md            # /plugin-name:command
    skills/
      plugin-name/
        SKILL.md            # Natural language skill
    README.md               # Plugin documentation
    README.ko.md            # Korean documentation
```

## Rules for Creating a Remote Skill Repository

When adding a new Skill to a remote repository from Codex, follow these rules.

1. Do not place `SKILL.md` at the repository root. Use one canonical entry point at `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`.
2. Keep only behavior-changing guidance in `SKILL.md`; move detailed procedures, schemas, and source material to `references/`, `scripts/`, or `assets/` when needed.
3. Every public Skill must declare its `name`, `description`, scope, and exclusions. Do not create duplicate triggers or entry points.
4. Each Skill README must document installation in this order: Codex, Claude Code, Hermes Agent, and OpenClaw. It must distinguish native plugins from portable Skills.
5. Do not call an installation path native unless the agent actually supports it. Distinguish shared `npx skills` installation from native plugin installation.
6. A Skill that includes source material must record the source URL, inspected commit or version, and local snapshot scope. A summary is not a substitute for source evidence.
7. Before publishing, run `skill-creator`'s `quick_validate.py` and verify installation for all four agents in temporary directories, including reference-file loading paths.
8. Document installation paths, environment variables, backup behavior, and overwrite behavior. Do not include credentials, tokens, or personal paths in a Skill or README.
9. Determine the public Skill set from `.claude-plugin/marketplace.json` and Git-tracked files. Do not document local untracked directories as publicly available.
10. Keep installation documentation in this order: shared `npx skills`, native Codex, native Claude Code, native Hermes Agent, and native OpenClaw. Do not mark Claude Code as the default recommendation. When a native command is unavailable, document the limitation and manual path instead of inventing a command.
11. Remote Skill CRUD workflows must receive the target repository through a `REMOTE_REPO` variable or input. Never hardcode a personal owner, repository name, or provider path into the Skill.
12. A remote Skill create, update, or delete is incomplete until the canonical Skill directory, registry or manifest, root `README.md`, and root `README.ko.md` are synchronized. Create adds them, update changes them together, and delete removes the corresponding references.
13. Root `README.md` must contain English prose only and root `README.ko.md` Korean prose only. Keep code identifiers, commands, paths, URLs, package names, and proper names unchanged when needed.

## License

MIT - Use these however you want.
