#!/bin/zsh

# Read-only battery health snapshot for macOS MacBooks.
set -u

IOREG_OUTPUT="$(ioreg -r -c AppleSmartBattery -l 2>/dev/null || true)"
if [[ -z "$IOREG_OUTPUT" ]]; then
  print -r -- "배터리: AppleSmartBattery 정보를 찾을 수 없습니다."
  exit 0
fi

SP_OUTPUT="$(system_profiler SPPowerDataType 2>/dev/null || true)"

ioreg_number() {
  printf '%s\n' "$IOREG_OUTPUT" | sed -nE "s/.*\"$1\"[[:space:]]*=[[:space:]]*([0-9]+).*/\1/p" | head -1
}

ioreg_word() {
  printf '%s\n' "$IOREG_OUTPUT" | sed -nE "s/.*\"$1\"[[:space:]]*=[[:space:]]*([^,]+).*/\1/p" | head -1 | sed 's/[[:space:]]+$//'
}

sp_value() {
  printf '%s\n' "$SP_OUTPUT" | sed -nE "s/^[[:space:]]*$1: (.*)$/\1/p" | head -1
}

first_nonempty() {
  local candidate
  for candidate in "$@"; do
    if [[ -n "$candidate" ]]; then
      print -r -- "$candidate"
      return 0
    fi
  done
  print -r -- ""
}

DESIGN_CAPACITY="$(ioreg_number DesignCapacity)"
RAW_MAX_CAPACITY="$(ioreg_number AppleRawMaxCapacity)"
RAW_CURRENT_CAPACITY="$(ioreg_number AppleRawCurrentCapacity)"
CURRENT_CAPACITY="$(ioreg_number CurrentCapacity)"
CYCLE_COUNT="$(first_nonempty "$(sp_value 'Cycle Count')" "$(sp_value '사이클 횟수')" "$(ioreg_number CycleCount)")"
MACOS_MAX_CAPACITY="$(first_nonempty "$(sp_value 'Maximum Capacity')" "$(sp_value '최대 용량')")"
MACOS_CONDITION="$(first_nonempty "$(sp_value 'Condition')" "$(sp_value '상태')")"
STATE_OF_CHARGE="$(first_nonempty "$(sp_value 'State of Charge (%)')" "$(sp_value '배터리 잔량 (%)')" "$CURRENT_CAPACITY")"
CHARGING="$(first_nonempty "$(sp_value 'Charging')" "$(sp_value '충전 중')" "$(ioreg_word IsCharging)")"
FULLY_CHARGED="$(first_nonempty "$(sp_value 'Fully Charged')" "$(sp_value '완전 충전')" "$(ioreg_word FullyCharged)")"
AC_CONNECTED="$(first_nonempty "$(sp_value 'Connected')" "$(sp_value '연결됨')" "$(ioreg_word ExternalConnected)")"
TIME_REMAINING="$(ioreg_number TimeRemaining)"
TEMPERATURE_RAW="$(ioreg_number Temperature)"
VOLTAGE_RAW="$(ioreg_number Voltage)"
DAILY_MAX_SOC="$(ioreg_number DailyMaxSoc)"

if [[ -n "$STATE_OF_CHARGE" && "$STATE_OF_CHARGE" != *% ]]; then
  STATE_OF_CHARGE="${STATE_OF_CHARGE}%"
fi

RAW_HEALTH=""
if [[ "$DESIGN_CAPACITY" != "" && "$RAW_MAX_CAPACITY" != "" ]]; then
  RAW_HEALTH="$(awk -v raw="$RAW_MAX_CAPACITY" -v design="$DESIGN_CAPACITY" 'BEGIN { if (design > 0) printf "%.1f", raw / design * 100 }')"
fi

TEMPERATURE=""
if [[ "$TEMPERATURE_RAW" != "" ]]; then
  TEMPERATURE="$(awk -v raw="$TEMPERATURE_RAW" 'BEGIN { printf "%.1f", raw / 100 }')"
fi

VOLTAGE=""
if [[ "$VOLTAGE_RAW" != "" ]]; then
  VOLTAGE="$(awk -v raw="$VOLTAGE_RAW" 'BEGIN { printf "%.3f", raw / 1000 }')"
fi

print -r -- "배터리 건강 스냅샷"
print -r -- "- 설계 용량: ${DESIGN_CAPACITY:-확인 불가} mAh (100%)"
if [[ -n "$RAW_HEALTH" ]]; then
  print -r -- "- 원시 최대 용량: ${RAW_MAX_CAPACITY} mAh (${RAW_HEALTH}% of design)"
else
  print -r -- "- 원시 최대 용량: ${RAW_MAX_CAPACITY:-확인 불가} mAh"
fi
print -r -- "- macOS 최대 용량: ${MACOS_MAX_CAPACITY:-확인 불가}"
print -r -- "- macOS 상태: ${MACOS_CONDITION:-확인 불가}"
print -r -- "- 사이클 수: ${CYCLE_COUNT:-확인 불가}"
print -r -- "- 현재 잔량: ${STATE_OF_CHARGE:-확인 불가}"
print -r -- "- 충전 중: ${CHARGING:-확인 불가}"
print -r -- "- 외부 전원: ${AC_CONNECTED:-확인 불가}"
print -r -- "- 완전 충전: ${FULLY_CHARGED:-확인 불가}"
[[ -n "$TIME_REMAINING" ]] && print -r -- "- 남은 시간: ${TIME_REMAINING}분"
[[ -n "$TEMPERATURE" ]] && print -r -- "- 배터리 온도: ${TEMPERATURE}°C"
[[ -n "$VOLTAGE" ]] && print -r -- "- 전압: ${VOLTAGE}V"
[[ -n "$DAILY_MAX_SOC" ]] && print -r -- "- 컨트롤러 DailyMaxSoc: ${DAILY_MAX_SOC}% (출처는 단정하지 않음)"
print -r -- "- 원시 현재 용량: ${RAW_CURRENT_CAPACITY:-확인 불가} mAh"
