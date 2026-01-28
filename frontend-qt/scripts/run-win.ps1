$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot\..

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

if ($qt6Dir) {
    # Qt6_DIR looks like: <QtKit>\lib\cmake\Qt6  → kit root is 3 levels up.
    $qtRoot = Resolve-Path (Join-Path $qt6Dir "..\..\..") | Select-Object -ExpandProperty Path
    $env:Path = "$qtRoot\bin;$env:Path"
    $env:QT_PLUGIN_PATH = "$qtRoot\plugins"
    $env:QML_IMPORT_PATH = "$qtRoot\qml"
}

$exeCandidates = @(
    "build\\Release\\aads_ui.exe",
    "build\\aads_ui.exe"
)

$exe = $exeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $exe) {
    Write-Host "Executable not found. Run build-win.ps1 or tools\\build-qt.bat first."
    exit 1
}

Write-Host "Starting $exe"
& $exe

if ($LASTEXITCODE -ne 0) {
    Write-Host "aads_ui exited with code $LASTEXITCODE"
    $logCandidates = @(
        (Join-Path (Split-Path $exe -Parent) "aads_ui.log"),
        "build\aads_ui.log",
        "build\Release\aads_ui.log"
    )
    $log = $logCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($log) {
        Write-Host "Last log lines ($log):"
        Get-Content $log -Tail 60
    } else {
        Write-Host "No aads_ui.log found. If you got a missing DLL popup, Qt bin is likely not on PATH."
        if ($qt6Dir) {
            Write-Host "Using Qt from: $qtRoot"
        } else {
            Write-Host "Qt6_DIR is not set and Qt was not auto-detected."
        }
    }
    exit $LASTEXITCODE
}
