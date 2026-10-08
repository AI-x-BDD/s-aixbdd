#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

sources=(
  "skills/transcript-deep-learning"
  "skills/git-commit-draft"
  "skills/course-transcript-notes"
  "skills/review-article-stepwise"
  "upstreams/asd-ste100-skill"
  "upstreams/no-ai-slop/skills/no-ai-slop"
  "upstreams/shuorenhua"
)

targets=(
  "$HOME/.agents/skills"
  "$HOME/.claude/skills"
)

link_skill() {
  local source=$1
  local target_dir=$2
  local name target

  name=$(basename "$source")
  target="$target_dir/$name"

  if [[ ! -f "$source/SKILL.md" ]]; then
    echo "Missing SKILL.md: $source" >&2
    return 1
  fi

  mkdir -p "$target_dir"

  if [[ -e "$target" && ! -L "$target" ]]; then
    echo "Preserved existing directory: $target" >&2
    return 0
  fi

  ln -sfn "$source" "$target"
  echo "$target -> $source"
}

for relative_source in "${sources[@]}"; do
  source="$repo_root/$relative_source"
  for target_dir in "${targets[@]}"; do
    link_skill "$source" "$target_dir"
  done
done
