#!/bin/bash
# Complete Jetson Deployment with Docker Compose Fix
# This script handles everything: upgrade, fix config, and deploy

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  NAVI - Complete Jetson Deployment Script                   ║"
echo "║  Fixes Docker Compose + TypeScript + Deploys Services        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 1: Fix Docker Compose version
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 1: Upgrading Docker Compose${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

CURRENT_VERSION=$(docker-compose --version 2>/dev/null || echo "none")
echo "Current version: $CURRENT_VERSION"

if [[ "$CURRENT_VERSION" == *"1.29"* ]]; then
    echo -e "${YELLOW}⚠ Old version detected (1.29.x) - upgrading...${NC}"
    
    sudo rm -f /usr/bin/docker-compose /usr/local/bin/docker-compose
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    
    echo -e "${GREEN}✅ Docker Compose upgraded${NC}"
    docker compose version
else
    echo -e "${GREEN}✅ Docker Compose version OK${NC}"
fi

echo ""

# Step 2: Fix TypeScript config
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 2: Fixing TypeScript Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "frontend/tsconfig.json" ]; then
    echo "Updating frontend/tsconfig.json..."
    cat > frontend/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"],
  "exclude": ["src/test/**/*", "**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*.spec.tsx"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF
    echo -e "${GREEN}✅ TypeScript config updated${NC}"
else
    echo -e "${YELLOW}⚠ frontend/tsconfig.json not found - skipping${NC}"
fi

echo ""

# Step 3: Clean up old containers
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 3: Cleaning Up Old Containers${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Stopping old containers..."
docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true

echo "Removing unused images..."
docker system prune -f

echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

# Step 4: Create required directories
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 4: Creating Required Directories${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

mkdir -p models/piper audio logs data

echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Step 5: Check for Piper voice model
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 5: Checking Voice Model${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ ! -f "models/piper/en_US-lessac-medium.onnx" ]; then
    echo -e "${YELLOW}⚠ Piper TTS model not found${NC}"
    echo "Downloading model (~75MB)..."
    
    cd models/piper
    wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
    wget -q --show-progress https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
    cd ../..
    
    echo -e "${GREEN}✅ Voice model downloaded${NC}"
else
    echo -e "${GREEN}✅ Voice model already present${NC}"
fi

echo ""

# Step 6: Build images
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 6: Building Docker Images${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Building frontend and backend (this may take 10-15 minutes)..."
docker compose build backend frontend

echo -e "${GREEN}✅ Images built${NC}"
echo ""

# Step 7: Start services
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 7: Starting Services${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

docker compose up -d

echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Step 8: Wait for services
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 8: Waiting for Services (30 seconds)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

sleep 30

# Step 9: Pull Ollama model
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 9: Pulling Ollama Model${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Pulling llama3.2 (~2GB)..."
docker exec aads-navi-ollama ollama pull llama3.2

echo -e "${GREEN}✅ Ollama model loaded${NC}"
echo ""

# Step 10: Health check
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}STEP 10: Health Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

IP_ADDR=$(hostname -I | awk '{print $1}')

# Check backend
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend API: ONLINE${NC}"
else
    echo -e "${YELLOW}⚠ Backend API: Not responding yet (may need more time)${NC}"
fi

# Check frontend
if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend: ONLINE${NC}"
else
    echo -e "${YELLOW}⚠ Frontend: Not responding yet (may need more time)${NC}"
fi

# Check Ollama
if curl -f -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama: ONLINE${NC}"
else
    echo -e "${YELLOW}⚠ Ollama: Not responding yet${NC}"
fi

echo ""

# Final summary
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              DEPLOYMENT COMPLETE!                            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend:    http://${IP_ADDR}:3000"
echo "   Backend API: http://${IP_ADDR}:8000"
echo "   API Docs:    http://${IP_ADDR}:8000/docs"
echo ""
echo "🔧 Management Commands:"
echo "   View logs:     docker compose logs -f"
echo "   Check status:  docker compose ps"
echo "   Restart:       docker compose restart"
echo "   Stop all:      docker compose down"
echo ""
echo "📊 Monitor Performance:"
echo "   tegrastats              # Jetson stats"
echo "   docker stats            # Container stats"
echo "   docker compose logs -f  # Live logs"
echo ""
echo "🧊 When satellites fail, we survive. ⚓"
echo ""
