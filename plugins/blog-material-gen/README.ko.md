# Blog Material Generator

[English](README.md) | [한국어](README.ko.md)

| | |
|---|---|
| **이름** | blog-material-gen |
| **설명** | Daily Git 브랜치에서 Notion으로 블로그 소재 자동 생성 (Slack 알림 지원) |
| **버전** | 1.0.0 |
| **트리거** | "블로그 소재", "daily 브랜치 분석", "글쓰기 소재 생성" |

---

Daily Git 브랜치를 자동 분석하여 Notion 데이터베이스에 블로그 소재를 생성하는 Claude Code 플러그인.

## 기능

- Git 브랜치/커밋 분석 → 블로그 아이디어 자동 추출
- 날짜 기반 Notion 페이지 생성
- 같은 날짜 다른 워크스페이스 → 기존 페이지에 `[워크스페이스명]` 태그로 추가
- 민감 정보 자동 마스킹 (API 키, 토큰, 비밀번호 등)
- Slack 알림 (선택)
- **LLM 기반 블로그 초안 생성** - OpenAI, Anthropic, Google Gemini를 사용한 AI 블로그 초안 자동 생성 (선택사항)
- **PR 및 커밋 링크** - Notion 출력에 GitHub URL 자동 생성으로 쉬운 탐색

## 설치

### 방법 1: 마켓플레이스 (권장)

```bash
# 1단계: 마켓플레이스 추가
/plugin marketplace add byungsker/opengiver-skills

# 2단계: 플러그인 설치
/plugin install blog-material-gen@opengiver-skills

# 3단계: Claude Code 재시작
```

### 방법 2: UI로 설치

```bash
# 플러그인 매니저 열기
/plugin

# "Marketplaces" 탭 → Add → 입력: byungsker/opengiver-skills
# "Discover" 탭으로 이동 → "blog-material-gen" 찾기 → Install
```

## 설정

### 1. Notion Integration 생성

1. [Notion Integrations](https://www.notion.so/my-integrations) 페이지 방문
2. "New integration" 클릭
3. 이름 입력 (예: "Blog Material Gen")
4. Associated workspace 선택
5. "Submit" → API Key 복사 (`secret_xxx...`)

### 2. Notion Database 연결

1. Notion에서 대상 데이터베이스 열기
2. 우측 상단 `...` → "Connections" → "Connect to" → 생성한 Integration 선택
3. Database ID 확인 (URL에서 추출):
   ```
   https://notion.so/myworkspace/abc123def456...?v=...
                               ^^^^^^^^^^^^^^^^
                               이 부분이 Database ID
   ```

### 3. 설정 명령어 실행

```bash
/blog-material-gen:setup
```

Agent가 다음 정보를 순서대로 요청합니다:

| 항목 | 필수 | 설명 |
|------|------|------|
| Notion API Key | O | `secret_` 로 시작하는 키 |
| Database ID | O | 32자리 hex 문자열 |
| Slack Webhook URL | X | 알림 받을 채널의 Webhook URL |
| LLM Provider | X | 블로그 초안 생성을 위한 OpenAI, Anthropic, Google Gemini |

설정은 `~/.config/blog-material-gen/config.json`에 저장됩니다.

## Slack 알림 설정 (선택)

### Webhook URL 생성

1. [Slack API](https://api.slack.com/apps) → "Create New App" → "From scratch"
2. App 이름 입력, Workspace 선택
3. "Incoming Webhooks" → "Activate Incoming Webhooks" ON
4. "Add New Webhook to Workspace" → 채널 선택 → "Allow"
5. Webhook URL 복사 (`https://hooks.slack.com/services/...`)

### 알림 내용

파이프라인 성공 시 다음 정보가 Slack으로 전송됩니다:

- 날짜
- 워크스페이스명
- 분석된 브랜치 수
- 생성된 블로그 아이디어 수
- Notion 페이지 링크 버튼

## LLM Provider (선택사항)

플러그인은 자동 블로그 초안 생성을 위해 3가지 LLM provider를 지원합니다. 필요에 따라 선택하세요:

### 지원 Provider

| Provider | 모델 | 무료 티어 | API Key URL |
|----------|------|-----------|-------------|
| **OpenAI** | gpt-4o-mini, gpt-4o | 없음 | [API Key 발급](https://platform.openai.com/api-keys) |
| **Anthropic** | Claude 3.5 Haiku, Sonnet, Opus | 없음 | [API Key 발급](https://console.anthropic.com/settings/keys) |
| **Google Gemini** | gemini-1.5-flash, gemini-1.5-pro | 있음 (분당 15회, 일일 1500회) | [API Key 발급](https://aistudio.google.com/app/apikey) |

### 추천

**Google Gemini Flash**를 대부분의 사용자에게 추천합니다:
- 넉넉한 무료 티어
- 빠른 응답 속도
- 좋은 품질의 블로그 초안

### 설정

LLM provider는 setup 중 설정하거나 (`/blog-material-gen:setup`) 나중에 `/blog-material-gen:change-llm`으로 변경할 수 있습니다.

**Config 형식**:
```json
{
  "api_key": "secret_xxx",
  "database_id": "abc123",
  "llm": {
    "provider": "google",
    "api_key": "AIza...",
    "model": "gemini-1.5-flash"
  }
}
```

### LLM 비활성화

LLM 기능을 비활성화하려면 config.json에서 `llm` 객체를 제거하거나 `/blog-material-gen:change-llm`에서 "비활성화"를 선택하세요.

## 사용법

### 자동 실행 (권장)

AGENTS.md에 Blog Material Generation Protocol이 포함되어 있으면, daily → dev PR 머지 완료 시 Agent가 자동으로 실행합니다.

### 수동 실행

```bash
/blog-material-gen
```

또는 특정 브랜치 지정:

```
"daily/2026-01-24 브랜치 분석해줘"
"블로그 소재 생성해줘"
```

## 출력 결과

### Notion 페이지 구조

```
📝 2026-01-24 글쓰기 소재

## 오늘의 요약
오늘은 3개의 feature 브랜치에서 15개의 커밋을 통해...

## 블로그 아이디어
1. TypeScript에서 JWT 인증 구현하기
2. React Query로 서버 상태 관리 최적화

## [opengiver-skills] 작업 상세
### feature/add-auth
- 요구사항: 사용자 인증 기능 추가
- 기술: TypeScript, React
- 코드 예제: ...
- 트러블슈팅: ...
- 배운 점: ...

## [another-project] 작업 상세  ← 같은 날짜 다른 워크스페이스
### feature/update-ui
...
```

## 플러그인 구조

```
blog-material-gen/
├── .claude-plugin/
│   └── plugin.json           # 플러그인 매니페스트
├── commands/
│   ├── setup.md              # /blog-material-gen:setup
│   └── change-llm.md         # /blog-material-gen:change-llm
├── skills/
│   └── blog-material-gen/
│       └── SKILL.md          # 자연어 스킬
├── scripts/
│   ├── types.ts              # 타입 정의
│   ├── git-analyzer.ts       # Git 분석
│   ├── code-masker.ts        # 민감 정보 마스킹
│   ├── notion-client.ts      # Notion API 클라이언트
│   ├── llm-client.ts         # LLM provider factory
│   ├── providers/            # LLM provider 구현체
│   │   ├── openai.ts
│   │   ├── anthropic.ts
│   │   └── google.ts
│   └── pipeline.ts           # 메인 파이프라인
├── package.json              # 의존성
├── README.md
└── README.ko.md
```

## 문제 해결

### "설정이 완료되지 않았습니다"

```bash
/blog-material-gen:setup
```

### "Failed to connect to Notion"

1. API Key가 `secret_` 로 시작하는지 확인
2. Database에 Integration이 연결되었는지 확인
3. Database ID가 정확한지 확인

### Slack 알림이 안 옴

1. Webhook URL이 `https://hooks.slack.com/services/` 로 시작하는지 확인
2. Slack App이 해당 채널에 접근 권한이 있는지 확인

### LLM 초안 생성이 작동하지 않음

1. config.json에 LLM 설정이 있는지 확인
2. 선택한 provider의 API key가 유효한지 확인
3. 콘솔에서 provider별 에러 메시지 확인
4. `/blog-material-gen:change-llm`으로 다른 provider로 전환 시도

**Provider별 확인사항**:
- **OpenAI**: API key가 `sk-`로 시작하는지 확인
- **Anthropic**: API key가 `sk-ant-`로 시작하는지 확인
- **Google**: API key가 `AIza`로 시작하는지 확인

## 라이선스

MIT
