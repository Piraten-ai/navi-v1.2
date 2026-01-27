$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot\..

if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
    Write-Error "cmake not found. Install CMake and ensure it is on PATH."
    exit 1
}

cmake -S . -B build
cmake --build build --config Release
