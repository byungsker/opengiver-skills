# Toss Frontend Fundamentals

[English](README.md) | [Korean](README.ko.md)

| | |
|---|---|
| **Name** | toss-frontend-fundamentals |
| **Description** | Source-backed code-quality review for React and TypeScript frontend code |
| **Version** | 1.0.0 |
| **Sources** | [Toss Frontend Fundamentals](https://github.com/toss/frontend-fundamentals) |

Toss Frontend Fundamentals is a source-backed skill for reviewing frontend code through four code-quality lenses:

- Readability
- Predictability
- Cohesion
- Coupling

The package includes the code-quality source snapshot, a routing manifest, a review rubric, and the related reference skills. The rubric is not treated as a substitute for the source: agents should load the mapped source document before making a source-backed finding.

## Installation

### Method 1: Install the shared Skill for all agents (`npx skills`)

The `skills` CLI copies the complete TFF Skill, including the source snapshot and linked reference files, to all four agents. The order is Codex, Claude Code, Hermes Agent, and OpenClaw.

```bash
npx skills add https://github.com/byungsker/opengiver-skills \
  --skill toss-frontend-fundamentals \
  --agent codex claude-code hermes-agent openclaw \
  --global --copy --yes --full-depth
```

To install for one runtime, keep only one value after `--agent`: `codex`, `claude-code`, `hermes-agent`, or `openclaw`.

Default installation paths:

| Agent | Path |
|---|---|
| Codex | `~/.agents/skills/toss-frontend-fundamentals` |
| Claude Code | `~/.claude/skills/toss-frontend-fundamentals` |
| Hermes Agent | `~/.hermes/skills/toss-frontend-fundamentals` |
| OpenClaw | `~/.openclaw/skills/toss-frontend-fundamentals` |

### Method 2: Install the native Codex plugin

The Codex plugin installs the TFF manifest and source-reference snapshot together.

```bash
codex plugin marketplace add byungsker/opengiver-skills --ref main
codex plugin add toss-frontend-fundamentals@opengiver-skills
```

### Method 3: Install the native Claude Code plugin

The Claude Code plugin installs the TFF Skill and source-reference snapshot together.

```bash
claude plugin marketplace add byungsker/opengiver-skills
claude plugin install toss-frontend-fundamentals@opengiver-skills
```

### Method 4: Install the native Hermes Agent Skill

Hermes Agent installs a Skill from a direct `SKILL.md` URL.

```bash
hermes skills install \
  https://raw.githubusercontent.com/byungsker/opengiver-skills/main/plugins/toss-frontend-fundamentals/skills/toss-frontend-fundamentals/SKILL.md \
  --yes
```

The current Hermes Agent URL installation is centered on the TFF entry Skill. Use Method 1 or Method 6 when the complete `references/source/` snapshot is required.

### Method 5: Install the native OpenClaw Skill

The current OpenClaw CLI has no Skill install subcommand. Copy the local TFF Skill directory to OpenClaw's managed global Skill directory; its references are copied with it.

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/toss-frontend-fundamentals"
mkdir -p "$target"
cp -R "$repo_dir/plugins/toss-frontend-fundamentals/skills/toss-frontend-fundamentals/." "$target/"
openclaw skills list
```

The managed global directory is `~/.openclaw/skills/toss-frontend-fundamentals`. For a workspace-only installation, copy the same directory to that workspace's `skills/toss-frontend-fundamentals`.

### Method 6: Deploy the complete TFF source snapshot

Clone the repository and run the plugin-specific installer. This places the complete TFF reference files for each selected target.

```bash
git clone https://github.com/byungsker/opengiver-skills.git
cd opengiver-skills
./plugins/toss-frontend-fundamentals/install.sh --target all
```

To target one agent, use one of `--target codex`, `--target claude`, `--target hermes`, or `--target openclaw`.

The installer defaults to Codex `~/.codex/skills`, Claude Code `~/.claude/skills`, Hermes Agent `~/.hermes/skills`, and OpenClaw `~/.openclaw/skills`. Override home paths with `CODEX_HOME`, `CLAUDE_HOME`, `HERMES_HOME`, or `OPENCLAW_HOME`. Existing installations are preserved by default; use `--force` to overwrite, which moves the existing directory to a timestamped backup.

## Usage

Use the skill when reviewing React or TypeScript code, a diff, a custom Hook, a form, or a feature directory structure. It is intentionally limited to code quality. Use the host's frontend, performance, accessibility, security, or visual-review guidance for those concerns.

The source routing entry point is [`skills/toss-frontend-fundamentals/references/source-manifest.md`](skills/toss-frontend-fundamentals/references/source-manifest.md).

## Package layout

```text
toss-frontend-fundamentals/
├── .claude-plugin/plugin.json
├── install.sh
├── README.md
├── README.ko.md
└── skills/toss-frontend-fundamentals/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
        ├── review-rubric.md
        ├── source-manifest.md
        └── source/
```

The source snapshot is pinned in `source-manifest.md`. When freshness matters, verify the upstream repository rather than treating the local snapshot as current.

## License

The package is distributed under the repository's MIT license. The included source snapshot retains the upstream license at `skills/toss-frontend-fundamentals/references/source/LICENSE.md`.
