#!/bin/zsh
set -u

user_dir="${USER_HOME:-${HOME:-$(cd ~ && pwd)}}"

echo "== Filesystem =="
df -h / /System/Volumes/Data 2>/dev/null || true

echo ""
echo "== Small home roots (size only) =="
for top_dir in Desktop Movies Music Pictures; do
  if [[ -d "$user_dir/$top_dir" ]]; then
    du -sh "$user_dir/$top_dir" 2>/dev/null || true
  fi
done | sort -h
echo "Documents, Downloads, and Library are omitted from the default scan; use --deep when approved."

for target_dir in \
  "$user_dir/Library/Developer" \
  "$user_dir/Library/Caches"; do
  if [[ -d "$target_dir" ]]; then
    echo ""
    echo "== $target_dir =="
    du -xhd1 "$target_dir" 2>/dev/null | sort -h | tail -n 30 || true
  fi
done

if [[ "${1:-}" == "--deep" ]]; then
  for target_dir in "$user_dir/Downloads" "$user_dir/Documents"; do
    if [[ -d "$target_dir" ]]; then
      echo ""
      echo "== $target_dir (deep scan) =="
      du -xhd1 "$target_dir" 2>/dev/null | sort -h | tail -n 30 || true
    fi
  done

  echo ""
  echo "== Large files over 1 GiB in Downloads/Documents =="
  for target_dir in "$user_dir/Downloads" "$user_dir/Documents"; do
    if [[ -d "$target_dir" ]]; then
      find "$target_dir" -type f -size +1G -print0 2>/dev/null \
        | xargs -0 -I{} du -sh "{}" 2>/dev/null
    fi
  done | sort -h || true
fi

echo ""
echo "== APFS local snapshots =="
tmutil listlocalsnapshots / 2>&1 || true
