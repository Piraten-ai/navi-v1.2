#!/bin/bash

# Complete AADS Jetson Setup & Deployment
# Fixes all issues and gets system to full health

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║     AADS COMPLETE DEPLOYMENT SETUP                     ║"
echo "║     All-in-one fix for Jetson                          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📍 Project Root: $PROJECT_ROOT"
echo ""

# ============================================================
# 1. CREATE .ENV FILE
# ============================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 1: Create .env Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env already exists, backing up to .env.backup${NC}"
    cp .env .env.backup
fi

cat > .env << 'EOF'
# NAVI Production Configuration for Jetson
ENVIRONMENT=production
DEV_MODE=false

# Database - PostgreSQL
DATABASE_URL=postgresql+asyncpg://aads_user:aads_password@postgres:5432/aads_db

# Redis
REDIS_URL=redis://redis:6379/0

# InfluxDB
INFLUXDB_URL=http://influxdb:8086
INFLUXDB_TOKEN=aads_influx_token
INFLUXDB_ORG=aads
INFLUXDB_BUCKET=telemetry

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_BUCKET=aads-data

# Ollama/Navi
OLLAMA_BASE_URL=http://navi:11434
OLLAMA_MODEL=llama2:latest
OLLAMA_TIMEOUT=120

# Signal K Server
SIGNALK_ENABLED=true
SIGNALK_SERVER_URL=ws://signalk:3000/signalk/v1/stream
SIGNALK_MOCK_DATA=false

# Real Data Sources
NMEA_ENABLED=true
NMEA_SERIAL_PORT=/dev/ttyUSB0
NMEA_MOCK_DATA=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/aads.log
LOG_JSON=true
LOG_DEBUG=false

# Security
SECRET_KEY=your-secure-random-key-here-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://192.168.39.196:3000"]

# WebSocket
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=100
EOF

echo -e "${GREEN}✓ .env file created${NC}"
echo ""

# ============================================================
# 2. DOWNLOAD PIPER TTS MODEL
# ============================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 2: Download Piper TTS Model${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

MODELS_DIR="./models/piper"
MODEL_FILE="$MODELS_DIR/en_US-lessac-medium.onnx"
MODEL_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"

mkdir -p "$MODELS_DIR"

if [ -f "$MODEL_FILE" ]; then
    echo -e "${GREEN}✓ Piper model already exists${NC}"
    ls -lh "$MODEL_FILE"
else
    echo "📥 Downloading Piper TTS model (this may take a few minutes)..."
    echo "   Size: ~50MB"
    echo ""
    
    if command -v curl &> /dev/null; then
        curl -L -o "$MODEL_FILE" "$MODEL_URL" --progress-bar
    elif command -v wget &> /dev/null; then
        wget -O "$MODEL_FILE" "$MODEL_URL" --show-progress
    else
        echo -e "${RED}✗ Neither curl nor wget found${NC}"
        exit 1
    fi
    
    if [ -f "$MODEL_FILE" ]; then
        echo ""
        echo -e "${GREEN}✓ Piper model downloaded${NC}"
        ls -lh "$MODEL_FILE"
    else
        echo -e "${RED}✗ Download failed${NC}"
        exit 1
    fi
fi
echo ""

# ============================================================
# 3. STOP & CLEAN CONTAINERS
# ============================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 3: Restart Docker Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "⏹ Stopping services..."
docker-compose down 2>/dev/null || true

echo "⏳ Waiting 3 seconds..."
sleep 3

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to stabilize (10 seconds)..."
sleep 10

echo -e "${GREEN}✓ Services started${NC}"
echo ""

# ============================================================
# 4. VERIFY SERVICES
# ============================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Step 4: Verify Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "📋 Container Status:"
docker-compose ps

echo ""
echo "🌐 Testing Endpoints:"
echo ""

# Backend API
echo -n "  Backend API (http://localhost:8000): "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⏳ Still starting...${NC}"
fi

# Frontend
echo -n "  Frontend (http://localhost:3000): "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⏳ Still starting...${NC}"
fi

# Ollama
echo -n "  Ollama (http://localhost:11434): "
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${YELLOW}⏳ Still starting...${NC}"
fi

echo ""

# ============================================================
# 5. DISPLAY SUMMARY
# ============================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${GREEN}✓ .env file created and configured${NC}"
echo -e "${GREEN}✓ Piper TTS model downloaded${NC}"
echo -e "${GREEN}✓ Docker services restarted${NC}"
echo ""

echo "📍 Access URLs:"
echo "   Frontend:  http://192.168.39.196:3000"
echo "   Backend:   http://192.168.39.196:8000"
echo "   API Docs:  http://192.168.39.196:8000/docs"
echo ""

echo "🎯 Next Steps:"
echo "   1. Run diagnostic: bash diagnose-jetson.sh"
echo "   2. Check backend logs if needed: docker-compose logs -f aads-backend"
echo "   3. Test the system: http://192.168.39.196:3000"
echo ""

echo -e "${GREEN}✓ AADS deployment complete!${NC}"
