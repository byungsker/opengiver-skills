# Port Manager 로컬 Skill 호출표

정식 패키지·Skill 이름은 `port-manager`이고, 사용자가 요청한 기본 호출 별칭은 오타 철자 `port-manger`입니다. 기존 `$port-manager` 호출도 계속 지원합니다.

아래 slash 형식은 Codex에 보내는 요청 의도 표기입니다. 실제 slash 자동완성 등록을 뜻하지 않습니다. Codex가 지원하지 않는 slash 명령으로 처리하면 자연어 예시나 `$port-manager`를 사용하세요.

| 기능 | 요청한 스킬 커맨드 | 자연어 예시 | 동작과 주의사항 |
|---|---|---|---|
| 전체 포트 조회 | `/port-manger:all` | “로컬 개발 서버 포트 전부 표로 보여줘.” | 읽기 전용. 개발 서버와 그 밖의 TCP LISTEN을 구분하며, DB·시스템 서비스는 개발 서버로 단정하지 않습니다. |
| 포트 상세 조회 | `/port-manger:detail 5173` | “5173 포트 상세 정보 보여줘.” | 지정 포트의 PID, 시작 시각, 명령 요약, 프로젝트·워크트리 경로를 조회합니다. 종료하지 않습니다. |
| 저장소별 조회 | `/port-manger:repo:정확한레포이름` | “frontend 저장소에서 사용하는 포트를 워크트리별로 보여줘.” | 저장소 루트 이름이 정확히 일치하는 모든 워크트리를 묶고, 동명이인 경로는 구분합니다. |
| 서버 종료 | `/port-manger:delete 5173`<br>`/port-manger:delete 3000 5173` | “5173 포트 내려.”<br>“3000과 5173 포트 내려.” | 지정된 개발 서버만 PID·시작 시각·포트 소유자를 재확인 후 정상 종료합니다. 기본 동작은 강제 종료가 아닙니다. 워크트리는 남습니다. |
| 현재 프로젝트 서버 교체 | `/port-manger:replace 5173` | “현재 프로젝트 서버를 5173 포트로 띄워.” | 현재 프로젝트의 package manifest·lockfile·프레임워크를 확인하고 요청 포트를 고정합니다. 프로젝트가 모호하거나 다른 프로세스가 먼저 점유하면 중단합니다. |
| 서버 종료와 linked worktree 제거 | `/port-manger:delete:worktree 5173` | “5173 포트랑 워크트리 제거해.” | 명시적 요청일 때만 종료 후 linked worktree 제거를 시도합니다. main·현재·잠금·분리 HEAD·dirty·untracked·ignored·소속 불명은 보호하고, 같은 워크트리의 다른 서버가 있으면 중단합니다. 브랜치는 보존합니다. |

## 내부 CLI

CLI는 Skill이 동작을 수행하는 내부 헬퍼입니다. 직접 실행할 때 기본 local Codex 경로는 다음과 같습니다.

```bash
"$HOME/.agents/skills/port-manager/scripts/port-manager" all
"$HOME/.agents/skills/port-manager/scripts/port-manager" detail 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" repo frontend
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 3000 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" replace 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 5173 --remove-worktree
```

`--remove-worktree`를 넣지 않은 일반 `delete`와 `replace`는 어떤 워크트리도 제거하지 않습니다. CLI 경로의 `delete PORT... --remove-worktree`가 `/port-manger:delete:worktree PORT...` 요청의 내부 실행 방식입니다.
