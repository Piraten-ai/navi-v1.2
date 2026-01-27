#!/bin/bash
# Diagnostic and fix for Ollama connectivity (Jetson backend)

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "OLLAMA CONNECTION DIAGNOSTIC"
echo "============================"
echo ""

CONFIG_FILE="config/backend.env.jetson"
OLLAMA_MODEL=$(awk -F= '/^OLLAMA_MODEL=/{print $2}' "$CONFIG_FILE" 2>/dev/null | tail -1)
if [ -z "$OLLAMA_MODEL" ]; then
    OLLAMA_MODEL="mistral"
fi

echo "Using OLLAMA_MODEL: $OLLAMA_MODEL"
echo ""

echo "1. Checking Ollama container status..."
if docker ps --format "{{.Names}}" | grep -q "^aads-navi-ollama$"; then
    echo "OK: Ollama container is running"

    echo ""
    echo "2. Checking Ollama model..."
    if docker exec aads-navi-ollama ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
        echo "OK: Ollama model loaded"
    else
        echo "WARN: Model missing, pulling $OLLAMA_MODEL..."
        docker exec aads-navi-ollama ollama pull "$OLLAMA_MODEL"
    fi

    echo ""
    echo "3. Testing Ollama API..."
    if curl -f -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo "OK: Ollama API responding"
    else
        echo "WARN: Ollama API not responding"
    fi

    echo ""
    echo "4. Testing Ollama from backend container..."
    if docker exec aads-backend curl -f -s http://navi:11434/api/version > /dev/null 2>&1; then
        echo "OK: Backend can reach Ollama"
    else
        echo "WARN: Backend cannot reach Ollama"
        echo "      Checking network..."
        docker exec aads-backend ping -c 2 navi
    fi
else
    echo "WARN: Ollama container is NOT running"
    echo "      Starting Ollama..."
    docker compose up -d navi
    sleep 10
    echo "      Pulling $OLLAMA_MODEL..."
    docker exec aads-navi-ollama ollama pull "$OLLAMA_MODEL"
fi

echo ""
echo "5. Checking Backend API..."
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "OK: Backend API responding"
else
    echo "WARN: Backend API not responding"
fi

echo ""
echo "============================"
echo "NOTES"
echo "============================"
echo "Frontend runs on the Raspberry Pi using docker-compose.pi.yml."
echo "Set JETSON_HOST on the Pi before building:"
echo "  echo JETSON_HOST=<jetson-ip> > .env"
echo "  docker compose -f docker-compose.pi.yml build frontend"
echo "  docker compose -f docker-compose.pi.yml up -d frontend"
echo ""
echo "Manual Ollama test:"
echo "  curl http://localhost:11434/api/generate -d '{\"model\":\"$OLLAMA_MODEL\",\"prompt\":\"Hello\"}'"
