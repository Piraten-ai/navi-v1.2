#!/bin/bash
# AADS Jetson Diagnostic Script
# Run this to identify deployment issues on Jetson

set +e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

CONFIG_FILE="config/backend.env.jetson"
OLLAMA_MODEL="$(awk -F= '/^OLLAMA_MODEL=/{print $2}' "$CONFIG_FILE" 2>/dev/null | tail -1)"
if [ -z "$OLLAMA_MODEL" ]; then
    OLLAMA_MODEL="mistral"
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_pass() { echo -e "${GREEN}[OK]${NC} $1"; }
check_fail() { echo -e "${RED}[FAIL]${NC} $1"; }
check_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
check_info() { echo -e "${BLUE}[INFO]${NC} $1"; }

section() {
    echo ""
    echo "==================================="
    echo "$1"
    echo "==================================="
}

section "1. SYSTEM INFORMATION"

OS_NAME=$(grep PRETTY_NAME /etc/os-release 2>/dev/null | cut -d'"' -f2)
KERNEL=$(uname -r)
ARCH=$(uname -m)
IP_ADDR=$(hostname -I 2>/dev/null | awk '{print $1}')

check_info "OS: ${OS_NAME:-unknown}"
check_info "Kernel: ${KERNEL:-unknown}"
check_info "Architecture: ${ARCH:-unknown}"
check_info "IP Address: ${IP_ADDR:-unknown}"

section "2. JETSON HARDWARE"

if command -v tegrastats >/dev/null 2>&1; then
    check_pass "Jetson tools detected"
    if command -v nvpmodel >/dev/null 2>&1; then
        POWER_MODE=$(nvpmodel -q 2>/dev/null | grep "NV Power Mode" | awk '{print $NF}')
        if [ "$POWER_MODE" = "MAXN" ] || [ "$POWER_MODE" = "0" ]; then
            check_pass "Power mode: MAXN (optimal)"
        else
            check_warn "Power mode: $POWER_MODE (consider 'sudo nvpmodel -m 0')"
        fi
    fi
else
    check_warn "Not running on Jetson or tools not installed"
fi

if [ -d "/sys/devices/virtual/thermal" ]; then
    MAX_TEMP=0
    for zone in /sys/devices/virtual/thermal/thermal_zone*/temp; do
        if [ -f "$zone" ]; then
            TEMP=$(cat "$zone")
            TEMP_C=$((TEMP / 1000))
            if [ "$TEMP_C" -gt "$MAX_TEMP" ]; then
                MAX_TEMP=$TEMP_C
            fi
        fi
    done

    if [ "$MAX_TEMP" -lt 70 ]; then
        check_pass "Temperature: ${MAX_TEMP}C (good)"
    elif [ "$MAX_TEMP" -lt 85 ]; then
        check_warn "Temperature: ${MAX_TEMP}C (warm but OK)"
    else
        check_fail "Temperature: ${MAX_TEMP}C (too hot, check cooling)"
    fi
fi

section "3. MEMORY & STORAGE"

TOTAL_RAM=$(free -h | awk '/^Mem:/{print $2}')
USED_RAM=$(free -h | awk '/^Mem:/{print $3}')
AVAIL_RAM=$(free -h | awk '/^Mem:/{print $7}')
RAM_PERCENT=$(free | awk '/^Mem:/{printf("%.0f", $3/$2 * 100)}')

check_info "RAM: $USED_RAM / $TOTAL_RAM used ($RAM_PERCENT%)"
if [ "$RAM_PERCENT" -lt 80 ]; then
    check_pass "RAM usage healthy"
else
    check_warn "High RAM usage - consider reducing workload"
fi
check_info "RAM available: ${AVAIL_RAM:-unknown}"

SWAP_TOTAL=$(free -h | awk '/^Swap:/{print $2}')
if [ "$SWAP_TOTAL" = "0B" ]; then
    check_warn "No swap configured (recommended: 8GB)"
    echo "  Run: sudo fallocate -l 8G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile"
else
    check_pass "Swap: $SWAP_TOTAL configured"
fi

DISK_USED=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
DISK_AVAIL=$(df -h / | awk 'NR==2{print $4}')
check_info "Disk: ${DISK_USED}% used, ${DISK_AVAIL} available"
if [ "$DISK_USED" -lt 80 ]; then
    check_pass "Disk space healthy"
else
    check_warn "Low disk space - consider cleanup"
    echo "  Run: docker system prune -a"
fi

section "4. DOCKER"

if command -v docker >/dev/null 2>&1; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    check_pass "Docker installed: $DOCKER_VERSION"
    if systemctl is-active --quiet docker; then
        check_pass "Docker service running"
    else
        check_fail "Docker service not running"
        echo "  Run: sudo systemctl start docker"
    fi
    if docker ps >/dev/null 2>&1; then
        check_pass "Docker permissions OK"
    else
        check_warn "Cannot run docker without sudo"
        echo "  Run: sudo usermod -aG docker $USER && newgrp docker"
    fi
else
    check_fail "Docker not installed"
    echo "  Run: curl -fsSL https://get.docker.com | sh"
fi

if command -v docker-compose >/dev/null 2>&1; then
    DC_VERSION=$(docker-compose --version | awk '{print $4}' | sed 's/,//')
    check_pass "docker-compose installed: $DC_VERSION"
elif docker compose version >/dev/null 2>&1; then
    DC_VERSION=$(docker compose version --short)
    check_pass "docker compose (plugin) installed: $DC_VERSION"
else
    check_fail "docker-compose not installed"
    echo "  Run: sudo apt-get install -y docker-compose-plugin"
fi

if docker info 2>/dev/null | grep -q "nvidia"; then
    check_pass "NVIDIA Container Runtime detected"
elif [ -f "/etc/docker/daemon.json" ] && grep -q "nvidia" /etc/docker/daemon.json; then
    check_pass "NVIDIA runtime configured"
else
    check_warn "NVIDIA Container Runtime not detected"
    echo "  Required for Ollama GPU acceleration"
    echo "  See: docs/current/COMPLETE_TECHNICAL_REFERENCE.md"
fi

section "5. NVIDIA GPU"

if command -v nvidia-smi >/dev/null 2>&1; then
    check_pass "nvidia-smi available"
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null)
    GPU_TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>/dev/null)
    GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>/dev/null | sed 's/ %//')
    GPU_MEM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader 2>/dev/null)
    check_info "GPU: $GPU_NAME"
    check_info "GPU Temp: ${GPU_TEMP}C"
    check_info "GPU Util: ${GPU_UTIL}%"
    check_info "GPU Memory: $GPU_MEM"
else
    check_warn "nvidia-smi not available"
fi

section "6. NETWORKING"

PORTS=(8000 3001 5432 6379 8086 9000 9001 11434)
PORT_NAMES=("Backend" "SignalK" "Postgres" "Redis" "InfluxDB" "MinIO API" "MinIO Console" "Ollama")

for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${PORT_NAMES[$i]}
    if netstat -tuln 2>/dev/null | grep -q ":$PORT " || ss -tuln 2>/dev/null | grep -q ":$PORT "; then
        check_pass "$NAME (port $PORT) is listening"
    else
        check_warn "$NAME (port $PORT) not listening"
    fi
done

if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    check_pass "Internet connectivity OK"
else
    check_warn "No internet connection"
fi

section "7. DOCKER CONTAINERS"

if command -v docker >/dev/null 2>&1 && docker ps >/dev/null 2>&1; then
    CONTAINERS=("aads-backend" "aads-postgres" "aads-influxdb" "aads-redis" "aads-minio" "aads-navi-ollama" "aads-signalk")
    for container in "${CONTAINERS[@]}"; do
        if docker ps --format "{{.Names}}" | grep -q "^${container}$"; then
            STATUS=$(docker ps --filter "name=^${container}$" --format "{{.Status}}")
            if echo "$STATUS" | grep -q "Up"; then
                check_pass "$container: Running"
            else
                check_warn "$container: $STATUS"
            fi
        else
            if docker ps -a --format "{{.Names}}" | grep -q "^${container}$"; then
                STATUS=$(docker ps -a --filter "name=^${container}$" --format "{{.Status}}")
                check_fail "$container: $STATUS"
            else
                check_warn "$container: Not created"
            fi
        fi
    done

    echo ""
    check_info "Container Resource Usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | head -8
else
    check_warn "Cannot check container status"
fi

section "8. AADS DEPLOYMENT"

if [ -f "docker-compose.yml" ]; then
    check_pass "docker-compose.yml found"
else
    check_fail "docker-compose.yml not found"
    echo "  Are you in the correct directory?"
fi

if [ -f "$CONFIG_FILE" ]; then
    check_pass "Backend env file found: $CONFIG_FILE"
else
    check_warn "Backend env file not found: $CONFIG_FILE"
fi

DIRS=("backend" "config" "data" "models/piper" "audio" "logs")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        check_pass "Directory exists: $dir"
    else
        check_warn "Directory missing: $dir"
        echo "  Run: mkdir -p $dir"
    fi
done

if [ -f "models/piper/en_US-lessac-medium.onnx" ]; then
    check_pass "Piper TTS model downloaded"
else
    check_warn "Piper TTS model not found"
    echo "  Voice system will not work"
    echo "  See: docs/current/COMPLETE_TECHNICAL_REFERENCE.md"
fi

section "9. SERVICE HEALTH CHECKS"

if curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
    check_pass "Backend API responding"
elif curl -f -s http://localhost:8000/docs >/dev/null 2>&1; then
    check_pass "Backend API responding (docs endpoint)"
else
    check_warn "Backend API not responding"
    echo "  Try: docker logs aads-backend"
fi

if curl -f -s http://localhost:11434/api/version >/dev/null 2>&1; then
    check_pass "Ollama API responding"
    if docker exec aads-navi-ollama ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
        check_pass "Ollama model loaded"
    else
        check_warn "Ollama model not loaded"
        echo "  Run: docker exec aads-navi-ollama ollama pull ${OLLAMA_MODEL}"
    fi
else
    check_warn "Ollama not responding"
fi

section "10. SUMMARY & RECOMMENDATIONS"

check_info "Access URLs (if services running):"
echo "  Backend:  http://${IP_ADDR}:8000"
echo "  API Docs: http://${IP_ADDR}:8000/docs"
echo "  Signal K: http://${IP_ADDR}:3001"

echo ""
echo "Next Steps:"
echo "  1. Check logs: docker compose logs -f"
echo "  2. View troubleshooting: cat docs/current/COMPLETE_TECHNICAL_REFERENCE.md"
echo "  3. Restart services: docker compose restart"
echo "  4. Full rebuild: docker compose down && docker compose up -d --build"
echo ""

check_info "Diagnostic complete. Review warnings and failures above."
