# Toss Frontend Fundamentals

[English](README.md) | [한국어](README.ko.md)

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

### Claude Code 마켓플레이스

```text
/plugin marketplace add byungsker/opengiver-skills
/plugin install toss-frontend-fundamentals@opengiver-skills
```

### Codex CLI 네이티브 설치

Codex CLI에서는 다음 명령으로 Git 마켓플레이스를 등록하고 플러그인을 설치할 수 있습니다.

```bash
codex plugin marketplace add byungsker/opengiver-skills --ref main
codex plugin add toss-frontend-fundamentals@opengiver-skills
```

### Codex·Claude Code·Hermes·OpenClaw 공통 설치

저장소를 클론한 뒤 이식 가능한 설치 스크립트를 실행합니다.

```bash
git clone https://github.com/byungsker/opengiver-skills.git
cd opengiver-skills
./plugins/toss-frontend-fundamentals/install.sh --target codex
```

한 곳에 설치하려면 `--target claude`, `--target hermes`, `--target openclaw`를 사용합니다. 네 곳 모두 설치하려면 `--target all`을 사용합니다.

기본 설치 경로는 다음과 같습니다.

| 대상 | 기본 설치 경로 |
|---|---|
| Codex | `~/.codex/skills/toss-frontend-fundamentals` |
| Claude Code | `~/.claude/skills/toss-frontend-fundamentals` |
| Hermes | `~/.hermes/skills/toss-frontend-fundamentals` |
| OpenClaw | `~/.openclaw/skills/toss-frontend-fundamentals` |

`CODEX_HOME`, `CLAUDE_HOME`, `HERMES_HOME`, `OPENCLAW_HOME` 환경 변수로 각 홈 경로를 바꿀 수 있습니다. 기존 설치는 기본적으로 보존하며, 덮어쓰려면 `--force`를 사용합니다. 이때 기존 디렉터리는 먼저 타임스탬프 백업으로 이동합니다.

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
