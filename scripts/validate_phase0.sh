#!/usr/bin/env bash
set -euo pipefail

python_bin="${PYTHON:-python}"

echo "== git whitespace =="
git diff --check

echo "== tracked generated-file guard =="
tracked_generated="$(
  git ls-files \
    'artifacts/*' \
    'data/attempts/*' \
    'data/screenshots/*' \
    '*.nes' \
    '*.sav' \
    '*.state' \
    '*.fc?' \
    '*.fm2' \
    '*.pyc' \
    '__pycache__/*' \
    '.pytest_cache/*' || true
)"

if [[ -n "${tracked_generated}" ]]; then
  echo "Generated or local-only files are tracked:"
  echo "${tracked_generated}"
  exit 1
fi

echo "== ignored runtime artifact visibility =="
git status --short --ignored

echo "== tests =="
"${python_bin}" -m pytest -q

