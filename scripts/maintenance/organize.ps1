# Archive organization script (current structure)

$root = Resolve-Path (Join-Path $PSScriptRoot "..\\..")
Set-Location $root

$dirs = @(
  "docs\current",
  "docs\guides",
  "docs\reference",
  "docs\archived\GENERAL",
  "docs\archived\TECHNICAL",
  "docs\archived\INTEGRATIONS",
  "docs\hardware-manuals",
  "scripts"
)

foreach ($dir in $dirs) {
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

function Move-IfExists($file, $dest) {
  if (Test-Path $file) {
    Move-Item -Path $file -Destination $dest -Force
  }
}

$currentFiles = @(
  "AADS_WIKI.md",
  "AADS_DEPLOYMENT_READY.md",
  "COMPLETE_TECHNICAL_REFERENCE.md",
  "BRIDGE_SPEC.md",
  "HARDWARE_PLAN.md",
  "PROGRESS_LOG.md"
)

$guidesFiles = @(
  "DOCUMENTATION_INDEX.md",
  "PRODUCTION_DEPLOYMENT.md",
  "TESTING_GUIDE.md",
  "VERIFICATION_CHECKLIST.md",
  "RUN_TESTS_GUIDE.md",
  "TESTING_QUICK_START.md"
)

$referenceFiles = @(
  "GUI_REDESIGN.md",
  "GITHUB_ACTIONS_DOCKER.md",
  "MAP_DATA.md"
)

$generalFiles = @(
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
  "PHASE_2_TESTS_COMPLETE.md"
)

$technicalFiles = @(
  "TESTING_COMPLETE.md",
  "UPDATES_QUICK_REFERENCE.md",
  "UPDATE_AND_FIX.md",
  "QUICK_SUMMARY_IMPROVEMENTS.md",
  "NAVI_RESPONSE_FIX.md",
  "TESTING_UPGRADE_SUMMARY.md",
  "STRUCTURE.md",
  "STABLE_DIFFUSION_INTEGRATION.md"
)

$integrationsFiles = @(
  "SIGNAL_K_INTEGRATION_COMPLETE.md",
  "FRONTEND_IMPROVEMENTS_2026-01-23.md",
  "TEST_IMPROVEMENTS_SUMMARY.md"
)

foreach ($file in $currentFiles) { Move-IfExists $file "docs\current" }
foreach ($file in $guidesFiles) { Move-IfExists $file "docs\guides" }
foreach ($file in $referenceFiles) { Move-IfExists $file "docs\reference" }
foreach ($file in $generalFiles) { Move-IfExists $file "docs\archived\GENERAL" }
foreach ($file in $technicalFiles) { Move-IfExists $file "docs\archived\TECHNICAL" }
foreach ($file in $integrationsFiles) { Move-IfExists $file "docs\archived\INTEGRATIONS" }

Write-Host "Organization complete."
