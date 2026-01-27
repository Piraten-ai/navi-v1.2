$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot\..

$exeCandidates = @(
    "build\\Release\\aads_ui.exe",
    "build\\aads_ui.exe"
)

$exe = $exeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $exe) {
    Write-Host "Executable not found. Run build-win.ps1 or tools\\build-qt.bat first."
    exit 1
}

& $exe
