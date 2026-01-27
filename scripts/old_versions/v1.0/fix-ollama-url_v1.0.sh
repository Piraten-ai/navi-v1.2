#!/bin/bash
# Fix Ollama URL in backend environment

echo "🔧 Fixing Backend Ollama Connection"
echo "===================================="
echo ""

echo "Current OLLAMA_BASE_URL in docker-compose.yml:"
grep "OLLAMA_BASE_URL" docker-compose.yml

echo ""
echo "Updating to use Docker service name 'navi'..."

# Backup
cp docker-compose.yml docker-compose.yml.backup.ollama

# Fix the OLLAMA_BASE_URL
sed -i 's|OLLAMA_BASE_URL=http://localhost:11434|OLLAMA_BASE_URL=http://navi:11434|g' docker-compose.yml

echo ""
echo "Updated:"
grep "OLLAMA_BASE_URL" docker-compose.yml

echo ""
echo "Restarting backend..."
docker compose stop backend
docker compose up -d backend

echo ""
echo "Waiting for backend to start..."
sleep 10

echo ""
echo "Testing Ollama connection from backend..."
if docker exec aads-backend curl -f -s http://navi:11434/api/version > /dev/null 2>&1; then
    echo "✅ Backend can now reach Ollama!"
    
    echo ""
    echo "Testing chat..."
    docker exec aads-backend curl -s http://navi:11434/api/generate -d '{"model":"llama3.2","prompt":"Hello","stream":false}' | head -5
else
    echo "❌ Still cannot reach Ollama"
    echo ""
    echo "Checking backend logs..."
    docker compose logs --tail=20 backend | grep -i ollama
fi

echo ""
echo "✅ Fix applied!"
echo ""
echo "Now try chatting with Navi in the frontend:"
echo "   http://$(hostname -I | awk '{print $1}'):3000"
echo ""
echo "Go to the NAVI module and send a message!"
