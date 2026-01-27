#!/bin/bash
# Check backend API health

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "==================================="
echo "Backend API Health Check"
echo "==================================="
echo ""

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "Checking Backend API..."
echo "URL: $BACKEND_URL"
echo ""

echo "Port check..."
if command -v nc >/dev/null 2>&1; then
    if nc -z localhost 8000 2>/dev/null; then
        echo "OK: Port 8000 is listening"
    else
        echo "WARN: Port 8000 not listening"
    fi
else
    echo "WARN: nc not installed, skipping port check"
fi
echo ""

echo "Testing API endpoints..."
echo ""

echo "1. Health check (/health):"
curl -s -w "Status: %{http_code}\n" "$BACKEND_URL/health" 2>/dev/null || echo "ERR: No response"
echo ""

echo "2. Root endpoint (/):"
curl -s -w "Status: %{http_code}\n" "$BACKEND_URL/" 2>/dev/null || echo "ERR: No response"
echo ""

echo "3. API Docs (/docs):"
curl -s -w "Status: %{http_code}\n" "$BACKEND_URL/docs" 2>/dev/null | head -1 || echo "ERR: No response"
echo ""

echo "4. Navi endpoint (/api/v1/navi/chat):"
curl -s -X POST "$BACKEND_URL/api/v1/navi/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}' \
  -w "Status: %{http_code}\n" 2>/dev/null || echo "ERR: No response"
echo ""

echo "Backend container logs (last 20 lines):"
echo "-----------------------------------"
docker logs --tail 20 aads-backend 2>/dev/null || echo "ERR: Cannot access docker logs"
echo "-----------------------------------"
