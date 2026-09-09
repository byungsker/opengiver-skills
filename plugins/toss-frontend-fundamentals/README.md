# Toss Frontend Fundamentals

[English](README.md) | [한국어](README.ko.md)

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

### Claude Code marketplace

```text
/plugin marketplace add lbo728/opengiver-skills
/plugin install toss-frontend-fundamentals@opengiver-skills
```

### Codex, Claude Code, Hermes, or OpenClaw

Clone the repository and run the portable installer:

```bash
git clone https://github.com/lbo728/opengiver-skills.git
cd opengiver-skills
./plugins/toss-frontend-fundamentals/install.sh --target codex
```

Use `--target claude`, `--target hermes`, or `--target openclaw` for one target. Use `--target all` to install into all four user-level skill directories.

The installer uses these default locations:

| Target | Default destination |
|---|---|
| Codex | `~/.codex/skills/toss-frontend-fundamentals` |
| Claude Code | `~/.claude/skills/toss-frontend-fundamentals` |
| Hermes | `~/.hermes/skills/toss-frontend-fundamentals` |
| OpenClaw | `~/.openclaw/skills/toss-frontend-fundamentals` |

Override a home directory with `CODEX_HOME`, `CLAUDE_HOME`, `HERMES_HOME`, or `OPENCLAW_HOME`. Existing installations are preserved unless `--force` is supplied; `--force` moves the old directory to a timestamped backup first.

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
