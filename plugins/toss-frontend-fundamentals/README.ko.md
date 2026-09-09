# Toss Frontend Fundamentals

[영문](README.md) | [한국어](README.ko.md)

| | |
|---|---|
| **이름** | toss-frontend-fundamentals |
| **설명** | React·TypeScript 프론트엔드 코드를 Toss 원문 근거로 검토하는 Skill |
| **버전** | 1.0.0 |
| **출처** | [Toss Frontend Fundamentals](https://github.com/toss/frontend-fundamentals) |

Toss Frontend Fundamentals는 다음 네 가지 코드 품질 관점으로 프론트엔드 코드를 검토하는 원문 기반 Skill입니다.

- 가독성(Readability)
- 예측 가능성(Predictability)
- 응집도(Cohesion)
- 결합도(Coupling)

패키지에는 code-quality 원문 스냅샷, 문서 라우팅 인덱스, 리뷰 루브릭, 관련 참고 Skill이 함께 들어 있습니다. 루브릭은 원문을 대신하지 않으므로, 원문 근거를 사용하는 finding을 만들 때는 연결된 원문 문서를 실제로 읽습니다.

## 설치

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

현재 OpenClaw CLI에는 Skill 설치 하위 명령이 없습니다. 저장소를 클론한 뒤 TFF Skill 디렉터리를 관리되는 전역 Skill 디렉터리에 복사하면 원문 참조 파일도 함께 배치됩니다.

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/toss-frontend-fundamentals"
mkdir -p "$target"
cp -R "$repo_dir/plugins/toss-frontend-fundamentals/skills/toss-frontend-fundamentals/." "$target/"
openclaw skills list
```

관리되는 전역 경로는 `~/.openclaw/skills/toss-frontend-fundamentals`입니다. 작업 공간에만 설치하려면 같은 디렉터리를 해당 작업 공간의 `skills/toss-frontend-fundamentals`에 복사하세요.

### 방법 6: TFF 원문 스냅샷 전체 배치

저장소를 클론한 뒤 플러그인 전용 설치 스크립트를 실행합니다. 이 방법은 TFF의 전체 참조 파일을 각 대상에 배치합니다.

```bash
git clone https://github.com/byungsker/opengiver-skills.git
cd opengiver-skills
./plugins/toss-frontend-fundamentals/install.sh --target all
```

한 대상에만 설치하려면 `--target codex`, `--target claude`, `--target hermes`, `--target openclaw` 중 하나를 사용합니다.

스크립트 전용 기본 경로는 Codex `~/.codex/skills`, Claude Code `~/.claude/skills`, Hermes Agent `~/.hermes/skills`, OpenClaw `~/.openclaw/skills`입니다. `CODEX_HOME`, `CLAUDE_HOME`, `HERMES_HOME`, `OPENCLAW_HOME` 환경 변수로 홈 경로를 바꿀 수 있습니다. 기존 설치는 기본적으로 보존하며, 덮어쓰려면 `--force`를 사용합니다. 이때 기존 디렉터리는 타임스탬프 백업으로 이동합니다.

## 사용 범위

React·TypeScript 코드, diff, 커스텀 Hook, 폼, 기능 디렉터리 구조를 검토할 때 사용합니다. 이 Skill의 범위는 코드 품질이며, 성능·접근성·보안·시각 검토는 사용하는 에이전트의 전문 규칙을 별도로 적용해야 합니다.

원문 라우팅 진입점은 [`skills/toss-frontend-fundamentals/references/source-manifest.md`](skills/toss-frontend-fundamentals/references/source-manifest.md)입니다.

## 패키지 구조

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

원문 스냅샷의 커밋과 범위는 `source-manifest.md`에 고정되어 있습니다. 최신 여부가 중요할 때는 로컬 스냅샷을 최신 사실로 간주하지 말고 원격 저장소를 다시 확인해야 합니다.

## 라이선스

패키지는 저장소의 MIT 라이선스로 배포합니다. 포함된 원문 스냅샷의 원본 라이선스는 `skills/toss-frontend-fundamentals/references/source/LICENSE.md`에 보존되어 있습니다.
