#!/bin/bash
# Linting script for AADS project

set -euo pipefail

set -e

echo "==================================="
echo "Running AADS Linting Checks"
echo "==================================="

# Backend linting
echo ""
echo "1. Checking Backend Python Code..."
echo "-----------------------------------"
cd backend

# Check for syntax errors
echo "  - Checking for syntax errors..."
python3 -m flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

# Check code style
echo "  - Checking code style..."
python3 -m flake8 app --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

echo "  ✓ Backend linting passed!"

cd ..

# Frontend linting
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

echo "  ✓ Frontend linting passed!"

cd ..

echo ""
echo "==================================="
echo "✓ All Linting Checks Passed!"
echo "==================================="
echo ""
echo "The code is ready for deployment."
