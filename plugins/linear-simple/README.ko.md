# Linear Simple

[영문](README.md) | [한국어](README.ko.md)

| | |
|---|---|
| **이름** | linear-simple |
| **설명** | Linear GraphQL API 스킬 - MCP 없이 curl로 직접 호출하여 토큰 효율성 향상 |
| **버전** | 1.1.6 |
| **트리거** | "Linear 이슈", "BYU-125", "이슈 확인", "이슈 생성" |

---

Claude Code용 Linear GraphQL API 플러그인. MCP 없이 curl로 직접 호출하여 토큰 효율성을 50-70% 향상시킵니다.

## 기능

- **이슈 생성**: 제목, 설명, 우선순위 설정
- **이슈 조회**: 식별자로 조회 (예: BYU-125)
- **이슈 업데이트**: 상태 변경 (진행중, 완료 등)
- **댓글 추가**: 이슈에 댓글 달기
- **PR 업데이트**: PR 생성 + 댓글 + 상태 변경을 한 번에
- **계층형 설정**: User 레벨 API 키 + 프로젝트 레벨 팀/프로젝트 설정

## 설치

### 방법 1: 네 에이전트 공용 Skill 설치 (`npx skills`)

portable `SKILL.md`를 네 에이전트에 복사합니다. 설치 대상 순서는 Codex, Claude Code, Hermes Agent, OpenClaw입니다.

```bash
npx skills add https://github.com/byungsker/opengiver-skills \
  --skill linear-simple \
  --agent codex claude-code hermes-agent openclaw \
  --global --copy --yes --full-depth
```

기본 설치 경로:

| 에이전트 | 경로 |
|---|---|
| Codex | `~/.agents/skills/linear-simple` |
| Claude Code | `~/.claude/skills/linear-simple` |
| Hermes Agent | `~/.hermes/skills/linear-simple` |
| OpenClaw | `~/.openclaw/skills/linear-simple` |

`--agent`에는 하나의 값만 지정할 수도 있습니다. 공용 설치는 Skill 본문을 설치하며, `/linear-simple:*` 슬래시 명령은 Claude Code 네이티브 플러그인 설치에서 제공합니다.

### 방법 2: Codex 네이티브 플러그인 설치

```bash
codex plugin marketplace add byungsker/opengiver-skills --ref main
codex plugin add linear-simple@opengiver-skills
```

### 방법 3: Claude Code 네이티브 플러그인 설치

```bash
claude plugin marketplace add byungsker/opengiver-skills
claude plugin install linear-simple@opengiver-skills
```

### 방법 4: Hermes Agent 네이티브 Skill 설치

```bash
hermes skills install \
  https://raw.githubusercontent.com/byungsker/opengiver-skills/main/plugins/linear-simple/skills/linear-simple/SKILL.md \
  --yes
```

### 방법 5: OpenClaw 네이티브 Skill 설치

```bash
REMOTE_REPO="${REMOTE_REPO:-https://github.com/byungsker/opengiver-skills}"
repo_dir="$(mktemp -d)/opengiver-skills"
git clone --depth 1 "$REMOTE_REPO.git" "$repo_dir"
target="$HOME/.openclaw/skills/linear-simple"
mkdir -p "$target"
cp -R "$repo_dir/plugins/linear-simple/skills/linear-simple/." "$target/"
openclaw skills list
```

현재 OpenClaw CLI에는 Skill 설치 하위 명령이 없으므로 위 명령은 관리되는 전역 Skill 디렉터리에 복사합니다. 작업 공간에만 설치하려면 같은 디렉터리를 해당 작업 공간의 `skills/linear-simple`에 복사하세요.

### 선택 사항: Claude Code UI 또는 저장소 클론

Claude Code에서 `/plugin`을 실행한 뒤 마켓플레이스에 `byungsker/opengiver-skills`를 추가하고 `linear-simple`을 설치할 수도 있습니다. 전체 플러그인 디렉터리를 직접 복사하려면 다음을 사용합니다.

```bash
git clone https://github.com/byungsker/opengiver-skills.git
cp -r opengiver-skills/plugins/linear-simple ~/.claude/plugins/
```

## 설정 (필수)

설치 후 Linear API를 설정하세요:

```bash
/linear-simple:setup
```

Claude가 자동으로:
1. Linear API 키를 요청합니다 (Linear 설정 > API에서 발급)
2. API 키를 `~/.config/linear-simple/config.json`에 저장합니다
3. "이 워크스페이스에 Linear 팀/프로젝트를 설정할까요?" (Yes/No)
   - **Yes** → 팀/프로젝트 선택 → `.claude/linear-simple.json`에 저장 (`.gitignore`에 추가됨)
   - **No** → user config의 기본 팀 사용

팀원과 워크스페이스 설정을 공유하려면 `.gitignore`에서 `.claude/linear-simple.json`을 제거하세요.

## 설정 파일

### 계층형 설정 구조

| 레벨 | 위치 | 내용 |
|------|------|------|
| User | `~/.config/linear-simple/config.json` | API 키, 기본 팀 |
| Project | `.claude/linear-simple.json` | 팀, 프로젝트 (워크스페이스별) |

### User Config (`~/.config/linear-simple/config.json`)
```json
{
  "api_key": "lin_api_xxxxx",
  "default_team_id": "uuid",
  "default_team_key": "BYU",
  "default_team_name": "팀 이름"
}
```

### Project Config (`.claude/linear-simple.json`)
```json
{
  "team_id": "uuid",
  "team_key": "BYU",
  "team_name": "팀 이름",
  "project_id": "uuid",
  "project_name": "Bookgolas"
}
```

**로딩 우선순위:**
1. 프로젝트 config (있으면) → 팀/프로젝트 정보
2. User config → API 키 + fallback 팀

## 사용법

### 슬래시 명령어
```bash
/linear-simple:setup                        # API 및 프로젝트 설정
/linear-simple:get BYU-125                  # 이슈 상세 조회
/linear-simple:list                         # 최근 이슈 목록 (개수 물어봄)
/linear-simple:list 10                      # 최근 10개 이슈 목록
/linear-simple:create "API 버그 수정"        # 새 이슈 생성
/linear-simple:status BYU-125 "In Progress" # 상태 변경
/linear-simple:comment BYU-125 "완료!"       # 댓글 추가
/linear-simple:pr-update                    # PR + 댓글 + 상태 업데이트
```

### 자연어

**이슈 조회**
```
"BYU-125 이슈를 읽고 구현 계획을 세워줘"
"BYU-125 내용이 뭐야? 요구사항 파악해야해"
"BYU-125 상세 보여줘"
```

**이슈 목록**
```
"최근 10개 이슈 보여줘"
"지금 진행중인 이슈들 뭐 있어?"
"백로그 이슈 리스트 보여줘"
```

**이슈 생성**
```
"이슈 생성해줘"
→ 에이전트: "어떤 제목과 설명으로 만들까요?"
→ 사용자: "제목: [Product] 결제 플로우 구현
          설명: (제목에 맞게 적당히 작성해줘)"

"방금 얘기한 로그인 버그 이슈로 만들어줘"
"이슈 추가해: API 속도 제한 구현"
```

**상태 변경**
```
"BYU-125 상태를 진행중으로 바꿔"
"BYU-125 완료 처리해줘"
"BYU-125 리뷰중으로 변경해"
```

**댓글 추가**
```
"PR 만들고, 이 작업 이슈에 코멘트 달아줘"
→ 에이전트가 컨텍스트에서 이슈 번호 확인 후 PR 생성, PR 내용을 코멘트로 등록

"BYU-125에 '구현 시작' 코멘트 달아"
"BYU-125에 오늘 진행 상황 메모해줘"
```

**PR + 업데이트 (통합)**
```
"PR 생성하고 Linear 이슈도 업데이트해"
→ 에이전트: PR 생성 → PR 링크를 코멘트로 추가 → 상태를 "In Review"로 변경

"이 PR 푸시하고 Linear랑 동기화해줘"
"작업 마무리해줘 - PR 만들고 이슈는 리뷰중으로"
```

## 토큰 효율성: MCP vs Skill

| 방식 | 토큰 (10회 작업) |
|------|------------------|
| MCP | ~570,000 토큰 |
| Skill | ~520,000 토큰 |
| **절감** | **~50,000 토큰 (9%)** |

긴 대화에서는 효율성이 크게 증가합니다 (최대 99% 절감).

## 플러그인 구조

```
linear-simple/
├── .claude-plugin/
│   └── plugin.json           # 플러그인 매니페스트
├── commands/
│   ├── setup.md              # /linear-simple:setup
│   ├── get.md                # /linear-simple:get
│   ├── list.md               # /linear-simple:list
│   ├── create.md             # /linear-simple:create
│   ├── status.md             # /linear-simple:status
│   ├── comment.md            # /linear-simple:comment
│   └── pr-update.md          # /linear-simple:pr-update
├── skills/
│   └── linear-simple/
│       ├── SKILL.md          # 자연어 스킬
│       └── references/
│           └── graphql-patterns.md
├── README.md
└── README.ko.md
```

## 라이선스

MIT
