# Jetson Ubuntu Troubleshooting Guide

## Common Issues and Solutions

### 1. Docker Installation Issues

#### Problem: "Permission denied" when running docker commands
```bash
# Solution: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or logout and login again
# Test: docker ps (should work without sudo)
```

#### Problem: Docker service not starting
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Check Docker logs
sudo journalctl -u docker.service -n 50
```

#### Problem: NVIDIA runtime not found
```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Test GPU access
docker run --rm --runtime=nvidia nvidia/cuda:11.4.0-base-ubuntu20.04 nvidia-smi
```

---

### 2. Docker Compose Issues

#### Problem: docker-compose command not found
```bash
# Install docker-compose plugin
sudo apt-get update
sudo apt-get install -y docker-compose-plugin

# Or use docker compose (without hyphen)
docker compose version

# Alternative: Install standalone binary
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Problem: docker-compose.yml: version is obsolete
```bash
# Modern docker-compose doesn't need version field
# Edit docker-compose.yml and remove the "version: '3.8'" line at the top
# Or update to latest docker-compose version
```

---

### 3. Build Failures

#### Problem: "no space left on device"
```bash
# Check disk space
df -h

# Clean up Docker
docker system prune -a --volumes
# WARNING: This removes ALL unused containers, networks, images, and volumes

# Or more selectively:
docker image prune -a  # Remove unused images
docker volume prune    # Remove unused volumes
docker container prune # Remove stopped containers

# Check Jetson storage
sudo du -sh /var/lib/docker
```

#### Problem: Backend build fails on Python dependencies
```bash
# Check build logs
docker-compose build backend 2>&1 | tee build.log

# Common fixes:
# 1. Insufficient RAM - increase swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 2. Missing system libraries - install build deps
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    libpq-dev \
    libgl1-mesa-dev \
    libglib2.0-dev \
    gcc \
    g++

# 3. Rebuild without cache
docker-compose build --no-cache backend
```

#### Problem: Frontend build fails
```bash
# Check Node.js version in container
docker run --rm node:25-alpine node --version

# Build with more memory
docker-compose build --build-arg NODE_OPTIONS="--max-old-space-size=4096" frontend

# Or edit frontend/Dockerfile and add:
# ENV NODE_OPTIONS="--max-old-space-size=4096"
```

---

### 4. Runtime Issues

#### Problem: Backend container keeps restarting
```bash
# Check logs
docker logs aads-backend --tail 100

# Common causes:
# 1. Database not ready - wait 30 seconds and check again
# 2. Missing environment variables
docker exec aads-backend env | grep DATABASE_URL

# 3. Port already in use
sudo lsof -i :8000
# Kill process using port: sudo kill -9 <PID>

# Restart with verbose logging
docker-compose logs -f backend
```

#### Problem: Ollama out of memory
```bash
# Check GPU memory
nvidia-smi

# For Jetson Nano Orin DevKit (12GB RAM):
# Use smaller model or reduce batch size

# Edit docker-compose.yml, reduce Ollama memory:
# environment:
#   - OLLAMA_MAX_LOADED_MODELS=1
#   - OLLAMA_NUM_PARALLEL=1

# Or use smaller model
docker exec aads-navi-ollama ollama pull llama3.2:1b  # 1B parameter model (~700MB)

# Update backend environment:
# OLLAMA_MODEL=llama3.2:1b
```

#### Problem: PostgreSQL won't start
```bash
# Check logs
docker logs aads-postgres

# Common fixes:
# 1. Corrupted volume - remove and recreate
docker-compose down
docker volume rm navi-main_postgres_data
docker-compose up -d postgres

# 2. Permission issues
docker exec aads-postgres ls -la /var/lib/postgresql/data
docker exec aads-postgres chown -R postgres:postgres /var/lib/postgresql/data
```

---

### 5. Network Issues

#### Problem: Cannot access frontend from other devices
```bash
# Check firewall
sudo ufw status

# Allow ports
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 8000/tcp  # Backend

# Or disable firewall temporarily for testing
sudo ufw disable

# Check container networking
docker network inspect navi-main_aads-network

# Verify IP address
hostname -I
```

#### Problem: Backend cannot connect to Ollama
```bash
# Check if Ollama container is running
docker ps | grep ollama

# Test connection from backend container
docker exec aads-backend curl http://navi:11434/api/version

# Check docker-compose network configuration
# Ensure all services are on same network:
# networks:
#   - aads-network
```

#### Problem: WebSocket connection fails
```bash
# Check environment variables in frontend
docker exec aads-frontend cat /etc/nginx/conf.d/default.conf | grep proxy_pass

# Update VITE_WS_URL in docker-compose.yml
# Use Jetson's actual IP address, not localhost
# VITE_WS_URL=ws://192.168.39.196:8000/ws

# Rebuild frontend
docker-compose up -d --build frontend
```

---

### 6. Performance Issues

#### Problem: System slow or laggy
```bash
# Check CPU/GPU usage
tegrastats

# Check temperatures
cat /sys/devices/virtual/thermal/thermal_zone*/temp
# Should be < 85000 (85°C)

# Ensure MAXN mode
sudo nvpmodel -m 0
sudo jetson_clocks

# Check running processes
htop

# Reduce workload:
# 1. Lower camera FPS
# 2. Reduce Ollama concurrent requests
# 3. Use smaller AI models
```

#### Problem: High memory usage
```bash
# Check memory
free -h

# Check per-container usage
docker stats

# Reduce memory usage:
# 1. Limit container memory in docker-compose.yml
# services:
#   backend:
#     mem_limit: 2g
#     memswap_limit: 4g

# 2. Increase swap
sudo swapon --show
sudo fallocate -l 8G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

### 7. Audio/Voice System Issues

#### Problem: Voice system not working
```bash
# Check if audio directories exist
ls -la models/piper/
ls -la audio/

# Download Piper voice model if missing
mkdir -p models/piper
cd models/piper
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
cd ../..

# Check backend logs for voice errors
docker logs aads-backend | grep -i "voice\|piper\|whisper"

# Verify volumes mounted correctly
docker inspect aads-backend | grep -A 10 "Mounts"

# Test Whisper in container
docker exec -it aads-backend python -c "import whisper; print(whisper.available_models())"
```

#### Problem: Audio device not found
```bash
# List audio devices on Jetson
aplay -l

# Check if ALSA is installed
sudo apt-get install -y alsa-utils pulseaudio

# For USB audio devices, might need to pass through:
# Add to docker-compose.yml backend service:
# devices:
#   - /dev/snd:/dev/snd
# privileged: true  # Only if absolutely necessary
```

---

### 8. Camera Issues

#### Problem: Camera not detected
```bash
# List video devices
ls -la /dev/video*

# Test camera with v4l2
sudo apt-get install -y v4l-utils
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --all

# Add camera to docker-compose.yml backend:
# devices:
#   - /dev/video0:/dev/video0

# For IP cameras, no device needed - use RTSP URL in config
```

---

### 9. Environment-Specific Issues

#### Problem: Running in development vs production
```bash
# Check current environment
docker exec aads-backend env | grep ENVIRONMENT

# Switch to development mode (more logging)
# Edit docker-compose.yml:
# environment:
#   - ENVIRONMENT=development
#   - LOG_LEVEL=DEBUG

docker-compose up -d --force-recreate backend
```

#### Problem: .env file not loaded
```bash
# Check if .env exists
ls -la .env

# Docker Compose automatically loads .env from same directory
# If using different location:
docker-compose --env-file /path/to/.env up -d

# Verify environment variables in container
docker exec aads-backend env
```

---

### 10. Update/Deployment Issues

#### Problem: Git pull fails
```bash
# Check git status
git status

# If you have local changes
git stash
git pull origin main
git stash pop

# Or reset to remote (WARNING: loses local changes)
git fetch origin
git reset --hard origin/main
```

#### Problem: Rebuild after code changes not working
```bash
# Force rebuild without cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Or rebuild specific service
docker-compose up -d --build --force-recreate backend
```

---

## Quick Diagnostic Commands

### Full System Check
```bash
#!/bin/bash
echo "=== Jetson System Check ==="
echo ""

echo "1. OS Info:"
uname -a
cat /etc/os-release | grep PRETTY_NAME

echo -e "\n2. Memory:"
free -h

echo -e "\n3. Disk Space:"
df -h /

echo -e "\n4. Docker Status:"
docker --version
docker-compose --version
sudo systemctl status docker --no-pager

echo -e "\n5. Docker Containers:"
docker ps -a

echo -e "\n6. GPU Status:"
nvidia-smi

echo -e "\n7. CPU Temperature:"
cat /sys/devices/virtual/thermal/thermal_zone*/temp

echo -e "\n8. Network Interfaces:"
hostname -I

echo -e "\n9. Active Ports:"
sudo netstat -tulpn | grep LISTEN

echo -e "\n10. Docker Volumes:"
docker volume ls
```

Save as `check-system.sh`, run: `bash check-system.sh`

---

## Emergency Recovery

### Complete Reset (Use with caution!)
```bash
# Stop all containers
docker-compose down

# Remove all Docker data (WARNING: DELETES EVERYTHING)
docker system prune -a --volumes -f

# Remove project volumes
docker volume rm $(docker volume ls -q | grep navi-main)

# Fresh start
git pull origin main
docker-compose up -d --build

# Re-pull Ollama model
docker exec aads-navi-ollama ollama pull llama3.2
```

---

## Getting Help

If issues persist:

1. **Collect logs:**
```bash
docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).txt
```

2. **System info:**
```bash
bash check-system.sh > system_info.txt
```

3. **Check documentation:**
- `JETSON_DEPLOYMENT_GUIDE.md`
- `START_HERE.md`
- `README.md`

4. **Common resources:**
- NVIDIA Jetson Forums: https://forums.developer.nvidia.com/c/agx-autonomous-machines/jetson-embedded-systems
- Docker Docs: https://docs.docker.com

---

**Last Updated:** 2026-01-23
**Target Platform:** NVIDIA Jetson (Ubuntu 20.04/22.04)
