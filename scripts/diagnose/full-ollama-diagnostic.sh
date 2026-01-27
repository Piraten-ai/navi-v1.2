#!/bin/bash
# Complete diagnostic for Ollama connectivity (Jetson backend)

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

CONFIG_FILE="config/backend.env.jetson"
OLLAMA_MODEL=$(awk -F= '/^OLLAMA_MODEL=/{print $2}' "$CONFIG_FILE" 2>/dev/null | tail -1)
if [ -z "$OLLAMA_MODEL" ]; then
    OLLAMA_MODEL="mistral"
fi

BACKEND_RUNNING=false
OLLAMA_RUNNING=false
if docker ps --format "{{.Names}}" | grep -q "^aads-backend$"; then
    BACKEND_RUNNING=true
fi
if docker ps --format "{{.Names}}" | grep -q "^aads-navi-ollama$"; then
    OLLAMA_RUNNING=true
fi

echo "COMPLETE OLLAMA DIAGNOSTIC"
echo "=========================="
echo ""

echo "1. OLLAMA_BASE_URL in backend config:"
if [ -f "$CONFIG_FILE" ]; then
    grep "^OLLAMA_BASE_URL=" "$CONFIG_FILE" || echo "Not set in $CONFIG_FILE"
else
    echo "Missing: $CONFIG_FILE"
fi

echo ""
echo "2. OLLAMA settings inside backend container:"
if [ "$BACKEND_RUNNING" = true ]; then
    docker exec aads-backend env | grep OLLAMA || echo "No OLLAMA_* envs in container"
else
    echo "Backend container not running"
fi

echo ""
echo "3. Ollama API from host:"
curl -s http://localhost:11434/api/version || echo "No response"

echo ""
echo "4. Ollama API from backend container (service name 'navi'):"
if [ "$BACKEND_RUNNING" = true ]; then
    docker exec aads-backend curl -s http://navi:11434/api/version || echo "No response"
else
    echo "Backend container not running"
fi

echo ""
echo "5. Container network check:"
NETWORK_NAME=$(docker network ls --format "{{.Name}}" | grep "aads-network" | head -1)
if [ -n "$NETWORK_NAME" ]; then
    docker network inspect "$NETWORK_NAME" | grep -A 5 "aads-backend\\|aads-navi-ollama"
else
    echo "No aads-network found"
fi

echo ""
echo "6. Backend navi module config:"
if [ "$BACKEND_RUNNING" = true ]; then
    docker exec aads-backend grep -n "ollama" /app/app/modules/navi.py | head -5
else
    echo "Backend container not running"
fi

echo ""
echo "7. Recent backend logs about Ollama:"
docker compose logs --tail=50 backend | grep -i "ollama\\|navi initialized" || true

echo ""
echo "8. Testing a chat request from backend:"
if [ "$BACKEND_RUNNING" = true ]; then
    docker exec aads-backend python3 << PYTHON
import os
import requests

ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
model = os.getenv("OLLAMA_MODEL", "${OLLAMA_MODEL}")
print(f"Using OLLAMA_BASE_URL: {ollama_url}")
print(f"Using OLLAMA_MODEL: {model}")

try:
    response = requests.post(
        f"{ollama_url}/api/generate",
        json={"model": model, "prompt": "Hello", "stream": False},
        timeout=10,
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
PYTHON
else
    echo "Backend container not running"
fi
