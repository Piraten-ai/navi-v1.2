#!/bin/bash
# Quick fix for backend logging issue

echo "🔧 Fixing Backend Logging Configuration"
echo "========================================"
echo ""

# Stop backend
echo "Stopping backend container..."
docker compose stop backend

# Rebuild backend only (no cache to ensure fresh build)
echo "Rebuilding backend..."
docker compose build --no-cache backend

# Start backend
echo "Starting backend..."
docker compose up -d backend

echo ""
echo "✅ Backend fixed and restarted!"
echo ""
echo "Checking status in 10 seconds..."
sleep 10

# Check if it's running
if docker ps | grep -q aads-backend; then
    echo "✅ Backend is RUNNING"
    
    # Show last 20 lines of logs
    echo ""
    echo "Last logs:"
    docker compose logs --tail=20 backend
    
    # Test the API
    echo ""
    echo "Testing API..."
    sleep 5
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API is RESPONDING"
        echo ""
        echo "🎉 All services ready!"
        echo "   Frontend: http://$(hostname -I | awk '{print $1}'):3000"
        echo "   Backend:  http://$(hostname -I | awk '{print $1}'):8000"
    else
        echo "⚠️  API not responding yet - check logs:"
        echo "   docker compose logs -f backend"
    fi
else
    echo "❌ Backend failed to start - checking logs..."
    docker compose logs --tail=50 backend
fi
