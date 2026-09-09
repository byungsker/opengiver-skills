---
name: macbook-power-profile
description: "macOS MacBook의 잠자기 방지, 뚜껑 닫힘 실행, 충전 한도와 배터리 상태를 안전하게 확인·설정할 때 사용한다."
---

# MacBook 전원 프로필

이 스킬은 다음 전원 프로필을 하나의 흐름으로 다룬다.

1. 충전기 연결(AC) 상태에서 시스템 잠자기를 막아 외부 모니터와 함께 뚜껑을 닫고 사용할 수 있게 한다.
2. 사용자가 명시적으로 요청한 경우 배터리 전원에서도 유휴 잠자기와 뚜껑 닫힘 잠자기를 막는다.
3. macOS가 제공하는 기본 충전 한도를 80%로 설정한다.

설정과 별개로 AlDente 대시보드처럼 배터리 용량·건강 상태·사이클·현재 전원 상태를 읽기 전용으로 요약할 수 있다.

두 기능은 서로 독립적이다. 한쪽이 지원되지 않거나 UI에 접근할 수 없어도 다른 쪽의 결과를 섞어 성공으로 보고하지 않는다.

## 의도 라우팅

- “상태 확인”, “왜 안 자는지”, “현재 설정 보여줘”, “배터리 성능/건강/사이클/최대 용량 보여줘”는 읽기 전용 `status` 흐름으로 처리한다.
- “AlDente처럼 배터리 상태를 보여줘”는 읽기 전용 `battery-health` 흐름으로 처리한다. 설정을 변경하지 않는다.
- “설정해줘”, “뚜껑 닫아도 켜져 있게 + 80%로 맞춰줘”는 아래 `configure` 흐름을 실행한다.
- “충전기 없이도 뚜껑 닫고 계속 실행해줘”처럼 배터리 상태의 뚜껑 닫힘을 명시한 요청은 `battery-closed-lid` 흐름을 추가로 실행한다.
- “원래대로”, “되돌려줘”는 이 스킬이 만든 변경과 이 스킬이 소유한 세션 가드만 `restore` 흐름으로 되돌린다.
- 단순한 설명 요청에는 명령을 실행하지 않는다.

설정 요청이 명시된 경우에는 같은 Mac의 전원 설정을 변경할 수 있다. 설정 전 현재 값을 기록하고, 변경 뒤 각각을 다시 검증해 결과를 보고한다.

## 안전 규칙

- 사용자가 배터리 전원에서 뚜껑 닫힘을 명시하지 않은 한 배터리 프로필은 건드리지 않는다. `pmset -a`는 사용하지 않는다.
- 배터리 뚜껑 닫힘 요청이 명시된 경우에만 `pmset -b sleep 0 disablesleep 1`을 사용할 수 있다. `disablesleep`은 문서화되지 않은 설정이고 `-b`로 지정해도 `SleepDisabled=1`이라는 전역 상태를 만들 수 있으므로, 변경 전 값을 기록하고 명시적인 복원 경로를 함께 보고한다.
- `AppleClamshellCausesSleep`, `hibernatemode`, `standby`, `autopoweroff`는 변경하지 않는다. 뚜껑 센서를 패치하거나 커널 확장·비공식 드라이버를 설치하지 않는다.
- `SleepDisabled=1`은 배터리 완전 방전·발열 위험이 있다. 가방이나 밀폐된 공간에 넣기 전 반드시 `disablesleep 0`으로 되돌리거나 수동 잠자기를 실행하도록 경고한다. 자동 저전력 차단은 사용자가 별도로 요청하지 않으면 추가하지 않는다.
- `killall caffeinate`, `pkill`, `killall AlDente`처럼 소유권을 확인하지 않는 종료 명령은 사용하지 않는다. Orca, AlDente, 사용자가 직접 실행한 프로세스는 그대로 둔다.
- `sudo`가 필요하면 터미널의 일반 인증 흐름을 사용한다. 비밀번호를 수집·출력하거나 `sudo -S`로 주입하지 않는다.
- 상태 확인만 요청된 경우에는 `pmset`, `ioreg`, `system_profiler`, `ps`와 System Settings UI를 읽기만 한다.

## 1. 사전 점검 및 스냅샷

설정 전에 다음 명령을 각각 실행해 결과를 보존한다. 긴 `pmset -g log` 전체를 수집할 필요는 없다.

```sh
pmset -g
pmset -g custom
pmset -g batt
pmset -g assertions
pmset -g cap
system_profiler SPDisplaysDataType
ioreg -r -c AppleSmartBattery -l | rg 'ExternalConnected|CurrentCapacity|MaxCapacity|IsCharging|AppleRawCurrentCapacity'
ps -axo user=,pid=,ppid=,lstart=,command= | rg '[ /](caffeinate|AlDente)([[:space:]]|$)|aldente|Orca'
```

배터리 건강 요약이 목적이면 스킬에 포함된 `scripts/show_battery_health.sh`를 실행한다. 이 스크립트는 `AppleSmartBattery`와 `system_profiler SPPowerDataType`만 읽고 아무 설정도 변경하지 않는다.

필요하면 `mktemp -d -t macbook-power-profile`로 임시 스냅샷 디렉터리를 만들고 위 결과를 저장한다. 복원에 필요한 AC `sleep`의 기존 숫자와 충전 한도의 기존 UI 값을 반드시 기록한다. 이전 값을 알 수 없으면 복원 때 임의의 기본값을 추측하지 않는다.

다음 조건을 별도로 판정한다.

- 현재 전원이 `AC Power`인지 확인한다. `caffeinate -s`는 AC에서만 시스템 잠자기 방지 assertion이 유효하다.
- AC 클램셸 흐름에서는 내장 디스플레이 외에 외부 디스플레이가 하나 이상 연결됐는지 확인한다. AC + 외부 디스플레이가 없으면 AC 뚜껑 닫힘을 보장한다고 보고하지 않는다.
- `battery-closed-lid` 흐름에서는 외부 디스플레이가 필수가 아니지만 `SleepDisabled=1`이 실제로 읽히는지 확인하고, 물리적으로 뚜껑을 닫는 수동 테스트 없이는 동작 성공을 단정하지 않는다.
- `pmset -g assertions`에서 `PreventSystemSleep`을 `PreventUserIdleSystemSleep`과 구분한다. 후자만으로는 뚜껑 닫힘 동작을 보장하지 않는다.
- 일반 흐름에서는 `pmset -g custom`의 `AC Power` 블록에서 `sleep`만 확인한다. 배터리 블록은 비교용으로 읽는다.
- `battery-closed-lid` 흐름에서는 `Battery Power`의 `sleep`과 `pmset -g`의 `SleepDisabled`를 함께 확인한다.

## 2. 잠자기 방지 설정

AC 프로필의 유휴 시스템 잠자기 시간만 0으로 설정한다.

```sh
sudo pmset -c sleep 0
```

`displaysleep`은 사용자가 “외부 모니터도 계속 켜 둬”라고 별도로 요청한 경우에만 변경한다. 그 경우에도 AC에만 적용한다.

배터리 전원에서도 뚜껑을 닫은 뒤 계속 실행하라는 요청이 명시된 경우에는 배터리 유휴 타이머와 뚜껑 닫힘 잠자기 차단을 함께 설정한다.

```sh
sudo pmset -b sleep 0 disablesleep 1
```

이 명령의 성공 판정은 `pmset -g custom`에 `Battery Power`의 `sleep 0`이 보이고, `pmset -g`에 `SleepDisabled 1`이 보이는 것이다. `-b`는 명령 입력 프로필을 지정하지만 `SleepDisabled`는 현재 macOS에서 전역 플래그로 표시될 수 있으므로 “배터리에만 적용됐다”고 표현하지 않는다. 이 설정은 재부팅 후에도 남을 수 있다.

복원할 때는 스냅샷의 배터리 `sleep` 값을 사용하고, 뚜껑 닫힘 차단은 다음처럼 해제한다.

```sh
sudo pmset -b sleep <battery-snapshot-value> disablesleep 0
```

AC 클램셸 상태에서 현재 세션의 시스템 잠자기를 확실히 막아야 하고 이미 유효한 `PreventSystemSleep` assertion이 없으면, 이 스킬이 시작한 프로세스만 관리하는 세션 가드를 만든다.

```sh
/usr/bin/caffeinate -s >/dev/null 2>&1 &
```

세션 가드를 백그라운드로 시작했다면 PID를 `/tmp/macbook-power-profile.caffeinate.pid`에 기록한다. 기존 PID 파일이 있으면 다음을 모두 확인한 뒤 재사용한다.

- PID가 숫자이고 현재 사용자 소유인지
- 프로세스 경로가 `/usr/bin/caffeinate`인지
- 인자가 이 스킬이 기대하는 `-s`인지

검사가 하나라도 맞지 않으면 그 프로세스를 건드리지 말고 새 가드를 만들거나, 이미 다른 프로세스의 `PreventSystemSleep`이 유효하다는 사실만 보고한다. 이 스킬이 만든 PID만 `restore`에서 종료한다. PID 파일이 없거나 PID가 재사용된 경우에는 절대 종료하지 않는다.

외부 디스플레이가 없거나 AC가 아니면 AC용 `caffeinate -s` 가드를 만들지 말고 부족한 전제와 가능한 범위를 보고한다. 배터리 뚜껑 닫힘 흐름에서는 `caffeinate -i`를 주된 해결책으로 보고하지 않는다. 그것은 유휴 잠자기 assertion이며 `Clamshell Sleep`을 보장하지 않는다. 충전 상한 설정은 이 조건과 독립적으로 계속 진행할 수 있다.

## 3. macOS 기본 충전 상한 80%

충전 상한은 `pmset`, `defaults`, `ioreg` 쓰기, 숨은 plist 키로 설정하지 않는다. Apple Silicon과 지원되는 macOS에서는 System Settings UI를 사용한다.

1. `open 'x-apple.systempreferences:com.apple.Battery-Settings'`로 시스템 설정의 배터리 패널을 연다.
2. `충전` 또는 `Charging` 항목 옆의 정보 버튼을 연다.
3. `충전 한도` 또는 `Charge Limit` 슬라이더를 80으로 옮긴다.
4. 저장·닫기 후 같은 패널을 다시 열어 `80% 한도` 또는 `80% charge limit` 문구와 슬라이더 값 80을 UI에서 확인한다.

UI 자동화가 가능한 환경에서는 화면의 실제 접근성 트리와 표시 문구로 확인한다. UI가 잠겨 있거나 권한·MDM 정책으로 조작할 수 없으면 그 단계에서 중단하고 사용자가 System Settings에서 수행할 정확한 경로를 안내한다. 충전량이 우연히 80%인 것만으로 충전 상한 설정 성공을 판정하지 않는다.

충전 한도 UI가 없는 Mac이나 macOS에서는 지원되지 않는다고 보고한다. Optimized Battery Charging을 80% 한도로 오인하거나 AlDente를 대신 설치하지 않는다. 네이티브 한도는 배터리 잔량 보정 때문에 가끔 100%까지 충전할 수 있으므로, 그 예외를 오류로 단정하지 않는다.

## 4. 배터리 성능·건강 보고

`battery-health` 흐름에서는 다음 항목을 한 번의 읽기 전용 보고서로 보여준다.

- 설계 용량(mAh)과 설계 대비 100%
- I/O Registry가 보고한 원시 최대 충전 용량(mAh)과 설계 용량으로 계산한 비율
- macOS가 보고한 최대 용량(%)과 건강 상태(`Condition`)
- 사이클 수
- 현재 잔량, 충전 중 여부, 외부 전원 연결 여부, 완전 충전 여부, 남은 시간
- 가능한 경우 배터리 온도(°C), 전압(V), 컨트롤러의 `DailyMaxSoc`

용량 지표의 의미를 섞지 않는다. `AppleRawMaxCapacity / DesignCapacity`는 하드웨어 원시 추정치이고, `system_profiler`의 `Maximum Capacity`는 macOS의 건강 추정치다. 두 값이 다를 수 있으며, AlDente 화면처럼 macOS 퍼센트에 임의의 mAh를 곱해 만들어내지 않는다. macOS의 mAh 환산값이 노출되지 않으면 퍼센트만 표시하고 “확인 불가”로 둔다.

`Service Recommended` 같은 건강 상태는 macOS가 보고한 문자열 그대로 전달한다. 퍼센트나 사이클 수만 보고 상태를 임의로 “정상” 또는 “교체 필요”로 재분류하지 않는다. 값이 없는 항목은 추측하지 말고 `확인 불가`로 표시한다.

이 보고서는 현재 시점의 스냅샷이다. AlDente의 과거 그래프, 충전 기록, 보정 진행률, 어댑터 잠금 UI까지 재현한다고 주장하지 않는다.

## 5. AlDente 충돌 처리

설정 전후에 AlDente 프로세스와 helper가 있는지 확인한다. AlDente가 실행 중이거나 `chargeVal`이 80으로 보이면 “80%를 두 제어기가 함께 관리 중”이라고 보고한다.

- 이 스킬은 AlDente를 자동 종료·삭제하지 않고, 로그인 항목이나 privileged helper도 바꾸지 않는다.
- 사용자가 명시적으로 “AlDente를 끄거나 삭제해줘”라고 요청한 경우에만 대상 앱·helper·로그인 항목을 먼저 보여 주고 별도의 확인을 받은 뒤 처리한다.
- 따라서 네이티브 UI에서 80%가 확인됐더라도 AlDente가 남아 있으면 “앱 없이 동작 중”이라고 표현하지 않는다. “macOS 기본 한도 설정 완료, AlDente는 별도 실행 중”이라고 구분한다.

## 6. 최종 검증 및 보고

설정 후 다음을 다시 읽는다.

```sh
pmset -g custom
pmset -g batt
pmset -g assertions
```

성공 판정은 다음처럼 분리한다.

- 잠자기 방지: `AC Power`의 `sleep 0`이 보이고, 클램셸 전제(AC + 외부 디스플레이)가 충족되며, 필요 시 `PreventSystemSleep` assertion이 실제로 보인다.
- 배터리 뚜껑 닫힘: `Battery Power`의 `sleep 0`과 `SleepDisabled 1`을 읽고, 사용자가 뚜껑을 닫은 상태에서 원격 접속·에이전트 실행을 확인했을 때만 완전 성공으로 보고한다. 설정값만 확인되면 “설정 적용 완료, 물리 테스트 대기”로 구분한다.
- 충전 상한: System Settings의 충전 한도 UI가 80을 표시한다.
- 앱 독립성: AlDente가 없거나 사용자가 별도로 끈 경우에만 “AlDente 없이”라고 보고한다.

결과에는 변경한 값, 배터리 `SleepDisabled`의 전역 영향, 현재 AC 여부, 외부 디스플레이 여부, 소유한 caffeinate PID, AlDente 충돌 여부, 재부팅 후에도 남는 설정과 세션 종료 시 사라지는 가드를 명시한다.

## 복원

복원 요청이 오면 스냅샷에 기록된 AC·배터리 `sleep` 숫자를 사용해 해당 값만 되돌린다.

```sh
sudo pmset -c sleep <snapshot-value>
# 배터리 뚜껑 닫힘 모드를 사용한 경우
sudo pmset -b sleep <battery-snapshot-value> disablesleep 0
```

이 스킬이 기록한 PID 파일의 프로세스가 여전히 동일한 `/usr/bin/caffeinate -s`인지 확인한 뒤에만 종료하고 PID 파일을 정리한다. 다른 `caffeinate`, Orca, AlDente 프로세스는 종료하지 않는다. 배터리 `SleepDisabled`를 복원하면 `SleepDisabled 0`을 다시 확인한다. 충전 한도는 스냅샷에서 읽은 이전 UI 값이 있을 때만 System Settings에서 되돌리며, 모르면 현재 80을 유지하고 사용자에게 이전 값을 알 수 없다고 보고한다.
