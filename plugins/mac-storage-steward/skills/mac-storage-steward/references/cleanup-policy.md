# Mac 저장 공간 정리 정책

## 판단 표

| Class | Examples | Default action |
| --- | --- | --- |
| Safe-to-regenerate | Xcode `DerivedData`; npm/Yarn caches; Flutter `build/` and `.dart_tool/`; `.nuxt`, `.output`, `.next`, `node_modules/.cache`, `node_modules/.vite`; inactive `node_modules` and iOS `Pods/` with manifests and lockfiles | Propose the exact target after checking the owner is inactive; obtain explicit selection before deletion and preserve lockfiles and source |
| Review-required generated caches | Global Gradle/Flutter SDK caches, Simulator data, archives, device-support images, and unlisted build outputs | List exact items and obtain explicit selection |
| Review-required personal/project data | Downloads, videos, project history, virtual machines, app-support data | List exact items and obtain explicit selection |
| Protected | macOS-managed folders, active app data, permission-protected caches | Preserve and report |
| Never-touch | Source, documents, photos, backups, passwords, cloud folders | Preserve unless the user makes a separate, exact request |

## 안전 규칙

- 저장 공간 크기만으로 삭제를 결정하지 않으며, 이 공개 Skill에는 개인별 상시 승인이 없다.
- cache에는 앱에 필요한 오프라인 미디어나 상태가 남아 있을 수 있으므로 그 trade-off를 설명한다.
- `DerivedData`는 재생성할 수 있지만 다음 빌드가 느려질 수 있다.
- `gradle-wrapper.properties`가 해당 버전을 가리키는 프로젝트에는 Gradle cache와 wrapper 배포본이 필요하다. 정리 전에 버전을 비교하고 `~/.gradle` 전체를 일상적으로 삭제하지 않는다.
- Simulator device 데이터에는 테스트 증거, 초기 데이터베이스, 스크린샷이 있을 수 있으므로 “오래된 cache”라는 이유로 일괄 삭제하지 않는다.
- device 디렉터리나 CoreSimulator 로그에 최근 활동이 보이거나 이름이 QA·증거 작업을 나타내면 최근 사용 기기로 취급한다. 이름이 지정된 증거 기기는 사용자가 명시적으로 선택하기 전까지 보존한다.
- APFS 여유 공간은 purgeable 공간이 회수되면서 정리 후에도 바뀔 수 있다. 데이터 볼륨으로 검증하고 관찰값을 보고한다.
- macOS가 `Operation not permitted`를 보고하면 자동으로 권한을 높이지 않는다. 보호된 경로를 보고한다.

## 워크트리별 앱 Simulator 수명주기

- 앱 작업 단위가 Simulator를 새로 만들면 작업 증거에 워크트리의 canonical path 또는 식별자, Simulator UDID, runtime, 기기 모델을 함께 기록한다. 기기 이름만으로 소유 관계를 추정하지 않는다.
- 작업 단위가 완료되고 해당 워크트리를 제거하는 시점에만 그 워크트리의 Simulator 정리를 후보로 삼는다. 워크트리 제거와 Simulator 삭제는 하나의 종료 정리 흐름으로 계획하되, 실제 삭제 전후 검증은 각각 수행한다.
- 삭제 전에는 `xcrun simctl list devices`로 정확한 UDID를 확인하고, 기기가 부팅·사용 중이 아닌지, 테스트 결과·스크린샷·시드 데이터가 보존될 필요가 없는지, 다른 워크트리나 공유 QA 흐름이 사용하지 않는지 확인한다.
- 조건을 통과한 경우에만 기록된 정확한 UDID를 `xcrun simctl delete <UDID>`로 삭제한다. 이름·상태·오래된 날짜만으로 Simulator를 일괄 삭제하지 않는다.
- 공유 기기, 증거 기기, QA 기준 기기와 Simulator runtime은 워크트리 소유가 명시적으로 확인되지 않는 한 보존한다. 기기 데이터 삭제와 runtime 삭제를 혼동하지 않는다.
- 삭제 후에는 해당 UDID가 `xcrun simctl list devices`에 남아 있지 않은지, 워크트리 경로가 의도대로 제거되었는지, 다른 작업의 dirty/untracked 자료와 저장 공간이 보존되었는지 확인하고 결과를 기록한다.

## Codex 세션 저장 공간 관리

- Codex 세션은 단순 텍스트가 아니라 대화 이벤트, 도구 호출, 도구 출력과 작업 메타데이터를 포함한 로컬 JSONL 기록이다. 용량만으로 과거 세션을 불필요하다고 판단하지 않는다.
- Codex는 `sessions/`에 재개 가능한 rollout을 두고 `archived_sessions/`라는 별도 보관 영역도 사용한다. 두 영역과 `state_5.sqlite`, `session_index.jsonl`은 서로 연결될 수 있으므로 파일만 직접 이동·삭제·재구성하지 않는다.
- OpenAI의 현재 오픈소스 설정에서 `[history] max_bytes`는 `history.jsonl`에만 적용된다. 재개 가능한 rollout의 보존기간이나 “90일 후 삭제”를 의미하지 않는다.
- 세션은 나이만으로 삭제하지 않는다. 삭제·이동·압축은 사용자가 정확한 범위를 승인한 뒤, 활성 세션·state DB 참조·resume 가능성·복구본을 확인하는 별도 작업으로 수행한다.
- 작업 단위가 끝나면 핵심 결정·변경 파일·검증 결과·재개 지점을 프로젝트 문서, 이슈·PR, 또는 프로젝트 운영 위키에 남긴다. 이것이 장기 보존 기록이고 raw rollout은 복구 보조 자료다.
- 세션 증가를 줄이려면 작업 단위별로 새 세션을 시작하고, 대형 로그·빌드 출력은 `head`·`tail`·필터로 제한한다. 이 조치는 미래 증가량을 줄일 뿐 기존 rollout을 정리하지 않는다.
- Codex 소스에는 cold rollout 압축 기능이 있으나 feature-gated이며 설치된 버전에서 활성화됐다고 추정하지 않는다. 압축·외부 보관은 현재 설치 버전의 resume/unarchive 지원과 원본 복구를 검증한 뒤에만 선택한다.
- OpenAI가 제공하는 공식 cold archive 경로·보존기간 정책이 확인되지 않으면, 에이전트는 고정 기간 삭제를 권장하지 말고 후보 목록과 영향만 보고한 뒤 사용자 선택을 받는다.
