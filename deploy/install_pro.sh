#!/bin/bash
# AADS Pro Edition Installer
# For NVIDIA Jetson Nano Orin DevKit 12GB
# Optimized for high-performance maritime autonomous detection

set -e

echo "🧊 =================================="
echo "   AADS PRO EDITION INSTALLER"
echo "   Jetson Nano Orin DevKit Deployment"
echo "==================================== 🧊"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (sudo)"
    exit 1
fi

echo "📋 System Information:"
echo "   Architecture: $(uname -m)"
echo "   Kernel: $(uname -r)"
echo "   RAM: $(free -h | awk '/^Mem:/{print $2}')"
echo ""

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker $SUDO_USER
    rm get-docker.sh
else
    echo "✅ Docker already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    apt-get install -y docker-compose
else
    echo "✅ Docker Compose already installed"
fi

# Install NVIDIA Container Toolkit
echo "🎮 Installing NVIDIA Container Toolkit..."
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update && apt-get install -y nvidia-container-toolkit
systemctl restart docker

# Optimize Jetson Nano Orin DevKit
echo "⚡ Optimizing Jetson Nano Orin DevKit performance..."

# Set MAX power mode (25W)
if command -v nvpmodel &> /dev/null; then
    nvpmodel -m 0  # MAXN mode
    echo "✅ Set to MAXN performance mode"
fi

# Set CPU governor to performance
for cpu in /sys/devices/system/cpu/cpu[0-9]*; do
    if [ -f "$cpu/cpufreq/scaling_governor" ]; then
        echo "performance" > "$cpu/cpufreq/scaling_governor"
    fi
done
echo "✅ CPU governor set to performance"

# Max GPU clocks
if command -v jetson_clocks &> /dev/null; then
    jetson_clocks
    echo "✅ GPU clocks maximized"
fi

# Increase swap (helps with Ollama model loading on 12GB DevKit)
if [ ! -f /swapfile ] || [ $(du -h /swapfile | awk '{print $1}' | tr -d 'G') -lt 8 ]; then
    echo "💾 Creating 8GB swap file..."
    swapoff -a || true
    rm -f /swapfile
    fallocate -l 8G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    
    # Make swap permanent
    if ! grep -q "/swapfile" /etc/fstab; then
        echo "/swapfile none swap sw 0 0" >> /etc/fstab
    fi
    echo "✅ 8GB swap configured"
fi

# Clone repository (if not already in it)
if [ ! -f "docker-compose.yml" ]; then
    echo "📥 Cloning AADS repository..."
    cd /opt
    git clone https://github.com/Piraten-ai/aads-handover.git
    cd aads-handover
else
    echo "✅ Already in AADS repository"
fi

# Create environment file for Pro edition
if [ ! -f ".env" ]; then
    echo "⚙️  Creating configuration..."
    cat > .env << 'EOF'
# AADS Pro Edition Configuration
ENVIRONMENT=production
DEV_MODE=false
MOCK_CAMERA=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://aads:aads_secure_pass@postgres:5432/aads

# Ollama (using full model for Orin)
OLLAMA_MODEL=llama3.2

# Performance tuning for Jetson Nano Orin DevKit
WS_MAX_CONNECTIONS=50
BATCH_SIZE=4
FPS_TARGET=30
MAX_WORKERS=4
EOF
    echo "✅ Configuration created (.env)"
fi

# Pull Docker images
echo "📦 Pulling Docker images (this may take 15-20 minutes)..."
docker-compose pull

# Build custom images
echo "🔨 Building AADS images..."
docker-compose build

# Start services
echo "🚀 Starting AADS services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Pull Ollama model (full model for better performance)
echo "🤖 Pulling Ollama model (llama3.2 - ~2GB)..."
docker exec aads-navi-ollama ollama pull llama3.2

# Check service health
echo ""
echo "🏥 Checking service health..."
sleep 5

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend: HEALTHY"
else
    echo "⚠️  Backend: Not responding yet (may need more time)"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend: HEALTHY"
else
    echo "⚠️  Frontend: Not responding yet (may need more time)"
fi

# Display status
echo ""
echo "✅ =================================="
echo "   AADS PRO INSTALLATION COMPLETE"
echo "==================================== ✅"
echo ""
echo "📊 Services:"
echo "   Backend API:  http://$(hostname -I | awk '{print $1}'):8000"
echo "   Frontend UI:  http://$(hostname -I | awk '{print $1}'):3000"
echo "   API Docs:     http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "🔧 Management Commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart"
echo "   Update:       git pull && docker-compose up -d --build"
echo ""
echo "📝 Configuration: .env file"
echo ""
echo "💪 Jetson Nano Orin DevKit Performance Tips:"
echo "   - Monitor GPU/CPU with: tegrastats"
echo "   - Check temps: cat /sys/devices/virtual/thermal/thermal_zone*/temp"
echo "   - Ensure good cooling and ventilation"
echo "   - Watch memory: free -h | watch"
echo "   - Ollama runs on GPU: auto-optimized for DevKit"
echo ""
echo "🧊 When satellites fail, we survive. ⚓"
echo ""

# Make sure docker group is active (user needs to re-login)
if [ -n "$SUDO_USER" ]; then
    echo "⚠️  IMPORTANT: User '$SUDO_USER' must log out and back in for Docker permissions to take effect!"
fi
