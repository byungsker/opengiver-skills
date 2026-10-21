---
name: biome-eslint-ide-config-apply
description: 저장소에 이미 설정된 Biome·ESLint 자동 수정 규칙을 전체 대상 코드에 적용한다. 전체 일괄 적용을 명시적으로 요청하거나 이 스킬을 호출할 때 사용한다.
---

# Biome·ESLint 전체 코드 일괄 적용

현재 저장소에 설정된 Biome·ESLint 자동 수정 규칙을 적용 대상 소스 전체에 실행한다. 설정을 새로 만들거나 기존 규칙을 임의로 바꾸지 않는다.

## 호출 방법

- 사용하는 에이전트의 Skill 호출 기능에서 `biome-eslint-ide-config-apply`를 선택한다.
- 자연어 트리거: “이 저장소 전체에 import/Tailwind 자동 수정해”, “Biome·ESLint 전체 코드 일괄 적용해”, “전체 코드 린트 포맷 규칙 적용해”.
- 설정 방법이나 진단 설명만 묻는 요청에는 이 스킬을 실행하지 않는다. 규칙 설정 요청은 `biome-eslint-ide-config-skill`을 사용한다.

## 적용 절차

1. 저장소 루트와 적용되는 `AGENTS.md`를 읽고, package manager, Biome·ESLint 버전과 설정, 관련 명령을 확인한다. `git status --short --branch`로 시작 상태도 기록한다. 기존 변경을 되돌리거나 숨기지 않는다.
2. Biome과 ESLint에서 자동 수정이 활성화된 규칙과 각 파일 범위를 확인한다. 둘 중 한 도구에 설정이 없으면 그 도구는 건너뛰고 적용할 수 있는 나머지 설정만 실행한다. 두 도구 모두 요청한 자동 수정이 설정되어 있지 않으면 새 설정을 만들지 말고 `biome-eslint-ide-config-skill` 사용 방법을 보고한다.
3. 저장소의 ignore와 각 도구의 include/exclude 설정을 적용해 대상 파일을 정한다. `node_modules`, 생성 산출물, vendored 파일, 빌드 결과, 도구가 무시하는 파일은 제외한다. 사용자 변경이 있는 대상 파일도 요청 범위에 포함되므로, 시작 시 dirty 파일을 확인하고 결과에서 별도로 구분한다.
4. 프로젝트가 제공하는 일괄 autofix 명령의 실제 범위를 확인한다. 사용자가 전체 규칙을 요청했으면 설정된 모든 Biome·ESLint 자동 수정 규칙을 실행하고, import 정렬만 요청했으면 필요한 기능만 실행하도록 도구 CLI 옵션과 설치 버전을 확인한다. 예를 들어 import 정렬만 적용할 때 Biome formatter와 linter를 끄고 organize-imports를 실행한다.

   ```sh
   biome check --formatter-enabled=false --linter-enabled=false --organize-imports-enabled=true --write .
   ```

   전체 규칙 적용은 프로젝트 설정에 활성화된 autofix 동작을 포함한다. ESLint는 적용 대상 전체에 `eslint . --fix`와 동등한 프로젝트 명령을 사용할 수 있다. 사용자가 import 정렬과 Tailwind 규칙만 요청했으면 다른 formatter나 ESLint autofix가 함께 적용되지 않게 범위를 좁힌다.

5. 도구가 순차 실행되어도 결과가 되돌려지지 않는지 확인한다. Biome import 정렬과 ESLint class 수정이 서로 다른 코드를 다루는지 확인하고, 같은 파일을 두 formatter가 다시 포맷하는 충돌이 있으면 원인을 해결한 뒤 진행한다.
6. 전체 적용 후 동일 범위를 쓰기 없이 다시 검사한다. Biome 검사, ESLint 검사, `git diff --check`를 실행한다. 자동 수정이 남아 있거나 새 진단이 생기면 반복 실행으로 감추지 말고 원인과 남은 파일을 보고한다.
7. 최종 diff에서 의도한 import 정렬과 Tailwind class 변경인지 확인한다. 파일 전체 재포맷, 의미가 불분명한 class 변경, 생성 파일 변경이 섞이면 관련 부분을 사용자의 기존 변경을 보존하며 원인 확인한다. 광범위한 수정은 되돌리지 말고 확인 전 작업을 멈춘다.

## 완료 보고

변경 파일 수와 경로, 바뀐 규칙, 시작 전부터 dirty였던 파일과 이번 적용에서 추가 변경된 파일, 실행한 정확한 명령, 쓰기 없는 재검사 결과를 한글로 보고한다. 파일을 stage, commit, push하지 않는다.
