# One-button PC simulation (Signal K + bridge + full stack)

$root = Resolve-Path (Join-Path $PSScriptRoot "..\\..")
Set-Location $root

$env:BACKEND_ENV_FILE = "config/backend.env.sim"

Write-Host "Starting dev stack with simulation env..." -ForegroundColor Cyan
docker compose -f docker-compose.dev.yml up -d

Write-Host ""
Write-Host "Stack started." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "Backend:  http://localhost:8001" -ForegroundColor Gray
Write-Host "Signal K: http://localhost:3001" -ForegroundColor Gray
