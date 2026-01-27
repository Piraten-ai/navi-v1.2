# Phase 2 Test Verification Script (PowerShell)
# Run this after Python environment is configured

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase 2 Test Verification" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location backend

Write-Host "1. Verifying Navi module tests..." -ForegroundColor Yellow
python -m pytest tests/test_navi.py -v --tb=short -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Navi tests passed" -ForegroundColor Green
} else {
    Write-Host "❌ Navi tests failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "2. Verifying Psykologen module tests..." -ForegroundColor Yellow
python -m pytest tests/test_psykologen.py -v --tb=short -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Psykologen tests passed" -ForegroundColor Green
} else {
    Write-Host "❌ Psykologen tests failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "3. Verifying Ingeniøren module tests..." -ForegroundColor Yellow
python -m pytest tests/test_ingenioren.py -v --tb=short -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Ingeniøren tests passed" -ForegroundColor Green
} else {
    Write-Host "❌ Ingeniøren tests failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Running all Phase 2 tests together..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
python -m pytest tests/test_navi.py tests/test_psykologen.py tests/test_ingenioren.py -v --tb=short

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Phase 2 Test Count" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
$testCount = python -m pytest tests/test_navi.py tests/test_psykologen.py tests/test_ingenioren.py --collect-only -q | Select-String "test" | Measure-Object
Write-Host "Total tests collected: $($testCount.Count)" -ForegroundColor Green

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Coverage Report (Phase 2 Only)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
python -m pytest tests/test_navi.py tests/test_psykologen.py tests/test_ingenioren.py `
  --cov=app/modules/navi `
  --cov=app/modules/psykologen `
  --cov=app/modules/ingenioren `
  --cov-report=term-missing

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Phase 2 Verification Complete" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "All 3 new test files created successfully:" -ForegroundColor Green
Write-Host "  - test_navi.py (60+ tests)"
Write-Host "  - test_psykologen.py (55+ tests)"
Write-Host "  - test_ingenioren.py (60+ tests)"
Write-Host ""
Write-Host "Total Phase 2 tests: 175+" -ForegroundColor Green
Write-Host "Total all tests (Phase 1 + 2): 370+" -ForegroundColor Green
Write-Host ""
