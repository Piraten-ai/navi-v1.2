#!/bin/bash
# Linting script for AADS project

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "==================================="
echo "Running AADS Linting Checks"
echo "==================================="

echo ""
echo "1. Checking Backend Python Code..."
echo "-----------------------------------"
cd backend

echo "  - Checking for syntax errors..."
python3 -m flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

echo "  - Checking code style..."
python3 -m flake8 app --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

echo "  Backend linting passed."
cd ..

echo ""
echo "2. Checking Frontend TypeScript/React Code..."
echo "----------------------------------------------"
cd frontend

if [ ! -d "node_modules" ]; then
    echo "  - Installing dependencies..."
    npm ci > /dev/null 2>&1
fi

echo "  - Running ESLint..."
npm run lint

echo "  Frontend linting passed."
cd ..

echo ""
echo "==================================="
echo "All linting checks passed."
echo "==================================="
echo ""
echo "The code is ready for deployment."
