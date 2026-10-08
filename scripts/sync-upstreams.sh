#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

git submodule update --init --recursive
git submodule update --remote --merge

echo
echo "Review the changes before committing:"
git diff --submodule=log
