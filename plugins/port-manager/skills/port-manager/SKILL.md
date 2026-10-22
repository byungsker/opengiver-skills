---
name: port-manager
description: "로컬 프런트엔드 개발 서버의 TCP 포트, 프로젝트와 Git 워크트리, 프로세스 시작 시각을 macOS에서 조회·종료·교체할 때 사용합니다."
metadata:
  short-description: "로컬 개발 서버 포트를 안전하게 조회하고 교체합니다."
---

# Port Manager

로컬 개발 서버의 포트 점유를 사람이 읽기 쉽게 확인하고, 사용자가 지정한 포트의 확인된 개발 서버만 정상 종료하거나 현재 작업 폴더의 개발 서버로 교체합니다. 실제 프로세스 탐색과 포트 변경에는 이 스킬의 `scripts/port_manager.py`를 사용합니다.

## 실행 방법

Codex에서 `$port-manager all`, `$port-manager detail 5173`, `$port-manager repo frontend`, `$port-manager delete 3000 5173`, `$port-manager replace 4173`처럼 호출하거나 자연어로 요청합니다. `/port-manager:all` 슬래시 명령은 등록하지 않습니다. `port-manger`는 오타 별칭으로 이해하되 정식 이름은 `port-manager`입니다.

CLI 헬퍼는 이 Skill 패키지의 `scripts/port-manager` 및 `scripts/port_manager.py`에 포함되어 있습니다. Codex 공용 Skill을 `npx skills`로 설치했을 때 기본 직접 실행 경로는 다음과 같습니다.

```bash
"$HOME/.agents/skills/port-manager/scripts/port-manager" all
"$HOME/.agents/skills/port-manager/scripts/port-manager" detail 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" repo frontend
"$HOME/.agents/skills/port-manager/scripts/port-manager" delete 3000 5173
"$HOME/.agents/skills/port-manager/scripts/port-manager" replace 4173
```

Codex 네이티브 플러그인의 캐시 경로는 Codex가 관리합니다. 이 경우 Codex에서 Skill을 호출하거나 로드된 Skill 패키지의 `scripts/` 경로를 사용합니다.

## 조회 절차

1. `all`, `detail`, `repo` 요청에는 각각 `all`, `detail PORT`, `repo REPO_NAME`을 실행하고 표의 분류와 경로를 설명합니다.
2. `all`은 개발 서버로 확실히 분류된 리스너와 그 밖의 전체 TCP LISTEN 리스너를 분리해 표시합니다. 저장소의 런타임 리스너라도 명시적인 개발 서버 명령이 없으면 `개발 서버 후보`로 표시하고 종료 대상에서 제외합니다. DB·시스템 프로세스나 분류 불명 프로세스는 개발 서버라고 추정하지 않습니다.
3. `repo`는 로컬 Git 저장소 루트의 이름과 정확히 일치하는 프로세스만 묶습니다. 같은 이름의 서로 다른 저장소는 전체 경로와 워크트리 경로로 구분합니다.
4. 시작 시각·경과 시간·메모리 사용량은 OS 프로세스 정보에서 얻습니다. 유휴 여부는 애플리케이션 요청 상태를 OS 리스너만으로 알 수 없으므로 `알 수 없음`으로 표시합니다. CPU가 0이거나 연결이 없다는 이유로 유휴라고 단정하지 않습니다.
5. 명령은 민감한 인수값을 출력하지 않도록 제한된 요약으로 표시합니다. 프로세스 환경 변수는 읽거나 출력하지 않습니다.

## 종료와 교체

- `delete PORT...`와 `replace PORT`는 포트 번호만 받습니다. PID를 사용자에게 묻지 않습니다.
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
