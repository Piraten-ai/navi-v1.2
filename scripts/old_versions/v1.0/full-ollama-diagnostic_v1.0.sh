#!/bin/bash
# Complete diagnostic for Ollama connectivity

echo "🔍 COMPLETE OLLAMA DIAGNOSTIC"
echo "=============================="
echo ""

echo "1. Checking environment variable in docker-compose.yml..."
grep "OLLAMA_BASE_URL" docker-compose.yml

echo ""
echo "2. Checking environment variable INSIDE backend container..."
docker exec aads-backend env | grep OLLAMA

echo ""
echo "3. Testing Ollama from host..."
curl -s http://localhost:11434/api/version

echo ""
echo "4. Testing Ollama from backend container (using 'navi')..."
docker exec aads-backend curl -s http://navi:11434/api/version

echo ""
echo "5. Checking if backend can resolve 'navi' hostname..."
docker exec aads-backend ping -c 2 navi

echo ""
echo "6. Checking Docker network..."
docker network inspect navi-main_aads-network | grep -A 5 "aads-backend\|aads-navi-ollama"

echo ""
echo "7. Checking backend navi module code..."
docker exec aads-backend cat /app/app/modules/navi.py | grep -A 5 "ollama_url"

echo ""
echo "8. Recent backend logs about Ollama..."
docker compose logs --tail=50 backend | grep -i "ollama\|navi initialized"

echo ""
echo "9. Testing actual chat request from backend..."
docker exec aads-backend python3 << 'PYTHON'
import os
import requests

ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
print(f"Using OLLAMA_BASE_URL: {ollama_url}")

try:
    response = requests.post(
        f"{ollama_url}/api/generate",
        json={"model": "llama3.2", "prompt": "Hello", "stream": False},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
PYTHON

echo ""
echo "=============================="
echo "ANALYSIS"
echo "=============================="
