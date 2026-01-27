#!/bin/bash
# Complete Jetson backend deployment

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "NAVI - Complete Jetson Deployment"
echo "================================="
echo ""

CONFIG_FILE="config/backend.env.jetson"
OLLAMA_MODEL=$(awk -F= '/^OLLAMA_MODEL=/{print $2}' "$CONFIG_FILE" 2>/dev/null | tail -1)
if [ -z "$OLLAMA_MODEL" ]; then
    OLLAMA_MODEL="mistral"
fi

# Step 1: Check Docker Compose
echo "STEP 1: Checking Docker Compose"
if docker compose version >/dev/null 2>&1; then
    docker compose version
else
    echo "docker compose not available"
    echo "Install docker-compose-plugin before continuing"
    exit 1
fi
echo ""

# Step 2: Validate config
echo "STEP 2: Validating backend config"
if [ -f "$CONFIG_FILE" ]; then
    echo "Found $CONFIG_FILE"
else
    echo "Missing $CONFIG_FILE"
    exit 1
fi
echo ""

# Step 3: Clean up old containers
echo "STEP 3: Cleaning up old containers"
docker compose down || true
docker system prune -f
echo ""

# Step 4: Create required directories
echo "STEP 4: Creating required directories"
mkdir -p models/piper audio logs data
echo ""

# Step 5: Ensure Piper model
echo "STEP 5: Checking voice model"
if [ ! -f "models/piper/en_US-lessac-medium.onnx" ]; then
    echo "Piper model not found, downloading..."
    mkdir -p models/piper
    if command -v wget >/dev/null 2>&1; then
        wget -q --show-progress -O models/piper/en_US-lessac-medium.onnx \
          https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
        wget -q --show-progress -O models/piper/en_US-lessac-medium.onnx.json \
          https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
    elif command -v curl >/dev/null 2>&1; then
        curl -L -o models/piper/en_US-lessac-medium.onnx \
          https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
        curl -L -o models/piper/en_US-lessac-medium.onnx.json \
          https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
    else
        echo "Neither wget nor curl is available. Install one to download the model."
        exit 1
    fi
else
    echo "Piper model already present"
fi
echo ""

# Step 6: Build backend image
echo "STEP 6: Building backend image"
docker compose build backend
echo ""

# Step 7: Start services
echo "STEP 7: Starting services"
docker compose up -d
echo ""

# Step 8: Wait for services
echo "STEP 8: Waiting for services"
sleep 30
echo ""

# Step 9: Pull Ollama model
echo "STEP 9: Pulling Ollama model (${OLLAMA_MODEL})"
docker exec aads-navi-ollama ollama pull "${OLLAMA_MODEL}"
echo ""

# Step 10: Health check
echo "STEP 10: Health check"
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend API: ONLINE"
else
    echo "Backend API: Not responding yet"
fi

if curl -f -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "Ollama: ONLINE"
else
    echo "Ollama: Not responding yet"
fi

if curl -f -s http://localhost:3001 > /dev/null 2>&1; then
    echo "Signal K: ONLINE"
else
    echo "Signal K: Not responding yet"
fi
echo ""

IP_ADDR=$(hostname -I | awk '{print $1}')
echo "Access URLs:"
echo "  Backend API: http://${IP_ADDR}:8000"
echo "  API Docs:    http://${IP_ADDR}:8000/docs"
echo "  Signal K:    http://${IP_ADDR}:3001"
echo ""
echo "Frontend runs on the Raspberry Pi (docker-compose.pi.yml)."
