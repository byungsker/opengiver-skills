
> 상태: 폐기된 계획서. 과거 `blog-material-gen` 스킬을 만들기 위한 문서이며, 현재 저장소의 구현 지침이나 설치 절차로 사용하지 않습니다.

---

## 📋 BYU-289 구현 계획 (최종)

### 🎯 목표
Daily 브랜치(`daily/YYYY-MM-DD`) PR 머지 완료 시점에 **Notion '짧은 글쓰기' 데이터베이스**에 기술 블로그 소재를 자동 생성하는 파이프라인

---

## 🏗️ 아키텍처 설계

### 전체 플로우
```
daily/2026-01-23 브랜치 작업 완료
         ↓
    Agent가 수동으로 스킬 실행 (또는 PR 머지 후 자동)
         ↓
    1. Git 분석 (커밋, PR, diff 수집)
         ↓
    2. 데이터 가공 (코드 마스킹, 트러블슈팅 추출)
         ↓
    3. Notion 페이지 생성 (구조화된 블로그 소재)
         ↓
    완료 보고
```

---

## 📦 구현 컴포넌트

### 1. 프로젝트 구조
```
~/.config/opencode/
├── skills/
│   └── blog-material-gen/
│       ├── SKILL.md                    # 스킬 정의
│       └── scripts/
│           ├── pipeline.ts             # 메인 오케스트레이터
│           ├── git-analyzer.ts         # Git 데이터 수집
│           ├── code-masker.ts          # 코드 마스킹 유틸
│           ├── notion-client.ts        # Notion API 클라이언트
│           └── types.ts                # 타입 정의
├── .env                                # Notion API 키
└── package.json                        # 의존성
```

### 2. 스킬 파일: `SKILL.md`
```yaml
---
name: blog-material-gen
description: Daily 브랜치 작업 내용을 분석하여 Notion '짧은 글쓰기' DB에 블로그 소재를 자동 생성
---

# Blog Material Generator

Daily 브랜치의 모든 하위 feature 브랜치를 분석하고 Notion에 글쓰기 소재를 생성합니다.

## 사용 시점
- Daily 브랜치 → dev PR 머지 완료 후
- 또는 하루 작업 종료 시점

## 실행 방법
1. Daily 브랜치명 확인 (예: `daily/2026-01-23`)
2. 스킬 실행: "daily/2026-01-23 브랜치로 블로그 소재 생성해줘"

## 생성되는 내용
- 브랜치별 주요 변경사항 요약
- 실제 코드 + 예제 코드 (민감 정보 마스킹)
- 트러블슈팅 내역
- 기술 블로그 아이디어 목록

## 필수 환경변수
- `NOTION_API_KEY`: Notion Integration Token
- `NOTION_DATABASE_ID`: '짧은 글쓰기' 데이터베이스 ID
```

---

## 🛠️ 기술 스택 & 의존성

### 필수 패키지
```json
{
  "dependencies": {
    "@notionhq/client": "^2.2.15",
    "simple-git": "^3.25.0",
    "dotenv": "^16.4.5"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "typescript": "^5.3.3",
    "tsx": "^4.7.0"
  }
}
```

### 환경변수 (`.env`)
```bash
NOTION_API_KEY=secret_xxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 📝 핵심 구현 로직

### Component 1: Git 분석기 (`git-analyzer.ts`)

**기능**: Daily 브랜치 하위의 모든 feature 브랜치 정보 수집

```typescript
interface BranchAnalysis {
  branchName: string;           // feature/ENG-123-add-login
  commits: CommitInfo[];        // 커밋 목록
  prInfo?: PRInfo;              // PR 정보 (있다면)
  filesChanged: FileChange[];   // 변경 파일 목록
}

interface CommitInfo {
  hash: string;
  type: string;                 // feat, fix, refactor, etc.
  subject: string;
  body?: string;
  files: string[];
}

interface FileChange {
  path: string;
  additions: number;
  deletions: number;
  diff: string;                 // 실제 diff 내용
}
```

**구현 순서**:
1. `git log --all --grep="Merge pull request.*into daily/YYYY-MM-DD"` → 머지된 feature 브랜치 목록 추출
2. 각 브랜치별 커밋 히스토리 수집
3. `gh pr list --search "head:브랜치명 base:daily/YYYY-MM-DD"` → PR 정보 수집
4. `git diff` → 변경 파일 및 diff 추출

---

### Component 2: 코드 마스킹 유틸 (`code-masker.ts`)

**기능**: 실제 코드에서 민감 정보 제거 + 예제 코드 생성

```typescript
interface CodeBlock {
  language: string;
  realCode: string;       // 실제 코드
  exampleCode: string;    // 마스킹된 예제 코드
  description: string;    // 코드 설명
}

// 마스킹 규칙
const MASKING_RULES = {
  apiKeys: /sk-[a-zA-Z0-9]{48}/g,                    // → 'YOUR_API_KEY'
  tokens: /Bearer\s+[a-zA-Z0-9._-]+/g,               // → 'Bearer YOUR_TOKEN'
  urls: /https?:\/\/api\.myservice\.com/g,           // → 'https://api.example.com'
  specificVariables: /mySpecificBusinessLogic/g,     // → 'businessLogic'
};
```

**구현 순서**:
1. Diff에서 코드 블록 추출 (언어 감지)
2. 정규식 기반 민감 정보 치환
3. 변수명 일반화 (선택적)
4. 실제 코드 + 예제 코드 쌍 생성

---

### Component 3: Notion 클라이언트 (`notion-client.ts`)

**기능**: Notion API를 사용해 '짧은 글쓰기' DB에 페이지 생성

```typescript
import { Client } from '@notionhq/client';

async function createBlogMaterial(data: DailyBranchData) {
  const notion = new Client({ auth: process.env.NOTION_API_KEY });

  const children = buildNotionBlocks(data);

  return await notion.pages.create({
    parent: {
      type: 'database_id',
      database_id: process.env.NOTION_DATABASE_ID!,
    },
    properties: {
      Name: {
        title: [{ text: { content: `[${data.dailyBranch}] 글쓰기 소재` } }],
      },
      Tags: {
        multi_select: data.tags.map(tag => ({ name: tag })),
      },
      Date: {
        date: { start: data.date },
      },
    },
    children,
  });
}
```

**Notion 블록 구조**:
```typescript
function buildNotionBlocks(data: DailyBranchData): BlockObjectRequest[] {
  return [
    // Heading 1: 브랜치 총정리
    heading1('📌 ' + data.dailyBranch + ' 작업 총정리'),
    
    // Paragraph: 간단 요약
    paragraph(data.summary),
    
    // Heading 2: 기술 블로그 소재 목록
    heading2('📝 기술 블로그 소재 목록'),
    ...data.blogIdeas.map(idea => bulletItem(`**${idea.title}**: ${idea.description}`)),
    
    // Heading 2: 브랜치별 상세 재료
    heading2('🔍 브랜치별 상세 재료'),
    ...data.branches.flatMap(branch => [
      heading3(branch.name),
      bulletItem('**요구사항**: ' + branch.requirements),
      bulletItem('**주요 기술**: ' + branch.tech.join(', ')),
      codeBlock(branch.code.exampleCode, 'typescript'),
      bulletItem('**트러블슈팅**: ' + branch.troubleshooting),
    ]),
  ];
}
```

---

### Component 4: 메인 파이프라인 (`pipeline.ts`)

**기능**: 전체 프로세스 오케스트레이션

```typescript
export async function generateBlogMaterial(dailyBranch: string) {
  console.log(`🚀 Starting blog material generation for ${dailyBranch}...`);

  // Step 1: Git 분석
  const branches = await analyzeDailyBranch(dailyBranch);
  console.log(`✅ Analyzed ${branches.length} feature branches`);

  // Step 2: 데이터 가공
  const processedData = await processAnalysisData(branches);
  console.log(`✅ Processed data with ${processedData.blogIdeas.length} blog ideas`);

  // Step 3: Notion 생성
  const notionPage = await createBlogMaterial(processedData);
  console.log(`✅ Created Notion page: ${notionPage.url}`);

  return {
    success: true,
    notionUrl: notionPage.url,
    branchesAnalyzed: branches.length,
    blogIdeasGenerated: processedData.blogIdeas.length,
  };
}
```

---

## 🔄 실행 방식

### Option A: Agent가 수동 실행 (1차 구현)
```
사용자: "어제 작업한 daily/2026-01-23 브랜치로 블로그 소재 생성해줘"
Agent: 스킬 로드 → pipeline.ts 실행 → 결과 보고
```

### Option B: PR 머지 후 자동 실행 (2차 구현, 선택)
- GitHub Actions 워크플로우 추가
- `daily/* → dev` PR 머지 감지
- 워크플로우에서 `tsx scripts/pipeline.ts` 실행

---

## 📋 구현 단계 (Phase별)

### Phase 1: 환경 구축 (1일)
- [ ] `~/.config/opencode/skills/blog-material-gen/` 디렉토리 생성
- [ ] `package.json` 작성 및 의존성 설치 (`bun install`)
- [ ] `.env` 파일 생성 (Notion API 키 설정)
- [ ] Notion Integration 생성 및 '짧은 글쓰기' DB 공유
- [ ] 타입 정의 파일 (`types.ts`) 작성

### Phase 2: Git 분석기 구현 (2-3일)
- [ ] `git-analyzer.ts`: Daily 브랜치 하위 feature 브랜치 목록 추출
- [ ] 각 브랜치의 커밋 히스토리 수집 (`simple-git` 사용)
- [ ] `gh pr list` 연동하여 PR 정보 수집
- [ ] Diff 추출 및 파싱
- [ ] 테스트: 실제 daily 브랜치로 데이터 수집 확인

### Phase 3: 데이터 가공 로직 (2일)
- [ ] `code-masker.ts`: 코드 마스킹 정규식 작성
- [ ] 커밋 타입 분석 (feat/fix/refactor 분류)
- [ ] 트러블슈팅 섹션 추출 (커밋 메시지 + PR 본문)
- [ ] 블로그 소재 아이디어 자동 생성 로직
- [ ] 테스트: 더미 데이터로 가공 로직 검증

### Phase 4: Notion 통합 (2일)
- [ ] `notion-client.ts`: Notion API 클라이언트 구현
- [ ] 블록 생성 헬퍼 함수 (`heading1`, `codeBlock`, `bulletItem` 등)
- [ ] 템플릿 기반 페이지 생성 로직
- [ ] 에러 핸들링 (rate limit, connection error)
- [ ] 테스트: 실제 Notion DB에 테스트 페이지 생성

### Phase 5: 파이프라인 통합 (1일)
- [ ] `pipeline.ts`: 메인 실행 로직 작성
- [ ] CLI 인터페이스 구현 (`tsx scripts/pipeline.ts daily/2026-01-23`)
- [ ] 진행 상황 로깅 추가
- [ ] End-to-End 테스트

### Phase 6: 스킬 등록 (1일)
- [ ] `SKILL.md` 작성 (agent 실행 가이드)
- [ ] `opencode.json`에 스킬 권한 설정
- [ ] Agent 테스트: 실제 대화로 스킬 실행
- [ ] 문서화 (README.md)

### Phase 7: 자동화 (선택, 1-2일)
- [ ] GitHub Actions 워크플로우 작성 (`.github/workflows/blog-material.yml`)
- [ ] PR 머지 이벤트 트리거 설정
- [ ] 환경변수 GitHub Secrets 등록
- [ ] 워크플로우 테스트

---

## 🧪 테스트 전략

### 단위 테스트
- `git-analyzer.test.ts`: 브랜치 목록 추출, 커밋 파싱
- `code-masker.test.ts`: 마스킹 정규식 검증
- `notion-client.test.ts`: 블록 생성 로직

### 통합 테스트
- 실제 daily 브랜치로 전체 파이프라인 실행
- Notion에 생성된 페이지 수동 검증

### 엣지 케이스
- PR 정보 없는 브랜치 처리
- 커밋이 0개인 브랜치
- Diff가 너무 큰 경우 (truncate)
- Notion API rate limit 처리

---

## ⚠️ 고려사항 & 해결 방안

| 이슈 | 해결 방안 |
|------|----------|
| **Notion API Rate Limit (3 req/sec)** | 요청 간 300ms 딜레이, 배치 처리 |
| **민감 정보 노출 위험** | 화이트리스트 기반 마스킹, 수동 검토 단계 추가 |
| **PR 정보 없는 직접 커밋 브랜치** | 커밋 메시지로 대체 또는 스킵 |
| **너무 많은 브랜치 (10개 이상)** | 최근 N개로 제한 옵션 또는 전체 처리 |
| **세션 로그 접근** | OpenCode SDK `session.read()` 활용 (선택) |
| **코드 블록 너무 큼** | 핵심 부분만 추출 또는 링크로 대체 |

---

## 📐 템플릿 구조 (Notion 페이지)

```
📌 [daily/2026-01-23] 작업 총정리

오늘은 사용자 인증 기능과 프로필 페이지를 구현했습니다. 
총 3개의 feature 브랜치가 머지되었고, 2건의 트러블슈팅이 있었습니다.

---

📝 기술 블로그 소재 목록

• **Next.js에서 JWT 기반 인증 구현하기**: middleware.ts를 활용한 토큰 검증
• **Supabase RLS 정책 디버깅 팁**: 403 에러 해결 과정
• **TypeScript 제네릭으로 타입 안전한 API 클라이언트 만들기**: 실전 예제

---

🔍 브랜치별 상세 재료

### feature/ENG-123-add-jwt-auth

**요구사항**
- 사용자 로그인 시 JWT 토큰 발급
- 토큰 검증 middleware 구현
- 만료된 토큰 자동 갱신

**주요 기술 & 로직**
- Next.js middleware
- jose 라이브러리 (JWT 서명/검증)
- Cookie 기반 토큰 저장

**코드 예제**
```typescript
// middleware.ts
export async function middleware(req: NextRequest) {
  const token = req.cookies.get('auth-token');
  const { payload } = await jwtVerify(token, SECRET);
  // ...
}
```

**트러블슈팅**
- 문제: middleware에서 Supabase client 초기화 시 "Cannot use import statement outside a module" 에러
- 원인: Edge Runtime 환경에서 일부 모듈 미지원
- 해결: jose 라이브러리로 변경, token 검증만 middleware에서 처리

**배운 점**
- Next.js Edge Runtime의 제약사항
- JWT 토큰 갱신 전략 (sliding session)

**초안 포스트 아이디어**
"Next.js 14에서 JWT 인증 구현하기: Edge Runtime 환경에서의 제약과 해결법"

---

### feature/ENG-124-profile-page

...
```

---

## 🎯 성공 기준

- [ ] Daily 브랜치 하나당 Notion 페이지 1개 생성
- [ ] 모든 하위 feature 브랜치 정보 포함
- [ ] 코드 블록이 실제 코드 + 예제 코드 쌍으로 존재
- [ ] 트러블슈팅 섹션이 명확히 구분됨
- [ ] 실행 시간 5분 이내 (브랜치 10개 기준)
- [ ] Agent가 스킬을 통해 실행 가능

---

## 📊 예상 산출물

### 1. 실행 가능한 스킬
```bash
# Agent 대화
User: "daily/2026-01-23 브랜치로 블로그 소재 생성해줘"
Agent: [blog-material-gen 스킬 로드] → 파이프라인 실행 → Notion 페이지 생성 완료
```

### 2. Notion 페이지
- URL: `https://notion.so/짧은-글쓰기-xxxxx`
- 제목: `[daily/2026-01-23] 작업 총정리`
- 태그: `#Next.js`, `#Auth`, `#Troubleshooting`
- 내용: 브랜치별 상세 재료 (코드, 트러블슈팅, 배운 점)

### 3. 재사용 가능한 스크립트
```bash
# CLI로도 실행 가능
bun run tsx ~/.config/opencode/skills/blog-material-gen/scripts/pipeline.ts daily/2026-01-23
```

---

이 계획으로 진행할까요? 수정하거나 추가할 부분이 있나요?
