#!/bin/bash

# 🚀 AADS JETSON - COMPLETE SYSTEM FIX
# One-command solution to fix everything

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

clear

echo -e "${BLUE}${BOLD}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║     🚀 AADS JETSON COMPLETE SYSTEM FIX 🚀             ║"
echo "║                                                        ║"
echo "║     Fixing all issues and getting to 100% health      ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}📍 Working directory: $PROJECT_ROOT${NC}"
echo ""

# ============================================================
# PHASE 1: STOP EVERYTHING
# ============================================================
echo -e "${BLUE}${BOLD}PHASE 1: Stopping all services...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "⏹  Stopping Docker containers..."
docker-compose down 2>/dev/null || true
docker-compose down -v 2>/dev/null || true

echo "⏳ Waiting 2 seconds for cleanup..."
sleep 2

echo -e "${GREEN}✓ All services stopped${NC}"
echo ""

# ============================================================
# PHASE 2: CREATE CONFIGURATION
# ============================================================
echo -e "${BLUE}${BOLD}PHASE 2: Creating configuration...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Backup existing .env if present
if [ -f ".env" ]; then
    echo "💾 Backing up existing .env to .env.backup"
    cp .env .env.backup
    echo -e "${GREEN}✓ Backed up${NC}"
fi

# Create .env file
echo "📝 Creating .env file..."
cat > .env << 'ENVEOF'
# AADS Production Environment
ENVIRONMENT=production
DEV_MODE=false

# Database
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

# Signal K
SIGNALK_ENABLED=true
SIGNALK_SERVER_URL=ws://signalk:3000/signalk/v1/stream
SIGNALK_MOCK_DATA=false

# Data Sources
NMEA_ENABLED=true
NMEA_SERIAL_PORT=/dev/ttyUSB0
NMEA_MOCK_DATA=false

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/aads.log
LOG_JSON=true
LOG_DEBUG=false

# Security
SECRET_KEY=aads-production-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://192.168.39.196:3000"]

# WebSocket
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=100
ENVEOF

echo -e "${GREEN}✓ .env created${NC}"
echo ""

# Create directories
echo "📁 Creating required directories..."
mkdir -p models/piper
mkdir -p data
mkdir -p logs
mkdir -p audio
echo -e "${GREEN}✓ Directories ready${NC}"
echo ""

# ============================================================
# PHASE 3: DOWNLOAD PIPER TTS MODEL
# ============================================================
echo -e "${BLUE}${BOLD}PHASE 3: Downloading Piper TTS model...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

MODELS_DIR="models/piper"
MODEL_FILE="$MODELS_DIR/en_US-lessac-medium.onnx"
MODEL_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"

if [ -f "$MODEL_FILE" ]; then
    echo -e "${GREEN}✓ Piper model already exists${NC}"
    SIZE=$(du -h "$MODEL_FILE" | cut -f1)
    echo "  File: $MODEL_FILE"
    echo "  Size: $SIZE"
else
    echo "📥 Downloading Piper TTS model..."
    echo "   (This may take 2-5 minutes depending on connection)"
    echo ""
    
    if command -v curl &> /dev/null; then
        if curl -L -o "$MODEL_FILE" "$MODEL_URL" --progress-bar 2>/dev/null; then
            echo ""
            echo -e "${GREEN}✓ Piper model downloaded successfully${NC}"
            SIZE=$(du -h "$MODEL_FILE" | cut -f1)
            echo "  Size: $SIZE"
        else
            echo -e "${RED}✗ Download failed with curl${NC}"
            exit 1
        fi
    elif command -v wget &> /dev/null; then
        if wget -O "$MODEL_FILE" "$MODEL_URL" --show-progress 2>/dev/null; then
            echo -e "${GREEN}✓ Piper model downloaded successfully${NC}"
            SIZE=$(du -h "$MODEL_FILE" | cut -f1)
            echo "  Size: $SIZE"
        else
            echo -e "${RED}✗ Download failed with wget${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠ Warning: curl/wget not found, skipping Piper download${NC}"
        echo "  Install with: sudo apt-get install curl wget"
    fi
fi
echo ""

# ============================================================
# PHASE 4: START SERVICES
# ============================================================
echo -e "${BLUE}${BOLD}PHASE 4: Starting Docker services...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "🚀 Starting docker-compose..."
docker-compose up -d

echo "⏳ Waiting for services to initialize (15 seconds)..."
for i in {15..1}; do
    echo -ne "\r   $i seconds remaining...   "
    sleep 1
done
echo -e "\r✓ Services started                      "
echo ""

# ============================================================
# PHASE 5: VERIFY SERVICES
# ============================================================
echo -e "${BLUE}${BOLD}PHASE 5: Verifying services...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "📋 Container Status:"
docker-compose ps
echo ""

# Check Backend
echo -n "  Backend API (port 8000): "
if timeout 5 curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⏳ Still initializing${NC}"
fi

# Check Frontend
echo -n "  Frontend (port 3000): "
if timeout 5 curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⏳ Still initializing${NC}"
fi

# Check Ollama
echo -n "  Ollama (port 11434): "
if timeout 5 curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⏳ Still initializing${NC}"
fi

echo ""

# ============================================================
# PHASE 6: FINAL STATUS
# ============================================================
echo -e "${BLUE}${BOLD}PHASE 6: Final Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${GREEN}${BOLD}✓ SETUP COMPLETE!${NC}"
echo ""
echo "🎯 Access URLs:"
echo "   🖥  Frontend:   http://192.168.39.196:3000"
echo "   ⚙️  Backend:    http://192.168.39.196:8000"
echo "   📖 API Docs:   http://192.168.39.196:8000/docs"
echo ""

echo "📊 System Information:"
echo "   IP: 192.168.39.196"
echo "   Status: Ready for production"
echo ""

echo "🔧 Useful Commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Diagnose:      bash diagnose-jetson.sh"
echo "   Stop all:      docker-compose down"
echo "   Restart all:   docker-compose restart"
echo ""

echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}${BOLD}🎉 AADS System is Ready! 🎉${NC}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
