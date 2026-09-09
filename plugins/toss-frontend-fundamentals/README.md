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

### 방법 1: 네 에이전트 공용 Skill 설치 (`npx skills`)

`skills` CLI를 사용하면 원문 스냅샷과 연결된 참조 파일을 포함한 TFF Skill 전체를 네 에이전트에 복사할 수 있습니다. 설치 대상 순서는 Codex, Claude Code, Hermes Agent, OpenClaw입니다.

```bash
npx skills add https://github.com/byungsker/opengiver-skills \
  --skill toss-frontend-fundamentals \
  --agent codex claude-code hermes-agent openclaw \
  --global --copy --yes --full-depth
```

한 런타임에만 설치하려면 `--agent` 값을 `codex`, `claude-code`, `hermes-agent`, `openclaw` 중 하나로 바꾸세요.

기본 설치 경로:

| 에이전트 | 경로 |
|---|---|
| Codex | `~/.agents/skills/toss-frontend-fundamentals` |
| Claude Code | `~/.claude/skills/toss-frontend-fundamentals` |
| Hermes Agent | `~/.hermes/skills/toss-frontend-fundamentals` |
| OpenClaw | `~/.openclaw/skills/toss-frontend-fundamentals` |

### 방법 2: Codex 네이티브 플러그인 설치

Codex 플러그인은 TFF 매니페스트와 원문 참조 스냅샷을 함께 설치합니다.

```bash
codex plugin marketplace add byungsker/opengiver-skills --ref main
codex plugin add toss-frontend-fundamentals@opengiver-skills
```

### 방법 3: Claude Code 네이티브 플러그인 설치

Claude Code 플러그인은 TFF의 Skill과 원문 참조 스냅샷을 함께 설치합니다.

```bash
claude plugin marketplace add byungsker/opengiver-skills
claude plugin install toss-frontend-fundamentals@opengiver-skills
```

### 방법 4: Hermes Agent 네이티브 Skill 설치

Hermes Agent는 `SKILL.md` URL을 직접 설치합니다.

```bash
hermes skills install \
  https://raw.githubusercontent.com/byungsker/opengiver-skills/main/plugins/toss-frontend-fundamentals/skills/toss-frontend-fundamentals/SKILL.md \
  --yes
```

현재 Hermes Agent의 URL 설치는 TFF 진입점 Skill 중심이므로 `references/source/` 원문 스냅샷 전체가 필요하면 방법 1 또는 방법 6을 사용하세요.

### 방법 5: OpenClaw 네이티브 Skill 설치

OpenClaw는 `SKILL.md`가 루트에 있는 로컬 Skill 디렉터리를 설치 대상으로 받습니다. 저장소를 클론한 뒤 TFF 하위 디렉터리를 지정하면 원문 참조 파일도 함께 설치됩니다.

```bash
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 https://github.com/byungsker/opengiver-skills.git "$repo_dir"
openclaw skills install "$repo_dir/plugins/toss-frontend-fundamentals/skills/toss-frontend-fundamentals" \
  --as toss-frontend-fundamentals --global
```

`--global`은 `~/.openclaw/skills/toss-frontend-fundamentals`에 설치합니다. `openclaw skills install`이 없는 구버전은 OpenClaw를 먼저 업데이트하거나 활성 workspace의 `skills/toss-frontend-fundamentals`에 해당 디렉터리를 배치하세요.

### 방법 6: TFF 원문 스냅샷 전체 배치

저장소를 클론한 뒤 플러그인 전용 설치 스크립트를 실행합니다. 이 방법은 TFF의 전체 참조 파일을 각 대상에 배치합니다.

```bash
git clone https://github.com/byungsker/opengiver-skills.git
cd opengiver-skills
./plugins/toss-frontend-fundamentals/install.sh --target all
```

한 대상에만 설치하려면 `--target codex`, `--target claude`, `--target hermes`, `--target openclaw` 중 하나를 사용합니다.

스크립트 전용 기본 경로는 Codex `~/.codex/skills`, Claude Code `~/.claude/skills`, Hermes Agent `~/.hermes/skills`, OpenClaw `~/.openclaw/skills`입니다. `CODEX_HOME`, `CLAUDE_HOME`, `HERMES_HOME`, `OPENCLAW_HOME` 환경 변수로 홈 경로를 바꿀 수 있습니다. 기존 설치는 기본적으로 보존하며, 덮어쓰려면 `--force`를 사용합니다. 이때 기존 디렉터리는 타임스탬프 백업으로 이동합니다.

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
