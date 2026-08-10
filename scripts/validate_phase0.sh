#!/usr/bin/env bash
set -euo pipefail

python_bin="${PYTHON:-python}"

echo "== git whitespace =="
tracked_whitespace="$(git grep -nI -E '[[:blank:]]+$' -- . || true)"
if [[ -n "${tracked_whitespace}" ]]; then
  echo "Tracked files contain trailing whitespace:"
  echo "${tracked_whitespace}"
  exit 1
fi
git diff --check
git diff --cached --check

echo "== bash syntax =="
bash -n scripts/validate_phase0.sh

echo "== ruff lint =="
"${python_bin}" -m ruff check src tests

echo "== tracked generated-file guard =="
tracked_generated="$(
  git ls-files \
    'artifacts/*' \
    'data/attempts/*' \
    'data/screenshots/*' \
    'data/variants/*.yaml' \
    'data/variants/backups/*' \
    'data/variants/promotions/*' \
    'public/assets/local/*' \
    ':(exclude)public/assets/local/.gitkeep' \
    '*.nes' \
    '*.fds' \
    '*.sav' \
    '*.state' \
    '*.fc?' \
    '*.fm2' \
    '*.pyc' \
    '__pycache__/*' \
    '.pytest_cache/*' \
    '*.egg-info/*' \
    '.coverage' \
    'htmlcov/*' || true
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

echo "== active goal contract =="
"${python_bin}" -m smb3_agent goal validate data/goals/world_8_double_whistle.yaml

echo "== active segment catalog =="
"${python_bin}" -m smb3_agent segment validate \
  data/segments/world_8_double_whistle.yaml \
  --goal world_8_double_whistle

echo "== deterministic goal status =="
"${python_bin}" -m smb3_agent goal status world_8_double_whistle

echo "== Mario Route Lab render =="
route_lab_tmp="$(mktemp -d "${TMPDIR:-/tmp}/smb3-route-lab.XXXXXX")"
route_lab_html="${route_lab_tmp}/world_8_double_whistle.html"
cleanup_route_lab() {
  rm -f -- "${route_lab_html}"
  rmdir -- "${route_lab_tmp}"
}
trap cleanup_route_lab EXIT

"${python_bin}" -m smb3_agent lab ui-render --output "${route_lab_html}"
if [[ ! -s "${route_lab_html}" ]]; then
  echo "Mario Route Lab render is empty: ${route_lab_html}"
  exit 1
fi

route_lab_contract=(
  "Mario Route Lab"
  "Run World 8 Route"
  "World 2 Map"
  "First Whistle (World 2)"
  "Warp Zone 5 / 6 / 7"
  "Second Whistle (Warp Zone)"
  "Warp Zone World 8"
  "World 8 Pipe"
  "World 8 Map"
  "primary-button"
  "secondary-button"
  "segmented-control"
  "segment-active"
  "route-item-selected"
  "status-failed"
  "status-learned"
  "status-validation"
)

for expected in "${route_lab_contract[@]}"; do
  if ! grep -Fq -- "${expected}" "${route_lab_html}"; then
    echo "Mario Route Lab render is missing: ${expected}"
    exit 1
  fi
done

echo "Mario Route Lab render contract passed"
