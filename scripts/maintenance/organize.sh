#!/bin/bash
# Archive organization script (current structure)

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

mkdir -p docs/current docs/guides docs/reference \
  docs/archived/GENERAL docs/archived/TECHNICAL docs/archived/INTEGRATIONS \
  docs/hardware-manuals scripts

move_if_exists() {
  local src="$1"
  local dst="$2"
  if [ -f "$src" ]; then
    mv "$src" "$dst/"
  fi
}

current_files=(
  AADS_WIKI.md
  AADS_DEPLOYMENT_READY.md
  COMPLETE_TECHNICAL_REFERENCE.md
  BRIDGE_SPEC.md
  HARDWARE_PLAN.md
  PROGRESS_LOG.md
)

guides_files=(
  DOCUMENTATION_INDEX.md
  PRODUCTION_DEPLOYMENT.md
  TESTING_GUIDE.md
  VERIFICATION_CHECKLIST.md
  RUN_TESTS_GUIDE.md
  TESTING_QUICK_START.md
)

reference_files=(
  GUI_REDESIGN.md
  GITHUB_ACTIONS_DOCKER.md
  MAP_DATA.md
)

general_files=(
  CHANGES_SUMMARY.md
  FINAL_DELIVERY_SUMMARY.md
  FINAL_FIX_SUMMARY.md
  FIXES_APPLIED_2026-01-23.md
  ALL_FIXES_COMPLETE.md
  UPDATES_COMPLETION_REPORT.md
  JETSON_DEPLOYMENT_READY.md
  HOTFIX_REACT_ERROR_31.md
  IMPLEMENTATION_SUMMARY.md
  IMPLEMENTATION_SUMMARY_OLLAMA_FRONTEND.md
  FRONTEND_FIXES_2026-01-23.md
  DOCKER_BUILD_FIX.md
  DOCKER_BOTS_FIX_SUMMARY.md
  PHASE_2_TESTS_COMPLETE.md
)

technical_files=(
  TESTING_COMPLETE.md
  UPDATES_QUICK_REFERENCE.md
  UPDATE_AND_FIX.md
  QUICK_SUMMARY_IMPROVEMENTS.md
  NAVI_RESPONSE_FIX.md
  TESTING_UPGRADE_SUMMARY.md
  STRUCTURE.md
  STABLE_DIFFUSION_INTEGRATION.md
)

integrations_files=(
  SIGNAL_K_INTEGRATION_COMPLETE.md
  FRONTEND_IMPROVEMENTS_2026-01-23.md
  TEST_IMPROVEMENTS_SUMMARY.md
)

for f in "${current_files[@]}"; do
  move_if_exists "$f" "docs/current"
done

for f in "${guides_files[@]}"; do
  move_if_exists "$f" "docs/guides"
done

for f in "${reference_files[@]}"; do
  move_if_exists "$f" "docs/reference"
done

for f in "${general_files[@]}"; do
  move_if_exists "$f" "docs/archived/GENERAL"
done

for f in "${technical_files[@]}"; do
  move_if_exists "$f" "docs/archived/TECHNICAL"
done

for f in "${integrations_files[@]}"; do
  move_if_exists "$f" "docs/archived/INTEGRATIONS"
done

echo "Organization complete."
