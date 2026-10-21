---
name: biome-eslint-ide-config-skill
description: "프로젝트별 Biome import 정렬, ESLint Tailwind 클래스 줄바꿈·표준 클래스 검사, Zed·VS Code 저장 자동화를 설정한다. 설정된 규칙의 전체 적용을 요청할 때도 사용한다."
---

# Biome·ESLint·IDE 저장 설정

프로젝트의 기존 도구 설정을 읽고 Biome import 정렬, ESLint Tailwind CSS 줄바꿈·표준 클래스 검사, Zed·VS Code 저장 시 자동 실행을 구성한다. 설정 파일은 기존 항목을 보존하면서 병합하고, 요청된 저장소 범위만 변경한다. 설정 완료 후 동의하거나 나중에 전체 적용을 자연어로 요청하면 같은 스킬의 일괄 적용 절차를 사용한다.

## 대상 저장소 확인

1. 저장소 루트와 적용되는 `AGENTS.md`를 읽고, `git status --short --branch`로 작업 트리 변경을 확인한다. 기존 변경은 보존한다.
2. 루트 및 관련 workspace의 `package.json`, lockfile, `biome.json`·`biome.jsonc`, ESLint 설정, formatter 설정, `.zed/settings.json`, `.vscode/settings.json`, `.gitignore`를 확인한다.
3. 모노레포라면 workspace 패키지 이름을 확인한다. 앱 별칭은 `tsconfig`·`jsconfig`와 bundler 설정에서 읽고, FSD는 실제 소스 레이어와 공개 API를 보고 판정한다. 이름만 보고 계층을 추측하지 않는다.
4. Tailwind 사용 여부와 실제 CSS 진입점을 확인한다. 기존 ESLint·Biome 버전, 설정 형식, package manager를 유지한다. 새 의존성을 추가할 때는 설치된 도구와 호환되는 공식 버전을 확인하고 lockfile을 함께 갱신한다.

## 규칙 선택 질문

설정을 쓰기 전에 현재 설정과 아래 기본안을 짧게 요약해 사용자에게 확인한다. 기존 설정이 있으면 기본안을 그대로 적용한다고 가정하지 말고, 무엇을 유지하거나 바꾸는지 차이를 보여준다. import 묶음 순서, Tailwind 줄바꿈 값, 지원되는 경우 표준 클래스 검사 활성화 여부를 답변을 받은 뒤 확정한다. 답을 기다리는 동안 파일 조사, 호환성 확인, 편집기 설정 병합 계획처럼 선택과 무관한 작업은 진행할 수 있다.

### Import 정렬 기본안

프로젝트의 실제 패키지명, 별칭, FSD 레이어 이름으로 아래 순서를 구체화해 제시한다.

1. 외부 패키지: 프레임워크, 라이브러리, Node.js 내장 모듈 등
2. 모노레포 내부 workspace 패키지: 프로젝트에 있을 때만 포함
3. 소스 루트 별칭: FSD면 `app → pages → widgets → features → entities → shared` 순서. 실제 프로젝트가 단수형 등 다른 이름을 쓰면 해당 경로를 대응시킨다. FSD가 아니면 확인한 별칭과 프로젝트 구조를 제시한다.
4. 상위 상대 경로: 현재 파일에서 더 먼 경로부터 가까운 경로 순서
5. 같은 디렉터리 상대 경로: `./` 경로

각 그룹 사이에는 빈 줄 하나를 둔다. 그룹 안에서는 import 출처를 현재 모듈 기준 거리 순으로 정렬하고, 거리가 같으면 Biome의 자연 정렬을 사용한다. 사용자에게 이 순서를 그대로 쓸지, 그룹을 추가·삭제·이동할지 물어본다. 스타일 import, side-effect import, type-only import를 별도 그룹으로 두는 등 추가 규칙이 필요한지도 함께 묻는다.

Biome은 사용자 설정의 그룹 순서를 적용하고 기본적으로 출처의 거리를 반영해 정렬한다. 상대 경로 깊이별로 각각 빈 줄을 강제하려면 관찰된 깊이에 대한 구체적인 matcher가 필요할 수 있다. 무한한 깊이를 지원한다고 가정하지 말고, 현재 저장소에서 나타나는 깊이를 반영한 설정으로 임시 fixture를 정렬해 검증한다. matcher가 적용되지 않으면 이를 보고하고, Biome이 지원하는 부모 경로 묶음과 `./` 묶음으로 대안을 제시한다. Biome 공식 문서: [organizeImports](https://biomejs.dev/assist/actions/organize-imports/javascript/).

### Tailwind 줄바꿈 기본안

Tailwind가 확인될 때 현재 ESLint 설정과 아래 기본값을 보여주고, 유지할지 조정할지 묻는다.

- 규칙: `better-tailwindcss/enforce-consistent-line-wrapping`
- 기본값: `classesPerLine: 4`, `group: "never"`, `printWidth: 0`, `preferSingleLine: true`
- 새로 규칙을 추가할 때 severity 기본값은 `warn`; 기존 프로젝트의 severity 정책이 있으면 그 기준을 따른다.

조정 요청이 있으면 해당 필드의 목표값을 확인한다. Tailwind가 없으면 플러그인을 설치하거나 Tailwind 설정을 만들지 않고 해당 부분을 건너뛴다. 플러그인이 없을 때는 프로젝트 package manager로 개발 의존성을 추가하고, 기존 flat 또는 legacy ESLint 설정에 연결한다. Tailwind 진입점과 작업 디렉터리는 실제 파일을 확인해 지정한다. 플러그인 설정은 [공식 규칙 문서](https://github.com/schoero/eslint-plugin-better-tailwindcss/blob/main/docs/rules/enforce-consistent-line-wrapping.md)를 따른다.

### Tailwind 표준 클래스 검사 기본안

Tailwind CSS 버전이 `4.1.15` 이상이면 `better-tailwindcss/enforce-canonical-classes`를 추가 기본안으로 제시하고 사용 여부를 묻는다. 기본 severity는 `warn`이며, 이 규칙은 `bg-gradient-to-r`를 `bg-linear-to-r`처럼 Tailwind가 제안하는 표준 클래스로 고치고 자동 수정할 수 있다. 공식 문서: [enforce-canonical-classes](https://github.com/schoero/eslint-plugin-better-tailwindcss/blob/main/docs/rules/enforce-canonical-classes.md).

- Tailwind 버전이 지원 범위보다 낮거나 판별되지 않으면 이 규칙을 설정하지 않고 이유를 알린다.
- 플러그인의 `recommended` 설정이 이 규칙을 이미 활성화하면 중복 선언하지 않는다. 이 규칙이 활성화되면 규칙이 포괄하는 `enforce-shorthand-classes`, `enforce-consistent-important-position`, `enforce-consistent-variable-syntax`의 중복 진단을 피한다.
- VS Code에서 이 규칙을 활성화하면 같은 진단을 중복 표시하지 않도록 `.vscode/settings.json`에 `"tailwindCSS.lint.suggestCanonicalClasses": "ignore"`를 병합한다. Zed 설정은 지원 여부를 공식 설정에서 확인하기 전까지 추측해 추가하지 않는다.
- 이 규칙은 Tailwind 내부 제안을 따르므로 Tailwind 버전에 따라 수정 결과가 달라질 수 있다. 버전 변경 후 대표 class를 다시 확인한다.

## 설정 적용

1. 사용자가 선택한 순서를 기존 `biome.json`에 병합한다. `assist.actions.source.organizeImports.level`과 `options.groups`를 설정하고, 빈 줄이 필요한 경계마다 `:BLANK_LINE:`을 둔다. 모노레포 workspace 패키지와 일반 외부 패키지가 같은 scope를 공유하면 외부 패키지 matcher에서 workspace 패턴을 제외한다. 전체 설정을 덮어쓰지 않는다.
2. Biome이 없으면 저장소의 package manager와 현재 설정에 맞춰 개발 의존성을 추가하고, schema URL과 설치 버전을 맞춘다. 이미 설치되어 있으면 기존 버전을 유지한다.
3. Tailwind 규칙은 현재 ESLint 설정에 중복 없이 병합한다. Tailwind CSS 진입점과 파일 glob을 앱 구조에 맞춘다. 다른 ESLint 규칙이나 전체 포맷 정책은 요청 없이 바꾸지 않는다.
4. `.zed/settings.json`과 `.vscode/settings.json`이 있으면 기존 언어별 formatter·저장 동작을 보존하고 필요한 code action만 병합한다. 파일이 없으면 프로젝트 범위 파일을 만든다. 사용자 전역 설정은 수정하지 않는다.
   - Zed에서 Biome import 정렬은 `source.organizeImports.biome`, ESLint 자동 수정은 `source.fixAll.eslint`로 연결한다. JS·TS·TSX 등 실제 대상 언어에 `format_on_save`와 `code_actions_on_format`을 설정한다.
   - VS Code에서는 `editor.codeActionsOnSave`에 Biome import 정렬과 ESLint 수정 action을 추가한다. 현재 VS Code 설정 형식에 맞는 `"explicit"` 값을 우선 사용한다. Tailwind만 저장 시 수정하도록 `eslint.codeActionsOnSave.rules`를 제한한다.
   - 기존 Prettier·Biome·ESLint formatter가 서로 수정 결과를 되돌릴 수 있는지 확인한다. 저장 action과 formatter를 함께 사용할 때는 실제 실행 순서와 결과를 검증한다. 포매터를 끄거나 교체하지 말고, 충돌이 있으면 사용자 선택을 구한다.
   - 설정 문법은 설치된 도구 버전의 [Zed JavaScript 문서](https://zed.dev/docs/languages/javascript), [VS Code 저장 시 code action 문서](https://code.visualstudio.com/docs/editing/codebasics#_code-actions-on-save), [VS Code ESLint 확장 문서](https://github.com/microsoft/vscode-eslint)를 확인한다.
5. `.gitignore`와 `git check-ignore -v`를 확인해 프로젝트 설정 파일이 ignore되는지 판정한다. 프로젝트 `.gitignore`가 `.zed` 또는 `.vscode`를 무시하면 `settings.json`만 추적 가능하게 예외를 추가하고 나머지 디렉터리 내용은 기존 무시 정책대로 유지한다. 전역 ignore와 기존 파일의 로컬 설정은 구분해서 설명한다. 다른 ignore 정책은 변경하지 않는다.
6. 기존 package script를 덮어쓰지 않는다. 동등한 명령이 없고 프로젝트 관례상 필요하면 scoped script를 추가한다. 의존성, lockfile, 도구 설정, editor JSON을 각각 해당 parser나 CLI로 확인한다.

## 초기 설정 후 전체 코드 일괄 적용

설정 파일 병합과 대표 파일 검증을 마친 뒤에는 전체 파일 autofix를 즉시 실행하지 않는다. 변경한 규칙과 적용 대상 glob을 요약하고 사용자에게 다음처럼 묻는다.

> 설정을 완료했고 대표 파일 확인을 마쳤습니다. 현재 설정된 import 정렬과 Tailwind 자동 수정 규칙을 전체 대상 파일에 적용할까요?

- 사용자가 적용한다고 답하면 아래 `전체 코드 일괄 적용` 절차를 같은 저장소와 대화에서 이어서 실행한다. 해당 대화의 답변이 적용 승인이므로 다시 묻지 않는다.
- 사용자가 거절하거나 답하지 않으면 전체 파일을 수정하지 않는다. 요청을 기다리는 동안 추가 파일 수정도 하지 않는다.
- 일부 경로만 원하면 답변에 지정된 범위로 제한한다.

## 전체 코드 일괄 적용

이미 설정된 Biome import 정렬과 ESLint Tailwind 자동 수정 규칙을 대상 소스 전체에 적용한다. 이 절차는 설정을 새로 만들거나 기존 규칙을 임의로 바꾸지 않는다. 전체 적용 명령을 사용자가 실행했거나 초기 설정 후 사용자가 적용을 승인했을 때 시작한다.

1. 저장소 루트와 적용되는 `AGENTS.md`, package manager, Biome·ESLint 버전과 설정, 관련 package script를 확인한다. `git status --short --branch`로 시작 상태를 기록하고 기존 변경을 보존한다.
2. Biome과 ESLint에서 이 스킬이 구성한 규칙과 파일 범위를 확인한다. 설정되지 않은 도구는 건너뛴다. 두 도구 모두 규칙이 없으면 설정을 만들지 말고 먼저 이 스킬의 설정 절차를 안내한다.
3. 도구 설정과 ignore 규칙을 적용해 대상 파일을 정한다. `node_modules`, 생성 산출물, vendored 파일, 빌드 결과, 도구가 무시하는 파일은 제외한다. 사용자 변경이 있는 대상 파일도 요청 범위에 포함되므로 시작 상태와 최종 diff에서 구분한다.
4. 프로젝트 package script의 실제 범위를 확인한 뒤 Biome import 정렬과 설정된 Tailwind 자동 수정 규칙을 적용한다. import 정렬만 실행할 때는 설치된 Biome이 지원하는 옵션을 확인하고 formatter·linter를 끈 뒤 실행한다. 예:

   ```sh
   biome check --formatter-enabled=false --linter-enabled=false --organize-imports-enabled=true --write .
   ```

   ESLint는 실제 설정에 등록된 Tailwind 규칙과 대상 glob에 한정한다. 사용자가 요청하지 않은 Biome formatter·linter 또는 다른 ESLint 자동 수정 규칙까지 함께 적용하는 package script는 범위를 좁혀 실행한다.
5. 두 도구를 순차 실행해도 결과가 되돌려지지 않는지 확인한다. 공통 파일의 formatter 충돌이 있으면 원인을 확인한 뒤 진행한다.
6. 적용 후 같은 범위를 쓰기 없이 다시 검사하고 `git diff --check`를 실행한다. 자동 수정이 남거나 새 진단이 생기면 반복 실행으로 감추지 말고 원인과 파일을 확인한다.
7. 최종 diff에서 의도한 import 정렬과 Tailwind class 변경인지 확인한다. 예상치 못한 전체 재포맷, 의미가 불분명한 class 변경, 생성 파일 변경이 있으면 사용자 변경을 보존하며 원인을 확인하고 광범위한 결과를 임의로 되돌리지 않는다.

완료 보고에는 변경 파일 수와 경로, 시작 전부터 dirty였던 파일, 실행한 정확한 명령, 쓰기 없는 재검사 결과를 포함한다. 이 스킬은 파일을 stage, commit, push하지 않는다.

## 확인 및 완료 보고

- CLI에서 Biome의 organize-imports가 선택한 그룹과 상대 경로 순서를 만드는지 임시 fixture 또는 범위가 작은 대표 파일로 확인한다. 전체 저장소 파일은 사용자가 위 질문에 동의하기 전에는 일괄 수정하지 않는다.
- ESLint에서 대표 Tailwind class 문자열이 선택한 줄바꿈 값으로 autofix되는지 확인한다. canonical class 규칙을 활성화했으면 Tailwind 4.1.15 이상에서 지원되는 대표 문자열도 autofix로 확인한다. Tailwind 없는 프로젝트에는 해당 확인을 생략한다.
- `.zed/settings.json`·`.vscode/settings.json`은 JSON으로 검증하고 `git check-ignore -v`로 추적 가능 여부를 확인한다. 실제 편집기에서 저장 동작을 관찰하지 못했다면 설정 파일 검증과 IDE 저장 검증을 구분해 보고한다.
- 완료 시 변경된 파일, 실제 적용한 import 그룹 순서, Tailwind 값, formatter 충돌 여부, 실행한 정확한 확인 명령을 한글로 보고한다. 프로젝트 package manager에 맞는 Biome 검사·수정 명령과 ESLint 검사·수정 명령을 함께 알려준다. 예: `biome check <경로>`, `biome check --write <경로>`, `eslint <경로>`, `eslint <경로> --fix`.
