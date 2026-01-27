#!/bin/bash
# Quick fix for backend logging issue

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Fixing backend logging configuration"
echo "===================================="
echo ""

echo "Stopping backend container..."
docker compose stop backend

echo "Rebuilding backend..."
docker compose build --no-cache backend

echo "Starting backend..."
docker compose up -d backend

echo ""
echo "Backend restarted."
echo "Checking status in 10 seconds..."
sleep 10

if docker ps | grep -q aads-backend; then
    echo "Backend is running"

    echo ""
    echo "Last logs:"
    docker compose logs --tail=20 backend

    echo ""
    echo "Testing API..."
    sleep 5
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend API is responding"
        echo ""
        IP_ADDR=$(hostname -I 2>/dev/null | awk '{print $1}')
        IP_ADDR="${IP_ADDR:-localhost}"
        echo "Backend:  http://${IP_ADDR}:8000"
        echo "API Docs: http://${IP_ADDR}:8000/docs"
        echo "Frontend runs on the Raspberry Pi (docker-compose.pi.yml)."
    else
        echo "API not responding yet - check logs:"
        echo "  docker compose logs -f backend"
    fi
else
    echo "Backend failed to start - checking logs..."
    docker compose logs --tail=50 backend
fi
