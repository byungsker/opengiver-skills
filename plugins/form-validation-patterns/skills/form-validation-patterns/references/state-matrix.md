# 폼 상태 매트릭스

폼을 구현하거나 검토할 때 해당 행을 프로젝트의 실제 상태명과 컴포넌트에 매핑한다. 모든 행이 모든 폼에 필요한 것은 아니지만, 적용하지 않은 행은 이유를 기록한다.

| 상태 | 진입 조건 | 사용자에게 보이는 피드백 | 접근성 계약 | 확인할 위험 |
|---|---|---|---|---|
| `empty/pristine` | 최초 진입, 값 없음 | 목적·필수 여부·다음 행동 | `label`과 설명 연결 | 빈 상태가 오류처럼 보임 |
| `editing` | 입력 또는 수정 중 | 기존 오류 갱신 규칙 | 입력 `focus` 보존 | 오류가 너무 이르거나 늦게 표시됨 |
| `invalid` | `client/cross-field` 규칙 실패 | `inline field/group` 오류, 필요 시 요약 | `aria-invalid`, `aria-describedby`, 오류 `focus` | 색상/`disabled`만 피드백 |
| `validating` | 비동기 검증 중 | 진행 중임과 재입력 가능 여부 | `aria-busy` 또는 `live` 상태 | 오래된 응답이 최신 값 덮어씀 |
| `submitting` | 유효한 제출 시작 | 처리 중 상태, 중복 제출 방지 | 상태 설명, `focus` 탈취 금지 | `double submit` |
| `success` | 권위 있는 처리 완료 | 완료 결과와 다음 행동 | 성공 `live/status`, 예측 가능한 `focus` | 성공을 버튼 변화로만 표시 |
| `failure/retry` | 네트워크·서버 실패 | 원인 범위, 보존된 값, 재시도 | 오류와 `retry control` 연결 | 재시도 때 입력 초기화 |
| `policy/domain` | 권한·소유권·업무 규칙 거절 | `field/form` 수준의 업무 오류 | 형식 오류와 구분되는 설명 | `client` 규칙으로 오판 |
| `stale/duplicate` | 이전 요청 또는 반복 제출 | 최신 요청만 유효하다는 상태 | 무관한 `focus` 이동 금지 | 이전 응답 반영·중복 처리 |
| `empty-result` | 조회/검색 결과 없음 | 다음 검색·생성·재시도 행동 | `heading/status` 구조 | 막다른 빈 화면 |
