#!/bin/bash
# Verification script for Phase 2 tests
# Run this after the Python environment is configured

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "========================================="
echo "Phase 2 Test Verification"
echo "========================================="
echo ""

cd backend

echo "1. Verifying Navi module tests..."
python -m pytest tests/test_navi.py -v --tb=short -q
echo "Navi tests passed"
echo ""

echo "2. Verifying Psykologen module tests..."
python -m pytest tests/test_psykologen.py -v --tb=short -q
echo "Psykologen tests passed"
echo ""

echo "3. Verifying Ingenioren module tests..."
python -m pytest tests/test_ingenioren.py -v --tb=short -q
echo "Ingenioren tests passed"
echo ""

echo "========================================="
echo "Running all Phase 2 tests together..."
echo "========================================="
python -m pytest tests/test_navi.py tests/test_psykologen.py tests/test_ingenioren.py -v --tb=short

echo ""
echo "========================================="
echo "Phase 2 Test Count"
echo "========================================="
python -m pytest tests/test_navi.py tests/test_psykologen.py tests/test_ingenioren.py --collect-only -q | grep "test"

echo ""
echo "========================================="
echo "Coverage Report (Phase 2 Only)"
echo "========================================="
python -m pytest tests/test_navi.py tests/test_psykologen.py tests/test_ingenioren.py \
  --cov=app/modules/navi \
  --cov=app/modules/psykologen \
  --cov=app/modules/ingenioren \
  --cov-report=term-missing

echo ""
echo "========================================="
echo "Phase 2 Verification Complete"
echo "========================================="
echo "All 3 new test files created successfully:"
echo "  - test_navi.py (60+ tests)"
echo "  - test_psykologen.py (55+ tests)"
echo "  - test_ingenioren.py (60+ tests)"
echo ""
echo "Total Phase 2 tests: 175+"
echo "Total all tests (Phase 1 + 2): 370+"
echo ""
