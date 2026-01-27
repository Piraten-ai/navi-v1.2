#!/bin/bash
# Update and rebuild the Raspberry Pi frontend

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "NAVI Frontend Update (Pi)"
echo "========================="
echo ""

echo "[1/4] Pulling latest changes..."
git pull

echo ""
echo "[2/4] Stopping frontend..."
docker compose -f docker-compose.pi.yml down

echo ""
echo "[3/4] Rebuilding frontend..."
docker compose -f docker-compose.pi.yml build --no-cache frontend

echo ""
echo "[4/4] Starting frontend..."
docker compose -f docker-compose.pi.yml up -d frontend

echo ""
echo "Waiting 10 seconds for services to start..."
sleep 10

echo ""
echo "Testing frontend..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000

echo ""
echo "Update complete."
echo "Frontend URL: http://localhost:3000"
echo "Logs: docker compose -f docker-compose.pi.yml logs -f frontend"
