#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)

dirs = [
    "docs\\current",
    "docs\\guides",
    "docs\\reference",
    "docs\\archived\\GENERAL",
    "docs\\archived\\TECHNICAL",
    "docs\\archived\\INTEGRATIONS",
    "docs\\hardware-manuals",
    "scripts",
]

for d in dirs:
    subprocess.run(f'mkdir "{d}"', shell=True)

moves = [
    ("AADS_WIKI.md", "docs\\current\\"),
    ("AADS_DEPLOYMENT_READY.md", "docs\\current\\"),
    ("COMPLETE_TECHNICAL_REFERENCE.md", "docs\\current\\"),
    ("BRIDGE_SPEC.md", "docs\\current\\"),
    ("HARDWARE_PLAN.md", "docs\\current\\"),
    ("PROGRESS_LOG.md", "docs\\current\\"),
    ("DOCUMENTATION_INDEX.md", "docs\\guides\\"),
    ("PRODUCTION_DEPLOYMENT.md", "docs\\guides\\"),
    ("TESTING_GUIDE.md", "docs\\guides\\"),
    ("VERIFICATION_CHECKLIST.md", "docs\\guides\\"),
    ("RUN_TESTS_GUIDE.md", "docs\\guides\\"),
    ("TESTING_QUICK_START.md", "docs\\guides\\"),
    ("GUI_REDESIGN.md", "docs\\reference\\"),
    ("GITHUB_ACTIONS_DOCKER.md", "docs\\reference\\"),
    ("MAP_DATA.md", "docs\\reference\\"),
    ("CHANGES_SUMMARY.md", "docs\\archived\\GENERAL\\"),
    ("FINAL_DELIVERY_SUMMARY.md", "docs\\archived\\GENERAL\\"),
    ("FINAL_FIX_SUMMARY.md", "docs\\archived\\GENERAL\\"),
    ("FIXES_APPLIED_2026-01-23.md", "docs\\archived\\GENERAL\\"),
    ("ALL_FIXES_COMPLETE.md", "docs\\archived\\GENERAL\\"),
    ("UPDATES_COMPLETION_REPORT.md", "docs\\archived\\GENERAL\\"),
    ("JETSON_DEPLOYMENT_READY.md", "docs\\archived\\GENERAL\\"),
    ("HOTFIX_REACT_ERROR_31.md", "docs\\archived\\GENERAL\\"),
    ("IMPLEMENTATION_SUMMARY.md", "docs\\archived\\GENERAL\\"),
    ("IMPLEMENTATION_SUMMARY_OLLAMA_FRONTEND.md", "docs\\archived\\GENERAL\\"),
    ("FRONTEND_FIXES_2026-01-23.md", "docs\\archived\\GENERAL\\"),
    ("DOCKER_BUILD_FIX.md", "docs\\archived\\GENERAL\\"),
    ("DOCKER_BOTS_FIX_SUMMARY.md", "docs\\archived\\GENERAL\\"),
    ("PHASE_2_TESTS_COMPLETE.md", "docs\\archived\\GENERAL\\"),
    ("TESTING_COMPLETE.md", "docs\\archived\\TECHNICAL\\"),
    ("UPDATES_QUICK_REFERENCE.md", "docs\\archived\\TECHNICAL\\"),
    ("UPDATE_AND_FIX.md", "docs\\archived\\TECHNICAL\\"),
    ("QUICK_SUMMARY_IMPROVEMENTS.md", "docs\\archived\\TECHNICAL\\"),
    ("NAVI_RESPONSE_FIX.md", "docs\\archived\\TECHNICAL\\"),
    ("TESTING_UPGRADE_SUMMARY.md", "docs\\archived\\TECHNICAL\\"),
    ("STRUCTURE.md", "docs\\archived\\TECHNICAL\\"),
    ("STABLE_DIFFUSION_INTEGRATION.md", "docs\\archived\\TECHNICAL\\"),
    ("SIGNAL_K_INTEGRATION_COMPLETE.md", "docs\\archived\\INTEGRATIONS\\"),
    ("FRONTEND_IMPROVEMENTS_2026-01-23.md", "docs\\archived\\INTEGRATIONS\\"),
    ("TEST_IMPROVEMENTS_SUMMARY.md", "docs\\archived\\INTEGRATIONS\\"),
]

for src, dst in moves:
    if os.path.exists(src):
        subprocess.run(f'move "{src}" "{dst}"', shell=True)

print("Reorganization complete.")
