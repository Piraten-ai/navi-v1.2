#!/bin/bash
# Quick script to update and rebuild frontend after settings/dashboard changes

echo "==================================="
echo "NAVI Frontend Update Script"
echo "==================================="
echo ""

# Pull latest changes
echo "[1/4] Pulling latest changes from GitHub..."
git pull

echo ""
echo "[2/4] Stopping containers..."
docker-compose down

echo ""
echo "[3/4] Rebuilding frontend container (this may take a few minutes)..."
docker-compose build --no-cache frontend

echo ""
echo "[4/4] Starting all services..."
docker-compose up -d

echo ""
echo "==================================="
echo "Waiting 10 seconds for services to start..."
sleep 10

echo ""
echo "Testing frontend..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000

echo ""
echo "==================================="
echo "UPDATE COMPLETE!"
echo "==================================="
echo ""
echo "Frontend URL: http://192.168.39.196:3000"
echo ""
echo "New features added:"
echo "  ⚙️  Settings panel (gear icon top-right)"
echo "  📊 Dashboard module with customizable gauges"
echo "  💬 Hey Listen! prompts (can be toggled in settings)"
echo ""
echo "To view logs: docker-compose logs -f frontend"
echo "==================================="
