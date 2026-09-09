# Toss Frontend Fundamentals 원문 인덱스

이 문서는 요약이 아니라 `references/source/`에 보존한 원문 스냅샷을 어떤 상황에서 읽을지 정하는 인덱스다. `review-rubric.md`만 읽고 원문을 읽었다고 간주하지 않는다.

## 스냅샷 정보

- 원격 저장소: <https://github.com/toss/frontend-fundamentals>
- 공개 문서: <https://frontend-fundamentals.com/code-quality/>
- 확인한 저장소 커밋: `161d3d6a0d6d372eacd75036de567511643f6265`
- 확인일: 2026-09-09
- 로컬 원문 루트: `references/source/`
- 라이선스: 원본 저장소의 [MIT License](source/LICENSE.md)

이 스냅샷은 해당 커밋의 근거를 보존하기 위한 것이다. 사용자가 최신 원문 여부를 묻거나 원격 저장소의 변경을 의심하면 현재 GitHub 파일과 커밋을 다시 확인한다.

## 반드시 지킬 로딩 순서

1. 현재 코드에서 관찰한 냄새를 하나 이상의 원문 문서 제목과 연결한다.
2. 아래 표의 로컬 파일을 실제로 읽는다. 문서 제목이나 파일명만 보고 판단하지 않는다.
3. 원문이 제시한 개선안과 예외·트레이드오프를 확인한다.
4. 현재 프로젝트의 코드·호출자·테스트에 적용되는지 대조한다.
5. 보고서의 `원문` 항목에 로컬 경로와 원격 문서 URL을 남긴다.

원문에서 다루지 않는 문제는 Toss 원칙으로 포장하지 않는다. 성능·접근성·보안·기능 오류는 해당 전문 규칙과 별도 근거로 분리한다.

## 기준별 원문 라우팅

### 공통

| 상황 | 먼저 읽을 문서 |
| --- | --- |
| 배포된 code-quality 문서의 진입점과 범위를 확인할 때 | [index.md](source/fundamentals/code-quality/index.md) |
| 네 기준의 정의와 상충 관계를 확인할 때 | [code/index.md](source/fundamentals/code-quality/code/index.md) |
| 문서의 목적과 사용 범위를 확인할 때 | [code/start.md](source/fundamentals/code-quality/code/start.md) |

### 가독성

| 관찰 신호 | 원문 문서 | 원문이 다루는 판단 |
| --- | --- | --- |
| 서로 실행되지 않는 분기가 한 컴포넌트에 섞임 | [submit-button.md](source/fundamentals/code-quality/code/examples/submit-button.md) | 분기별 컴포넌트 분리 |
| 구현 상세가 호출부에 노출됨 | [login-start-page.md](source/fundamentals/code-quality/code/examples/login-start-page.md) | 맥락을 줄이는 Wrapper·추상화의 조건 |
| 여러 종류의 상태·쿼리·API 로직이 한 Hook에 섞임 | [use-page-state-readability.md](source/fundamentals/code-quality/code/examples/use-page-state-readability.md) | 로직 종류가 아니라 책임 단위로 분리 |
| 복잡한 조건식 | [condition-name.md](source/fundamentals/code-quality/code/examples/condition-name.md) | 도메인 의미가 드러나는 이름과 이름을 생략해도 되는 단순 조건 |
| 의미 없는 숫자·문자열 | [magic-number-readability.md](source/fundamentals/code-quality/code/examples/magic-number-readability.md) | 읽기를 돕는 이름과 과도한 상수화의 경계 |
| 코드 위아래를 반복해서 이동함 | [user-policy.md](source/fundamentals/code-quality/code/examples/user-policy.md) | 요구사항을 가까이 드러내기와 조회 객체의 선택 |
| 중첩 삼항 | [ternary-operator.md](source/fundamentals/code-quality/code/examples/ternary-operator.md) | early return·조건문으로 흐름 단순화 |
| 비교식 방향이 읽기 어려움 | [comparison-order.md](source/fundamentals/code-quality/code/examples/comparison-order.md) | 왼쪽에서 오른쪽으로 읽히는 표현 |

### 예측 가능성

| 관찰 신호 | 원문 문서 | 원문이 다루는 판단 |
| --- | --- | --- |
| 표준 API와 이름이 겹치거나 실제 동작이 다름 | [http.md](source/fundamentals/code-quality/code/examples/http.md) | 이름 충돌을 피하고 실제 계약 드러내기 |
| 같은 종류의 Hook·함수가 반환 모양이 다름 | [use-user.md](source/fundamentals/code-quality/code/examples/use-user.md) | 반환 계약 통일과 판별 가능한 Union |
| 조회·계산 함수에 부수 효과가 숨음 | [hidden-logic.md](source/fundamentals/code-quality/code/examples/hidden-logic.md) | 부수 효과를 호출부나 이름으로 드러내기 |

### 응집도

| 관찰 신호 | 원문 문서 | 원문이 다루는 판단 |
| --- | --- | --- |
| 함께 수정되는 파일이 기술별 디렉터리에 흩어짐 | [code-directory.md](source/fundamentals/code-quality/code/examples/code-directory.md) | 기능·도메인 기준으로 함께 배치 |
| 같은 의미의 값이 여러 파일에 반복됨 | [magic-number-cohesion.md](source/fundamentals/code-quality/code/examples/magic-number-cohesion.md) | 함께 변경되는 상수의 단일 기준 |
| 폼의 필드·검증·제출 배치가 문제의 변경 단위와 다름 | [form-fields.md](source/fundamentals/code-quality/code/examples/form-fields.md) | 필드 단위와 폼 전체 단위의 선택 |

### 결합도

| 관찰 신호 | 원문 문서 | 원문이 다루는 판단 |
| --- | --- | --- |
| 하나의 Hook이 너무 많은 책임을 관리함 | [use-page-state-coupling.md](source/fundamentals/code-quality/code/examples/use-page-state-coupling.md) | 책임별 Hook으로 영향 범위 축소 |
| 공통화된 코드가 페이지별 변화를 억지로 흡수함 | [use-bottom-sheet.md](source/fundamentals/code-quality/code/examples/use-bottom-sheet.md) | 결합도를 낮추기 위한 중복 허용 |
| 중간 컴포넌트가 사용하지 않는 Props를 전달함 | [item-edit-modal.md](source/fundamentals/code-quality/code/examples/item-edit-modal.md) | 조합을 먼저 검토하고 깊은 공유에만 Context 사용 |

## 실행용 참고 원문

저장소의 Claude Code 플러그인은 위 문서를 에이전트가 적용하는 최소 규칙으로 압축한 4개 Skill을 제공한다. 원문 예시와 실행 규칙이 충돌하면 원문 문서의 구체적 맥락을 우선하고, 플러그인 파일은 적용 형식과 평가 기준을 확인할 때만 읽는다.

- [readability/SKILL.md](source/frontend-fundamentals-plugin/skills/readability/SKILL.md)
- [predictability/SKILL.md](source/frontend-fundamentals-plugin/skills/predictability/SKILL.md)
- [cohesion/SKILL.md](source/frontend-fundamentals-plugin/skills/cohesion/SKILL.md)
- [coupling/SKILL.md](source/frontend-fundamentals-plugin/skills/coupling/SKILL.md)
- [grader.md](source/frontend-fundamentals-plugin/eval/graders/grader.md)
