#!/usr/bin/env bash

set -euo pipefail

SKILL_NAME="toss-frontend-fundamentals"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/skills/${SKILL_NAME}"
FORCE=0
TARGET_SPEC="all"

usage() {
  cat <<'EOF'
Usage: install.sh [--target TARGET] [--force]

Install Toss Frontend Fundamentals into an agent's user-level skills directory.

Targets:
  codex      ${CODEX_HOME:-$HOME/.codex}/skills
  claude     ${CLAUDE_HOME:-$HOME/.claude}/skills
  hermes     ${HERMES_HOME:-$HOME/.hermes}/skills
  openclaw   ${OPENCLAW_HOME:-$HOME/.openclaw}/skills
  all        Install into all four targets (default)

Options:
  --force    Move an existing installation to a timestamped backup first
  --help     Show this help
EOF
}

fail() {
  printf 'error: %s\n' "$1" >&2
  exit 1
}

skill_parent_for() {
  case "$1" in
    codex) printf '%s/skills' "${CODEX_HOME:-${HOME}/.codex}" ;;
    claude) printf '%s/skills' "${CLAUDE_HOME:-${HOME}/.claude}" ;;
    hermes) printf '%s/skills' "${HERMES_HOME:-${HOME}/.hermes}" ;;
    openclaw) printf '%s/skills' "${OPENCLAW_HOME:-${HOME}/.openclaw}" ;;
    *) fail "알 수 없는 설치 대상: $1" ;;
  esac
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      [ "$#" -ge 2 ] || fail "--target에는 codex, claude, hermes, openclaw 또는 all이 필요합니다."
      TARGET_SPEC="$2"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail "알 수 없는 옵션: $1"
      ;;
  esac
done

[ -d "$SOURCE_DIR" ] || fail "Skill 원본 디렉터리를 찾을 수 없습니다: $SOURCE_DIR"

case "$TARGET_SPEC" in
  all) TARGETS="codex claude hermes openclaw" ;;
  codex|claude|hermes|openclaw) TARGETS="$TARGET_SPEC" ;;
  *) fail "--target 값은 codex, claude, hermes, openclaw 또는 all이어야 합니다." ;;
esac

for target in $TARGETS; do
  parent_dir="$(skill_parent_for "$target")"
  destination="${parent_dir}/${SKILL_NAME}"
  if { [ -e "$destination" ] || [ -L "$destination" ]; } && [ "$FORCE" -ne 1 ]; then
    fail "이미 설치된 Skill이 있습니다: $destination (덮어쓰려면 --force 사용)"
  fi
done

for target in $TARGETS; do
  parent_dir="$(skill_parent_for "$target")"
  destination="${parent_dir}/${SKILL_NAME}"
  mkdir -p "$parent_dir"

  if { [ -e "$destination" ] || [ -L "$destination" ]; } && [ "$FORCE" -eq 1 ]; then
    backup="${destination}.backup.$(date '+%Y%m%d%H%M%S')"
    mv "$destination" "$backup"
    printf '기존 설치를 백업했습니다: %s\n' "$backup"
  fi

  cp -R "$SOURCE_DIR" "$destination"
  printf '설치했습니다: %s -> %s\n' "$target" "$destination"
done

printf '완료: %s\n' "$SKILL_NAME"
