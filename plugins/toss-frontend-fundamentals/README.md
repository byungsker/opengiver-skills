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
/plugin marketplace add byungsker/opengiver-skills
/plugin install toss-frontend-fundamentals@opengiver-skills
```

### 네 런타임 한 번에 설치

`skills` CLI를 사용하면 원문 근거 레퍼런스를 포함한 TFF Skill 전체를 Claude Code·Codex·Hermes Agent·OpenClaw에 한 번에 복사할 수 있습니다.

```bash
npx skills add https://github.com/byungsker/opengiver-skills --skill toss-frontend-fundamentals --agent claude-code codex hermes-agent openclaw --global --copy --yes --full-depth
```

한 런타임에만 설치하려면 `--agent` 값을 `claude-code`, `codex`, `hermes-agent`, `openclaw` 중 하나로 바꾸세요.

### Claude Code CLI 네이티브 설치

Claude Code 자체의 플러그인 CLI를 사용하려면 다음 한 줄을 실행합니다.

```bash
claude plugin marketplace add byungsker/opengiver-skills && claude plugin install toss-frontend-fundamentals@opengiver-skills
```

### Codex CLI 네이티브 설치

Codex CLI에서는 다음 명령으로 Git 마켓플레이스를 등록하고 플러그인을 설치할 수 있습니다.

```bash
codex plugin marketplace add byungsker/opengiver-skills --ref main
codex plugin add toss-frontend-fundamentals@opengiver-skills
```

### Codex, Claude Code, Hermes, or OpenClaw

Clone the repository and run the portable installer:

```bash
git clone https://github.com/byungsker/opengiver-skills.git
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
