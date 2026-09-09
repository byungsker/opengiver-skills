---
name: mac-storage-steward
description: "Mac 저장 공간을 조사하고 위험을 분류한 뒤, 사용자가 승인한 좁은 대상만 정리하고 사후 검증할 때 사용한다."
---

# Mac 저장 공간 관리

이 Skill은 무차별적인 디스크 정리기가 아니라, 책임을 나누는 작은 팀처럼 사용한다. 저장 공간을 조사해 달라는 요청은 삭제 승인과 다르다. 매 실행마다 변경된 내용을 검증하고, 아직 결정이 필요한 후보를 보고한다.

## 역할

다음 역할을 순서대로 수행하고 역할 사이의 근거를 유지한다.

1. **저장 공간 조사자** — `df`와 읽기 전용 `du` 근거를 수집한다. 개인 파일 내용을 불필요하게 열지 않고 가장 큰 디렉터리와 파일을 찾는다.
2. **위험 검토자** — 후보를 `Safe-to-regenerate`, `Review-required`, `Protected`, `Never-touch`로 분류한다. 큰 이유와 잃을 수 있는 내용을 기록한다.
3. **정리 작업자** — 명시적으로 승인된 후보 경로에만 작업한다. 범위를 좁혀 검증한 대상을 사용하고 무관한 사용자 변경을 보존한다.
4. **검증 감사자** — 인벤토리를 다시 실행하고 정리 전후의 여유 공간을 비교하며, 승인된 대상이 바뀌었는지 확인하고 실패했거나 macOS가 보호한 항목을 보고한다.

## Approval boundary

이 공개 Skill에는 개인별 상시 승인이 없다. 생성된 개발 부산물은 소유 프로세스가 비활성이고 프로젝트 매니페스트가 존재하며 원본과 lockfile을 보존할 수 있을 때만 `Safe-to-regenerate` 후보로 제안한다. 현재 프로젝트에 같은 수준으로 구체적인 승인 정책이 없는 한, 파괴적 작업에는 사용자의 명시적 선택이 필요하다.

`CoreSimulator` runtime volumes or devices, Xcode Archives, device-support images, global Gradle or Flutter SDK caches, source, lockfiles, downloads, documents, and general application caches remain review-required or protected.

현재 사용 중이거나 앞으로 사용할 가능성이 있다는 근거가 있으면 Gradle과 CoreSimulator를 기본적으로 보존한다. 크기만으로 둘 중 하나를 통째로 삭제하지 않는다. 줄이기를 제안하기 전에 Gradle cache/wrapper 버전과 프로젝트의 `gradle-wrapper.properties`를 비교하고, Simulator runtime/device와 최근 파일 시스템·로그 활동 및 이름이 지정된 QA·증거 기기를 비교한다. 이 근거 확인 뒤 개별적으로 오래된 것으로 식별된 버전이나 기기만 삭제한다.

## 필수 절차

### 1. 기준 상태 기록

먼저 `df`를 기록하고 실행 중인 빌드 프로세스를 확인한다. 활성 소유 프로세스와 경쟁하지 않는다. 정리를 제안하기 전에 인벤토리를 실행한다.

### 2. 남은 저장 공간 조사

표준 로컬 감사로 충분하면 포함된 읽기 전용 인벤토리 스크립트를 실행한다.

```zsh
scripts/storage_inventory.sh
```

집중 감사에서는 `~/Library/Developer`, `~/Library/Caches`, `~/Downloads`, `~/Documents/GitHub`, `~/Documents`처럼 관련된 하위 트리만 조사한다. APFS는 시스템 볼륨과 데이터 볼륨을 분리하므로 `/`만 보지 말고 `/System/Volumes/Data`도 확인한다.

개인 파일의 내용을 조사하거나 출력하지 않는다. 사용자의 결정을 위해 필요한 경우에만 경로, 크기, 파일 유형, 이름을 보고한다.

### 3. 추가 삭제를 제안하기 전에 분류

- **Safe-to-regenerate:** 소유 프로세스가 비활성이고 프로젝트 매니페스트와 lockfile이 재생성 가능성을 보여 주는 생성 개발 산출물. 무엇을 다시 만들거나 내려받는지 설명한다.
- **Review-required generated caches:** 전역 Gradle/Flutter SDK cache, Simulator 데이터, Xcode Archive, 상시 승인 목록에 없는 생성 디렉터리.
- **Review-required:** Simulator device, Xcode archive, iOS device support image, 다운로드, 동영상, 중복 archive, 프로젝트 `.git` 객체, 가상 머신, 앱 지원 데이터. 사용자가 정확한 항목을 선택하도록 요청한다.
- **Protected:** macOS 관리 데이터, 활성 시스템 위치, 암호화되었거나 권한으로 보호된 cache, 실행 중인 앱이 현재 사용하는 모든 항목.
- **Never-touch without explicit separate request:** 소스 저장소, 문서, 사진, 백업, 비밀번호 저장소, 클라우드 동기화 폴더, 정체를 알 수 없는 숨김 파일.

Read [cleanup-policy.md](references/cleanup-policy.md) for the detailed decision rules.

### 4. 필요한 곳에서 승인 요청

파괴적 작업마다 후보 경로, 크기, 용도, 위험, 예상 회수 공간을 간단한 표로 보여 준다. `Review-required` 항목에 대해 “정리해 줘”라는 말만으로 승인을 추론하지 않는다. 광범위한 요청은 조사를 허가할 뿐 개인 데이터 삭제를 허가하지 않는다.

### 5. 좁은 범위로 정리

실행 직전에 모든 대상을 검증한다.

- 절대 경로로 해석한다.
- 승인된 디렉터리 안에 있는지 확인한다.
- `/`, `/System`, `/Users`, 홈 디렉터리 자체, 승인된 하위 항목을 넘어 확장될 수 있는 wildcard를 거부한다.
- 가능하면 대상을 소유한 앱을 중지하거나 피한다.
- 사용자가 승인한 개인 파일은 휴지통으로 옮기는 것을 우선하고, 승인된 cache나 생성 산출물만 영구 삭제한다.
- 넓은 루트, 홈 디렉터리, 저장소, 알 수 없는 경로에 `rm -rf`를 절대 사용하지 않는다.

Xcode `DerivedData`는 바로 아래의 자식 항목만 제거한다. 프로젝트 정리에서는 이름이 지정된 생성 디렉터리만 제거하고 매니페스트, lockfile, 소스, 테스트 증거를 보존한다. Simulator device나 runtime volume이 종료되어 있다는 이유만으로 삭제하지 않는다. 증거와 이름이 지정된 테스트 기기가 중요할 수 있다.

### 6. 검증 및 인계

인벤토리를 다시 실행하고 다음을 보고한다.

- 정리 전후 여유 공간
- 실제로 변경된 정확한 대상
- macOS가 보호했거나 실패한 대상
- 의도적으로 보존한 항목
- 남은 가장 큰 후보와 다음에 필요한 승인

프로젝트에 운영 기록이나 위키가 있다면 작업 완료 후 개인 정보가 제거된 결과만 남긴다. 개인 파일 이름, 비밀값, 원본 명령 출력은 기록하지 않는다.

## 기본 응답 계약

현재 여유 공간과 근거가 있는 가장 큰 후보를 먼저 보고한다. “정리함”과 “식별했지만 보존함”을 구분한다. 사용자가 삭제 내역을 묻는다면 정확한 대상 분류로 답하고, 파일별 검토를 하지 않은 영역은 그렇다고 밝힌다.
