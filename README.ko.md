# Opengiver Skills

[영문](README.md) | [한국어](README.ko.md)

Opengiver Skills는 좋은 작업 방식, 좋은 지식, 좋은 도구를 잘 다듬어 누구에게나 건네는 저장소입니다. 한 사람이 배운 것이 그 사람에게서 멈추지 않고, 다음 사람이 사용하고 개선하고 다시 건넬 수 있게 만듭니다.

이 저장소의 Skill은 큰 프롬프트가 아니라, 행동을 바꾸는 지침과 필요한 근거를 함께 담은 작은 작업 체계입니다. `SKILL.md`의 의미는 에이전트가 달라도 유지하고, Codex·Claude Code·Hermes Agent·OpenClaw에서는 각자의 설치·발견·실행 방식에 맞춰 전달합니다.

**기여를 환영합니다!** 플러그인 개선 아이디어가 있거나 새 플러그인을 추가하고 싶으시면 [PR을 보내주세요](#기여하기).

## Opengiver의 철학: 좋은 것을 잘 다듬어, 다시 건넨다

Opengiver는 좋은 것이 그것을 발견한 사람에게서 멈추면 안 된다고 믿습니다. 더 나은 작업 방식, 오래 남을 지식, 누군가의 수고를 줄이는 도구는 혼자 갖고 있을 때보다 다른 사람이 이해하고 사용할 수 있을 때 더 큰 가치를 만듭니다.

하지만 Opengiver는 무조건 퍼주는 저장소가 아닙니다. 좋은 것을 실제로 쓸 수 있도록 다듬어 건네고, 받은 사람이 다시 고치고 확장해 다음 사람에게 건넬 수 있는 상태를 만듭니다. Skill은 한 번 작동하는 것으로 끝나지 않습니다. 다른 사람이 이해하고, 적용하고, 개선하고, 다음 Giver가 될 수 있을 때 완성됩니다.

- **쓸 수 있는 것을 건넵니다:** 경험을 원래 맥락 밖에서도 사용할 수 있는 지침·도구·참조 자료로 다듬습니다.
- **의존을 만들지 않습니다:** 원래 만든 사람에게 다시 묻지 않아도 이어갈 수 있도록 이유와 경계를 함께 설명합니다.
- **다음 Giver를 만듭니다:** 모든 기여를 다른 사람이 고치고 확장하고 다시 공유하기 쉽게 만듭니다.
- **문을 열어둡니다:** 도움을 받는 사람, 더 나은 방식으로 개선하는 사람, 새로운 것을 나누는 사람을 모두 환영합니다.

## 플러그인이란?

플러그인은 Skill의 의미를 바꾸는 별도 규칙이 아니라, 같은 Skill을 특정 에이전트에서 발견·설치·호출할 수 있게 포장하는 배포 형식입니다. 이 저장소에서는 Skill이 핵심 작업 원칙을 맡고, 플러그인은 명령어·매니페스트·워크플로우·런타임별 통합을 맡습니다. 따라서 플러그인 없이 Skill 자체를 설치할 수도 있고, 필요한 경우 사용하는 에이전트의 네이티브 방식을 선택할 수도 있습니다.

## 사용 가능한 플러그인

| 플러그인 | 버전 | 설명 | 명령어 |
|----------|------|------|--------|
| [linear-simple](plugins/linear-simple) | `1.1.6` | 이슈 관리를 위한 Linear GraphQL API | `/linear-simple:setup`, `/linear-simple:get`, `/linear-simple:create` |
| [git-worktree](plugins/git-worktree) | `1.0.0` | 격리된 작업 공간으로 안전한 병렬 개발을 위한 Git 워크트리 프로토콜 | Skill 전용 (명령어 없음) |
| [db-safety](plugins/db-safety) | `1.0.0` | 실수로 인한 데이터 손실을 방지하는 데이터베이스 안전 프로토콜 | Skill 전용 (명령어 없음) |
| [toss-frontend-fundamentals](plugins/toss-frontend-fundamentals) | `1.0.0` | React·TypeScript 코드를 Toss 원문 근거로 검토하는 Skill | Skill 전용 (명령어 없음) |

## 설치

### 방법 1: 네 에이전트 공용 Skill 설치 (`npx skills`)

아래 명령은 이식 가능한 `SKILL.md`와 연결된 참조 파일을 네 에이전트의 사용자 Skill 디렉터리에 복사합니다. 설치 대상 순서는 항상 Codex, Claude Code, Hermes Agent, OpenClaw입니다. 플러그인 명령이나 마켓플레이스 기능은 포함되지 않습니다.

```bash
for skill in linear-simple db-safety git-worktree toss-frontend-fundamentals; do
  npx skills add https://github.com/byungsker/opengiver-skills \
    --skill "$skill" \
    --agent codex claude-code hermes-agent openclaw \
    --global --copy --yes --full-depth
done
```

특정 에이전트 하나에만 설치하려면 `--agent` 뒤에 하나만 남깁니다.

```bash
npx skills add https://github.com/byungsker/opengiver-skills \
  --skill toss-frontend-fundamentals \
  --agent codex --global --copy --yes --full-depth
```

기본 설치 대상은 다음과 같습니다.

| 에이전트 | `--agent` 값 | 기본 경로 |
|---|---|---|
| Codex | `codex` | `~/.agents/skills/<skill>` |
| Claude Code | `claude-code` | `~/.claude/skills/<skill>` |
| Hermes Agent | `hermes-agent` | `~/.hermes/skills/<skill>` |
| OpenClaw | `openclaw` | `~/.openclaw/skills/<skill>` |

위 표는 현재 `npx skills`가 표시하는 공용 설치 경로입니다. Codex 네이티브 플러그인은 플러그인 설정과 캐시를 사용하며, TFF의 별도 `install.sh --target codex`는 `CODEX_HOME` 또는 `~/.codex/skills`를 사용합니다.

### 방법 2: Codex 네이티브 플러그인 설치

```bash
codex plugin marketplace add byungsker/opengiver-skills --ref main
for plugin in linear-simple db-safety git-worktree toss-frontend-fundamentals; do
  codex plugin add "$plugin@opengiver-skills"
done
```

플러그인 설치 후 새 Codex 세션에서 Skill을 사용합니다. Codex 플러그인은 이식 가능한 Skill과 달리 플러그인 매니페스트와 연결된 구성요소를 함께 설치합니다.

### 방법 3: Claude Code 네이티브 플러그인 설치

```bash
claude plugin marketplace add byungsker/opengiver-skills
for plugin in linear-simple db-safety git-worktree toss-frontend-fundamentals; do
  claude plugin install "$plugin@opengiver-skills"
done
```

슬래시 명령이 있는 플러그인은 이 방식으로 설치해야 합니다. 예를 들어 `linear-simple`은 `/linear-simple:setup`을 제공합니다.

### 방법 4: Hermes Agent 네이티브 Skill 설치

Hermes Agent의 Skill 설치 명령은 `SKILL.md` URL을 직접 받습니다.

```bash
for skill in linear-simple db-safety git-worktree toss-frontend-fundamentals; do
  hermes skills install \
    "https://raw.githubusercontent.com/byungsker/opengiver-skills/main/plugins/$skill/skills/$skill/SKILL.md" \
    --yes
done
```

이 방식은 Hermes Agent 네이티브 설치입니다. 참조 파일이 많은 Skill은 전체 디렉터리를 보존하는 방법 1을 우선 사용하세요.

### 방법 5: OpenClaw 네이티브 Skill 설치

OpenClaw는 `SKILL.md`가 루트에 있는 로컬 Skill 디렉터리를 설치 대상으로 받습니다. 이 저장소는 여러 Skill을 담고 있으므로 저장소를 클론한 뒤 각 Skill 하위 디렉터리를 지정합니다.

```bash
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 https://github.com/byungsker/opengiver-skills.git "$repo_dir"
for skill in linear-simple db-safety git-worktree toss-frontend-fundamentals; do
  openclaw skills install "$repo_dir/plugins/$skill/skills/$skill" \
    --as "$skill" --global
done
```

`--global`은 `~/.openclaw/skills`에 설치합니다. `openclaw skills install`이 없는 구버전은 OpenClaw를 먼저 업데이트하거나, 활성 작업 공간의 `skills/<skill>`에 동일한 Skill 디렉터리를 배치하세요.

### 선택 사항: Claude Code UI 또는 저장소 클론

Claude Code에서 `/plugin`을 실행한 뒤 `Marketplaces` 탭에서 `byungsker/opengiver-skills`를 추가하고 `Discover` 탭에서 플러그인을 설치할 수도 있습니다. 전체 저장소를 직접 내려받으려면 다음을 사용합니다.

```bash
git clone https://github.com/byungsker/opengiver-skills.git
cp -r opengiver-skills/plugins/* ~/.claude/plugins/
```

## 플러그인 상세

### linear-simple

MCP 없이 Linear GraphQL API를 직접 호출하여 토큰 효율성을 50-70% 향상.

**기능:**
- 이슈 CRUD (생성, 조회, 수정, 삭제)
- 댓글 관리
- 상태 업데이트
- PR + Linear 동기화

**설정:**
```bash
/linear-simple:setup
```

[전체 문서 보기 →](plugins/linear-simple/README.ko.md)

### git-worktree

격리된 작업 공간으로 안전한 병렬 개발을 위한 Git 워크트리 프로토콜.

**기능:**
- 각 기능/수정 브랜치별 격리된 워크트리 디렉토리
- .env 파일 및 시크릿 자동 관리
- `wt` CLI를 통한 개발 서버 관리
- 모바일 개발을 위한 Flutter 워크트리 전환기 (`wtf`)
- 공유 빌드 캐시를 통한 디스크 최적화
- PR 머지 후 자동 정리

**트리거:**
```
"워크트리"
"wt"
"구현 시작"
"작업 시작"
"병렬 개발"
"기능 브랜치"
```

[전체 문서 보기 →](plugins/git-worktree/README.ko.md)

---

### db-safety

실수로 인한 데이터 손실을 방지하고 안전한 마이그레이션을 강제하는 데이터베이스 안전 프로토콜.

**기능:**
- 위험한 작업 차단 (DROP, ALTER, DELETE, TRUNCATE)
- 안전한 SQL 쿼리 가이드 (안전/위험 패턴)
- 안전한 마이그레이션 패턴 (3단계 삭제, Expand-Contract)
- 위험 수준 분류 (LOW, MEDIUM, HIGH, CRITICAL)
- 환경 분리 (개발 DB와 운영 DB)
- 마이그레이션 실패 시 롤백 절차

**트리거:**
```
"DROP TABLE"
"ALTER COLUMN"
"DELETE FROM"
"마이그레이션"
"SQL"
"위험한 작업"
```

[전체 문서 보기 →](plugins/db-safety/README.ko.md)

---

### toss-frontend-fundamentals

가독성, 예측 가능성, 응집도, 결합도 기준으로 React·TypeScript 프론트엔드 코드를 검토합니다. 요약만 제공하는 것이 아니라 대응되는 Toss 원문 문서를 함께 포함하므로, 발견 사항을 만들기 전에 관련 원문을 실제로 읽을 수 있습니다.

네 에이전트 공용 설치는 위의 방법 1을 사용합니다. TFF는 원문 스냅샷이 포함되어 있으므로 Codex·Claude Code 네이티브 플러그인은 원문 참조까지 함께 설치합니다. Hermes Agent의 URL 설치는 진입점 Skill을 설치하므로 전체 원문 스냅샷이 필요하면 방법 1을 사용하세요.

```bash
git clone https://github.com/byungsker/opengiver-skills.git
cd opengiver-skills
./plugins/toss-frontend-fundamentals/install.sh --target all
```

저장소를 클론한 뒤 TFF의 전체 파일을 한 번에 배치하려면 `--target all`을 사용합니다. 한 에이전트에만 설치하려면 `--target codex`, `--target claude`, `--target hermes`, `--target openclaw` 중 하나를 사용합니다.

## 저장소 구조

```
opengiver-skills/
├── .claude-plugin/
│   └── marketplace.json          # 마켓플레이스 레지스트리
├── plugins/
│   ├── linear-simple/            # Linear API 플러그인
│   │   ├── .claude-plugin/
│   │   ├── commands/
│   │   ├── skills/
│   │   └── README.md
│   ├── git-worktree/             # Git 워크트리 프로토콜 플러그인
│   │   ├── .claude-plugin/
│   │   ├── skills/
│   │   └── README.md
│   ├── db-safety/                # 데이터베이스 안전 프로토콜 플러그인
│   │   ├── .claude-plugin/
│   │   ├── skills/
│   │   └── README.md
│   └── toss-frontend-fundamentals/ # Toss 원문 기반 프론트엔드 코드 품질 검토
│       ├── .claude-plugin/
│       ├── install.sh
│       ├── skills/
│       └── README.md
├── README.md
└── README.ko.md
```

## 기여하기

플러그인 개선 방법을 찾으셨나요? 새 플러그인을 제안하고 싶으신가요? PR과 이슈를 환영합니다!

**기여 아이디어:**
- 기존 플러그인 설명 개선
- 기존 플러그인에 새 기능 추가
- 버그 수정 또는 문서 명확화
- 새 플러그인 제안 (먼저 이슈로 논의)

**기여 방법:**

1. 레포 포크
2. 새 브랜치 생성
3. 변경 사항 작성
4. 명확한 설명과 함께 PR 제출

### 플러그인 구조

각 플러그인은 다음 구조를 따릅니다:

```
plugins/
  plugin-name/
    .claude-plugin/
      plugin.json           # 플러그인 매니페스트
    commands/
      setup.md              # /plugin-name:setup
      command.md            # /plugin-name:command
    skills/
      plugin-name/
        SKILL.md            # 자연어 스킬
    README.md               # 플러그인 문서
    README.ko.md            # 한글 문서
```

## 원격 Skill 저장소 생성 규칙

Codex에서 새 Skill을 원격 저장소에 추가할 때는 다음 규칙을 지킵니다.

1. 저장소 루트에 `SKILL.md`를 두지 않습니다. 정식 진입점은 `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` 하나로 둡니다.
2. `SKILL.md`에는 실제 작업을 바꾸는 지침만 작성하고, 상세 절차·스키마·원문은 필요한 경우 `references/`, `scripts/`, `assets/`로 분리합니다.
3. 모든 공개 Skill은 `name`, `description`, 적용 범위와 제외 범위를 갖고, 중복되는 트리거·진입점을 만들지 않습니다.
4. 각 Skill의 README에는 Codex·Claude Code·Hermes Agent·OpenClaw 순서로 설치 명령과 기본 설치 경로를 적고, 네이티브 플러그인과 이식 가능한 Skill의 차이를 명시합니다.
5. 지원을 확인하지 않은 에이전트에 대해 “네이티브 설치”라고 쓰지 않습니다. 공용 `npx skills` 설치와 실제 네이티브 플러그인 설치를 구분합니다.
6. 원문을 포함하는 Skill은 출처 URL, 확인한 커밋 또는 버전, 로컬 스냅샷 범위를 기록하고, 요약만으로 원문 근거를 대신하지 않습니다.
7. 공개 전에 `skill-creator`의 `quick_validate.py`를 실행하고, 임시 디렉터리에서 네 에이전트 대상 설치 결과와 참조 파일 로딩 경로를 확인합니다.
8. 설치 경로·환경 변수·백업·덮어쓰기 동작을 문서화하며, 자격 증명·토큰·개인 경로를 Skill과 README에 포함하지 않습니다.
9. 공개 Skill의 범위는 `.claude-plugin/marketplace.json`과 Git에 추적되는 파일로 판단하며, 로컬 미추적 디렉터리를 공개 목록에 포함된 것처럼 문서화하지 않습니다.
10. 설치 문서의 순서는 항상 `npx skills` 공용 설치, Codex 네이티브, Claude Code 네이티브, Hermes Agent 네이티브, OpenClaw 네이티브로 고정합니다. Claude Code를 기본 권장으로 표시하지 않으며, 네이티브 명령이 없는 버전은 지원 한계와 수동 경로를 함께 적고 명령을 추측하지 않습니다.
11. 원격 Skill CRUD 작업은 대상 저장소를 `REMOTE_REPO` 변수나 입력으로 받게 합니다. 특정 개인의 소유자·저장소 이름·제공자 경로를 Skill에 하드코딩하지 않습니다.
12. 원격 Skill의 생성·수정·삭제는 canonical Skill 디렉터리, 레지스트리 또는 매니페스트, 루트 `README.md`, 루트 `README.ko.md`를 함께 동기화해야 완료된 것으로 봅니다. 생성은 모두 추가하고, 수정은 함께 갱신하며, 삭제는 대응하는 참조를 제거합니다.
13. 루트 `README.md`의 설명 문장은 영어만 사용하고, 루트 `README.ko.md`의 설명 문장은 한국어만 사용합니다. 필요한 경우 코드 식별자·명령어·경로·URL·패키지 이름·고유명사는 원문을 유지할 수 있습니다.

## 라이선스

MIT - 자유롭게 사용하세요.
