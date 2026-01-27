#!/bin/bash
# Complete diagnostic and fix for Ollama connection

echo "🔍 OLLAMA CONNECTION DIAGNOSTIC"
echo "================================"
echo ""

# Get IP
JETSON_IP=$(hostname -I | awk '{print $1}')

echo "1. Checking Ollama container status..."
if docker ps | grep -q aads-navi-ollama; then
    echo "✅ Ollama container is running"
    
    # Check if model is loaded
    echo ""
    echo "2. Checking Ollama model..."
    if docker exec aads-navi-ollama ollama list 2>/dev/null | grep -q llama; then
        echo "✅ Ollama model loaded:"
        docker exec aads-navi-ollama ollama list
    else
        echo "❌ No Ollama model found!"
        echo "   Loading llama3.2..."
        docker exec aads-navi-ollama ollama pull llama3.2
    fi
    
    echo ""
    echo "3. Testing Ollama API..."
    if curl -f -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo "✅ Ollama API responding"
        curl -s http://localhost:11434/api/version | head -1
    else
        echo "❌ Ollama API not responding"
    fi
    
    echo ""
    echo "4. Testing Ollama from backend container..."
    if docker exec aads-backend curl -f -s http://navi:11434/api/version > /dev/null 2>&1; then
        echo "✅ Backend can reach Ollama"
    else
        echo "❌ Backend cannot reach Ollama"
        echo "   Checking network..."
        docker exec aads-backend ping -c 2 navi
    fi
else
    echo "❌ Ollama container is NOT running"
    echo "   Starting Ollama..."
    docker compose up -d navi
    sleep 10
    echo "   Pulling model..."
    docker exec aads-navi-ollama ollama pull llama3.2
fi

echo ""
echo "5. Checking Backend API..."
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API responding"
else
    echo "❌ Backend API not responding"
fi

echo ""
echo "6. Checking WebSocket in docker-compose.yml..."
CURRENT_WS=$(grep "VITE_WS_URL" docker-compose.yml | head -1)
echo "   Current: $CURRENT_WS"
if echo "$CURRENT_WS" | grep -q "localhost"; then
    echo "   ❌ Still using localhost - needs to be $JETSON_IP"
    NEEDS_FIX=true
else
    echo "   ✅ Using correct IP"
    NEEDS_FIX=false
fi

echo ""
echo "7. Checking frontend build..."
if docker exec aads-frontend test -f /usr/share/nginx/html/index.html 2>/dev/null; then
    echo "✅ Frontend files present"
    
    # Check if the built files have the correct WebSocket URL
    echo ""
    echo "8. Checking WebSocket URL in built frontend..."
    WS_IN_BUILD=$(docker exec aads-frontend grep -r "ws://.*:8000/ws" /usr/share/nginx/html/ 2>/dev/null | head -1)
    if [ -n "$WS_IN_BUILD" ]; then
        echo "   Found: $WS_IN_BUILD"
        if echo "$WS_IN_BUILD" | grep -q "localhost"; then
            echo "   ❌ Frontend was built with localhost - needs rebuild"
            NEEDS_REBUILD=true
        else
            echo "   ✅ Frontend has correct WebSocket URL"
            NEEDS_REBUILD=false
        fi
    else
        echo "   ⚠️  Could not find WebSocket URL in build"
        NEEDS_REBUILD=true
    fi
else
    echo "❌ Frontend files missing"
    NEEDS_REBUILD=true
fi

echo ""
echo "================================"
echo "SUMMARY"
echo "================================"

if [ "$NEEDS_FIX" = true ] || [ "$NEEDS_REBUILD" = true ]; then
    echo ""
    echo "⚠️  Issues detected. Applying fixes..."
    echo ""
    
    if [ "$NEEDS_FIX" = true ]; then
        echo "Fixing docker-compose.yml..."
        
        # Backup
        cp docker-compose.yml docker-compose.yml.backup.$(date +%s)
        
        # Fix WebSocket URL
        sed -i "s|VITE_WS_URL=ws://localhost:8000/ws|VITE_WS_URL=ws://${JETSON_IP}:8000/ws|g" docker-compose.yml
        sed -i "s|VITE_API_URL=http://localhost:8000|VITE_API_URL=http://${JETSON_IP}:8000|g" docker-compose.yml
        sed -i "s|VITE_SIGNALK_HOST=http://localhost:3001|VITE_SIGNALK_HOST=http://${JETSON_IP}:3001|g" docker-compose.yml
        
        echo "✅ Updated docker-compose.yml"
    fi
    
    if [ "$NEEDS_REBUILD" = true ]; then
        echo ""
        echo "Rebuilding frontend..."
        docker compose stop frontend
        docker compose build --no-cache frontend
        docker compose up -d frontend
        
        echo ""
        echo "Waiting for frontend to start..."
        sleep 15
        
        echo "✅ Frontend rebuilt"
    fi
    
    echo ""
    echo "🎉 FIXES APPLIED!"
else
    echo ""
    echo "✅ All checks passed!"
fi

echo ""
echo "================================"
echo "TEST YOUR CONNECTION"
echo "================================"
echo ""
echo "Open your browser to:"
echo "   http://${JETSON_IP}:3000"
echo ""
echo "Then:"
echo "1. Go to the NAVI module (AI chat)"
echo "2. Type a message to Ollama"
echo "3. Check browser console (F12) for WebSocket errors"
echo ""
echo "If still not working, check logs:"
echo "   docker compose logs -f backend | grep -i ollama"
echo "   docker compose logs -f frontend"
echo ""
echo "Manual Ollama test:"
echo "   curl http://localhost:11434/api/generate -d '{\"model\":\"llama3.2\",\"prompt\":\"Hello\"}'"
echo ""
