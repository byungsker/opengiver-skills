# Codex 세션 보존 및 정리 기준

## 목적

Codex의 로컬 세션 저장 공간을 줄이면서 과거 작업을 재개할 수 있는 원본과, 작업 결과를 장기 보존하는 문서를 혼동하지 않는다.

## 저장 영역 구분

- `~/.codex/sessions/`: 진행 중이거나 일반적으로 재개 가능한 rollout JSONL
- `~/.codex/archived_sessions/`: Codex가 관리하는 보관 rollout 영역
- `~/.codex/history.jsonl`: 입력 히스토리. `[history] max_bytes`의 대상
- `~/.codex/state_5.sqlite`, `~/.codex/session_index.jsonl`: 세션 발견·상태·경로를 보조하는 로컬 인덱스
- 프로젝트 문서·이슈·PR·프로젝트 운영 위키: 핵심 결정, 변경 파일, 검증 결과, 다음 재개 지점을 남기는 durable checkpoint

## 에이전트의 기본 행동

1. 세션 파일의 날짜나 크기만으로 삭제 후보를 확정하지 않는다.
2. OpenAI가 “90일 후 삭제”를 권장한다고 말하지 않는다. 공식 보존기간이 확인되지 않으면 기간을 임의로 정하지 않는다.
3. 작업 단위가 끝나면 raw transcript가 아니라 핵심 결과를 durable checkpoint에 남긴다. 원본 세션은 복구 보조 자료로 분류한다.
4. 저장 공간 압박이 있으면 `sessions/`와 `archived_sessions/`를 모두 조사하고, 활성 세션·state DB 참조·resume 필요성을 확인한다.
5. 삭제·이동·압축은 사용자가 정확한 날짜·폴더·세션 또는 보존 범위를 승인한 경우에만 수행한다.
6. 파일을 직접 옮긴 뒤 인덱스나 SQLite를 임의로 고치지 않는다. Codex가 지원하는 archive/unarchive 흐름 또는 검증된 복구 절차가 없는 상태에서는 원본을 보존한다.

## 저장 공간을 줄이는 우선순위

- 첫째, 이후 세션의 불필요한 대형 도구 출력과 중복 작업을 줄인다.
- 둘째, 완료된 작업의 결과를 프로젝트 문서·이슈·PR·프로젝트 운영 위키에 기록해 raw session 의존도를 낮춘다.
- 셋째, 현재 Codex 버전이 지원하는 cold rollout compression 또는 archive 동작을 별도 검증한다.
- 넷째, 사용자가 선택한 정확한 세션만 백업·체크섬 검증 후 정리한다.

## 근거와 한계

- OpenAI Codex 소스의 `history` 설정은 `history.jsonl`의 persistence와 `max_bytes`를 정의하며 rollout 보존기간 설정과는 별개다.
- OpenAI Codex 소스에는 `sessions/`, `archived_sessions/`, cold rollout compression 관련 구현이 있으나, 현재 설치 버전·feature flag·Desktop 연동 상태는 별도로 확인해야 한다.
- OpenAI 공식 저장소에는 외부 cold archive와 보존 정책을 요구하는 논의가 있으므로, 외부 보관을 현재 제품의 보장된 기능으로 설명하지 않는다.

## 참고

- https://github.com/openai/codex/blob/main/codex-rs/config/src/types.rs
- https://github.com/openai/codex/blob/main/codex-rs/message-history/src/lib.rs
- https://github.com/openai/codex/blob/main/codex-rs/rollout/src/compression.rs
- https://github.com/openai/codex/issues/37216
