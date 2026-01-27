#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)

dirs_to_create = [
    "docs/current",
    "docs/guides",
    "docs/reference",
    "docs/archived/GENERAL",
    "docs/archived/TECHNICAL",
    "docs/archived/INTEGRATIONS",
    "docs/hardware-manuals",
    "scripts",
]

for d in dirs_to_create:
    Path(d).mkdir(parents=True, exist_ok=True)

current_files = [
    "AADS_WIKI.md",
    "AADS_DEPLOYMENT_READY.md",
    "COMPLETE_TECHNICAL_REFERENCE.md",
    "BRIDGE_SPEC.md",
    "HARDWARE_PLAN.md",
    "PROGRESS_LOG.md",
]

guides_files = [
    "DOCUMENTATION_INDEX.md",
    "PRODUCTION_DEPLOYMENT.md",
    "TESTING_GUIDE.md",
    "VERIFICATION_CHECKLIST.md",
    "RUN_TESTS_GUIDE.md",
    "TESTING_QUICK_START.md",
]

reference_files = [
    "GUI_REDESIGN.md",
    "GITHUB_ACTIONS_DOCKER.md",
    "MAP_DATA.md",
]

general_files = [
    "CHANGES_SUMMARY.md",
    "FINAL_DELIVERY_SUMMARY.md",
    "FINAL_FIX_SUMMARY.md",
    "FIXES_APPLIED_2026-01-23.md",
    "ALL_FIXES_COMPLETE.md",
    "UPDATES_COMPLETION_REPORT.md",
    "JETSON_DEPLOYMENT_READY.md",
    "HOTFIX_REACT_ERROR_31.md",
    "IMPLEMENTATION_SUMMARY.md",
    "IMPLEMENTATION_SUMMARY_OLLAMA_FRONTEND.md",
    "FRONTEND_FIXES_2026-01-23.md",
    "DOCKER_BUILD_FIX.md",
    "DOCKER_BOTS_FIX_SUMMARY.md",
    "PHASE_2_TESTS_COMPLETE.md",
]

technical_files = [
    "TESTING_COMPLETE.md",
    "UPDATES_QUICK_REFERENCE.md",
    "UPDATE_AND_FIX.md",
    "QUICK_SUMMARY_IMPROVEMENTS.md",
    "NAVI_RESPONSE_FIX.md",
    "TESTING_UPGRADE_SUMMARY.md",
    "STRUCTURE.md",
    "STABLE_DIFFUSION_INTEGRATION.md",
]

integrations_files = [
    "SIGNAL_K_INTEGRATION_COMPLETE.md",
    "FRONTEND_IMPROVEMENTS_2026-01-23.md",
    "TEST_IMPROVEMENTS_SUMMARY.md",
]

def move_files(files, dest):
    for f in files:
        if os.path.exists(f):
            shutil.move(f, os.path.join(dest, f))

move_files(current_files, "docs/current")
move_files(guides_files, "docs/guides")
move_files(reference_files, "docs/reference")
move_files(general_files, "docs/archived/GENERAL")
move_files(technical_files, "docs/archived/TECHNICAL")
move_files(integrations_files, "docs/archived/INTEGRATIONS")

print("Reorganization complete.")
