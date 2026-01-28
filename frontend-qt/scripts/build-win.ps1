$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot\..

if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
    Write-Error "cmake not found. Install CMake and ensure it is on PATH."
    exit 1
}

# Locate Qt6 (needed for CMake configure).
# Prefer MSVC kit when available (matches VS BuildTools / Visual Studio generator).
$qt6Candidates = @(
    "E:\Qt\6.10.1\msvc2022_64\lib\cmake\Qt6",
    "E:\Qt\6.10.1\msvc2022_arm64\lib\cmake\Qt6",
    "E:\Qt\6.10.1\mingw_64\lib\cmake\Qt6",
    "E:\Qt\6.10.1\llvm-mingw_64\lib\cmake\Qt6"
)

if ($env:Qt6_DIR -and (Test-Path (Join-Path $env:Qt6_DIR "Qt6Config.cmake"))) {
    $qt6Dir = $env:Qt6_DIR
} else {
    $qt6Dir = $qt6Candidates | Where-Object { Test-Path (Join-Path $_ "Qt6Config.cmake") } | Select-Object -First 1
}

if (-not $qt6Dir) {
    Write-Error @"
Qt6 not found (Qt6Config.cmake).

Fix:
- Install Qt 6 (MSVC 2022 64-bit recommended) via `E:\Qt\MaintenanceTool.exe`, OR
- Set Qt6_DIR, e.g.:
  `$env:Qt6_DIR = 'E:\Qt\6.10.1\msvc2022_64\lib\cmake\Qt6'
"@
    exit 1
}

# Clean build to avoid stale QML cache / qmldir mismatches (can render blank UI).
# NOTE: On Windows the exe is often locked while running.
# We try to stop it first; if clean delete still fails, we fall back to incremental build.
$doClean = $true
if ($env:AADS_CLEAN -ne $null -and $env:AADS_CLEAN -eq "0") {
    $doClean = $false
}

if ($doClean -and (Test-Path "build")) {
    # Best-effort stop running UI so build folder can be cleaned.
    try { Stop-Process -Name "aads_ui" -Force -ErrorAction SilentlyContinue } catch {}
    Start-Sleep -Milliseconds 250

    try {
        Remove-Item -Recurse -Force "build"
    } catch {
        Write-Warning "Could not remove 'build' (likely locked). Continuing with incremental build. Close the UI or set AADS_CLEAN=0 to skip cleaning."
    }
}

cmake -S . -B build -DQt6_DIR="$qt6Dir"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

cmake --build build --config Release
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
