---
description: 설정된 Biome import와 ESLint Tailwind 자동 수정을 전체 대상 코드에 적용
---

# Biome·ESLint 전체 코드 일괄 적용

이 명령은 현재 저장소 전체의 설정된 규칙을 적용하라는 명시적 요청이다. 함께 제공되는 `biome-eslint-ide-config-skill` Skill의 `전체 코드 일괄 적용` 절차를 읽고 실행한다.

- 적용 전에 저장소 지침, 도구 버전과 실제 설정, 대상 파일 범위, 시작 시점의 작업 트리 상태를 확인한다.
- 이 스킬에서 설정한 Biome import 정렬과 ESLint Tailwind 자동 수정만 적용하고 다른 규칙은 함께 실행하지 않는다.
- 같은 범위를 쓰기 없이 다시 검사하고 diff를 검토한다. 기존 사용자 변경을 보존하며 파일을 stage, commit, push하지 않는다.
