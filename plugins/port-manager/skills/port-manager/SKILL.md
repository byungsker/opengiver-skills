---
name: port-manager
description: "macOS 로컬 개발 서버 포트를 조회·종료·교체하거나 명시된 linked worktree를 안전하게 제거합니다. `/port-manger:all`, `/port-manger:detail 5173`, `/port-manger:repo:정확한레포이름`, `/port-manger:delete 5173`, `/port-manger:replace 5173`, `/port-manger:delete:worktree 5173`, `5173 포트랑 워크트리 제거해`, `$port-manager` 요청에 사용합니다."
metadata:
  short-description: "로컬 개발 서버 포트와 linked worktree를 안전하게 관리합니다."
---

# Port Manager

로컬 개발 서버의 포트 점유를 사람이 읽기 쉽게 확인하고, 사용자가 지정한 포트의 확인된 개발 서버만 정상 종료하거나 현재 작업 폴더의 개발 서버로 교체합니다. 사용자가 포트 종료와 연결된 Git linked worktree 삭제를 함께 명시한 경우에만 안전 검사를 거쳐 워크트리를 제거합니다. 실제 프로세스 탐색과 포트 변경에는 이 스킬의 `scripts/port_manager.py`를 사용합니다.

## 사용자 호출 별칭

정식 패키지와 Skill 이름은 `port-manager`입니다. 사용자가 요청한 기본 사용자-facing 호출 표기는 오타 별칭 `port-manger`입니다. 아래 slash 모양 문자열이 일반 메시지로 들어오면 해당 기능 의도로 처리하고, 기존 `$port-manager` 호출도 계속 지원합니다.

- `/port-manger:all`
- `/port-manger:detail 5173`
- `/port-manger:repo:정확한레포이름`
- `/port-manger:delete 5173` — 여러 포트를 함께 지정할 수 있습니다.
- `/port-manger:replace 5173`
- `/port-manger:delete:worktree 5173` — 같은 의도의 자연어 예시는 “5173 포트랑 워크트리 제거해”입니다.
- `$port-manager all`, `$port-manager detail 5173`, `$port-manager repo frontend`, `$port-manager delete 5173`, `$port-manager replace 5173`, `$port-manager delete 5173 --remove-worktree`

이 slash 모양 문자열은 Skill의 요청 의도 별칭입니다. 공식 문서에는 이 colon 형식을 Skill 별칭으로 등록하는 방법이 나오지 않으므로 자동완성 명령이라고 주장하지 않습니다. 입력창이 지원하지 않는 slash 입력을 가로채면 자연어 예시나 `$port-manager` 호출을 사용합니다. Skill을 직접 선택하려면 Codex의 `$` Skill 선택을 사용할 수 있습니다.

`npx skills`로 설치한 Codex 공용 Skill의 CLI 기본 경로는 `~/.agents/skills/port-manager/scripts/port-manager`입니다. Codex 네이티브 플러그인 설치에서는 캐시 경로를 Codex가 관리하므로 Skill을 호출해 사용합니다.

```bash
"$HOME/.agents/skills/port-manager/scripts/port-manager" all
"$HOME/.agents/skills/port-manager/scripts/port-manager" detail 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" repo frontend
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 3000 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 5173 --remove-worktree
"$HOME/.agents/skills/port-manager/scripts/port-manager" replace 4173
```

Codex의 사용자 정의 슬래시 명령은 이 스킬에서 `/port-manager:all` 또는 오타 경로 `/port-manger:all`로 등록하지 않습니다. 설치된 스킬을 `$port-manager`로 선택한 다음 원하는 하위 명령을 말하거나 위 CLI 하위 명령을 실행합니다.

## 조회 절차

1. `all`, `detail`, `repo` 요청에는 각각 `all`, `detail PORT`, `repo REPO_NAME`을 실행하고 표의 분류와 경로를 설명합니다.
2. `all`은 개발 서버로 확실히 분류된 리스너와 그 밖의 전체 TCP LISTEN 리스너를 분리해 표시합니다. 저장소의 런타임 리스너라도 명시적인 개발 서버 명령이 없으면 `개발 서버 후보`로 표시하고 종료 대상에서 제외합니다. DB·시스템 프로세스나 분류 불명 프로세스는 개발 서버라고 추정하지 않습니다.
3. `repo`는 로컬 Git 저장소 루트의 이름과 정확히 일치하는 프로세스만 묶습니다. 같은 이름의 서로 다른 저장소는 전체 경로와 워크트리 경로로 구분합니다.
4. 시작 시각·경과 시간·메모리 사용량은 OS 프로세스 정보에서 얻습니다. 유휴 여부는 애플리케이션 요청 상태를 OS 리스너만으로 알 수 없으므로 `알 수 없음`으로 표시합니다. CPU가 0이거나 연결이 없다는 이유로 유휴라고 단정하지 않습니다.
5. 명령은 민감한 인수값을 출력하지 않도록 제한된 요약으로 표시합니다. 프로세스 환경 변수는 읽거나 출력하지 않습니다.

## 종료와 교체

- `delete PORT...`와 `replace PORT`는 포트 번호만 받습니다. PID를 사용자에게 묻지 않습니다.
- 기본 `delete PORT...`와 `replace PORT`는 워크트리를 제거하지 않습니다. 포트 종료와 워크트리 제거를 함께 요청한 경우에만 `delete PORT... --remove-worktree`를 사용합니다. 예: `$port-manager delete 5173 --remove-worktree` 또는 “5173 포트 내리고 해당 워크트리도 삭제해”.
- 워크트리 제거 전에 포트 소유 프로세스의 PID·시작 시각·cwd·포트 소유자와 Git 워크트리 등록·HEAD·브랜치를 확인합니다. 신호를 보내기 직전과 실제 제거 직전에 등록과 상태를 재검사합니다. 선택하지 않은 포트에서 같은 워크트리의 리스너가 하나라도 실행 중이면 종료하거나 제거하지 않습니다.
- 기본(main) 워크트리, 현재 Codex 실행 디렉터리를 포함하는 워크트리, 잠금·prunable·분리 HEAD 상태, 소속이 모호한 워크트리는 제거하지 않습니다. 수정 파일·미추적 파일·Git이 무시하는 파일이 있으면 보존을 위해 중단합니다. 이 옵션은 일반 `git worktree remove`만 실행하며 강제 삭제나 디렉터리 직접 삭제로 우회하지 않습니다.
- 제거 전 현재 HEAD와 연결 브랜치가 같은 커밋인지 확인하고, 제거 후 브랜치가 같은 커밋을 가리키는지 검증합니다. 브랜치는 삭제하지 않습니다. 서버 종료 뒤 다른 프로세스가 포트를 점유하거나 재검사·일반 제거가 실패하면 서버와 워크트리의 실제 상태를 각각 보고합니다. 여러 포트를 지정하면 모두 같은 Git 저장소에 속해야 합니다.
- PID, 프로세스 시작 시각, 실행 파일 요약, 작업 디렉터리, 계정과 macOS `lsof` 소켓 식별자를 신호 전 다시 확인합니다. IPv4·IPv6의 같은 PID 리스너는 한 프로세스로 묶습니다. 포트 소유자가 바뀌었거나 PID 재사용·소켓 재점유 정황이 있으면 중단합니다.
- 포트에 연결된 모든 고유 프로세스가 현재 계정 소유이고 높은 신뢰도로 개발 서버라고 분류될 때만 `SIGTERM`을 보냅니다. DB·시스템·분류 불명·다른 계정 프로세스는 자동 종료하지 않습니다. 기본 동작은 정상 종료 후 포트 해제를 확인하는 것입니다.
- 정상 종료가 제한 시간 안에 끝나지 않아도 `SIGKILL`로 자동 승격하지 않습니다. 상태를 보고하고, 사용자가 강제 종료를 명시적으로 요청하거나 확인한 뒤에만 `--force`를 추가합니다.
- `replace`는 현재 작업 디렉터리에서 가장 가까운 저장소 내 `package.json`, lockfile, 프레임워크 의존성, `dev` 스크립트(또는 Create React App의 `start`)를 확인합니다. 명령을 결정할 수 없으면 추측하지 않고 필요한 선택을 요청합니다. Vite는 `--strictPort`를 사용하며, 다른 개발 서버도 지정 포트를 실제로 점유하는지 확인합니다.
- 요청 포트를 다른 프로세스가 먼저 차지하면 해당 프로세스를 건드리지 않고 실패합니다. 자동으로 다음 포트를 선택하지 않습니다. 잘못된 포트로 뜬 이번 실행의 새 프로세스 그룹만 정리합니다.
- 새 서버 로그는 디스크에 저장하지 않습니다. stdout과 stderr는 버리고, 관리 메타데이터에는 포트·PID·저장소 경로·패키지 관리자·스크립트 이름·시작 시각만 최소 기록합니다. 메타데이터 파일은 사용자 Codex 홈의 `port-manager/servers` 아래에 제한된 권한으로 저장합니다.
- 종료/교체는 사용자가 해당 포트의 서버를 내리거나 바꾸라고 명시한 경우에만 수행합니다. `all`, `detail`, `repo` 결과와 유휴 추정만으로 종료 권한을 해석하지 않습니다. “그거 내리고 띄워”는 직전 대화에서 포트와 대상 서버가 명확할 때만 실행합니다.
- `replace`의 포트 또는 현재 프로젝트/워크트리가 모호하면 필요한 최소 정보만 묻습니다. 현재 폴더가 의도한 프로젝트라고 추정해 다른 폴더의 서버를 시작하지 않습니다.

## 안전한 실제 검증

회귀 테스트를 실행할 때는 별도 임시 저장소·워크트리와 테스트가 만든 더미 서버만 사용합니다. 기존 사용자 리스너에는 조회 명령만 실행합니다. 테스트 종료 시에도 기록한 더미 PID와 포트가 일치하는지 확인한 뒤 정리합니다.
