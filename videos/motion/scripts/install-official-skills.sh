#!/usr/bin/env bash
# 下載固定 revision 的 remotion-dev/skills 到 videos/.cache/official-skills/（不納入版控）。
# 上游 repo 未附授權檔，原文不收錄於本 repo；以逐檔 SHA-256 清單確認取得的是同一份內容。
set -euo pipefail

REV=1441a11e95db35443bd76bb318386c0d3ca00053
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HERE/../.cache/official-skills/remotion-dev-skills/$REV"
MANIFEST="$HERE/official-skills.sha256"

if [[ -f "$DEST/skills/remotion-best-practices/SKILL.md" ]]; then
  (cd "$DEST" && shasum -a 256 -c --quiet "$MANIFEST")
  echo "已存在且雜湊相符：$DEST"
  exit 0
fi

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
curl -fsSL "https://codeload.github.com/remotion-dev/skills/tar.gz/$REV" -o "$work/skills.tgz"
mkdir -p "$work/x"
tar -xzf "$work/skills.tgz" -C "$work/x" --strip-components=1
(cd "$work/x" && shasum -a 256 -c --quiet "$MANIFEST")
mkdir -p "$(dirname "$DEST")"
mv "$work/x" "$DEST"
echo "已安裝：$DEST"
echo "入口：$DEST/skills/remotion-best-practices/SKILL.md"
