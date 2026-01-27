**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# NAVI Deployment Guide

Complete deployment guide for NAVI (Arctic Autonomy Decision Support System) on NVIDIA Jetson hardware.

## ðŸŽ¯ Quick Start - Single Command

**Deploy to any Jetson device with ONE command:**

```bash
curl -sSL https://raw.githubusercontent.com/Piraten-ai/navi-main/main/deploy/install_complete.sh | sudo bash
```

That's it! The script handles:
- Docker installation
- All dependencies
- Building containers
- Starting all services
- Health verification

**For 1000 units:** Create a deployment image with this command baked in, or run via SSH/MDM.

---

## ðŸ“ Access After Installation

- **Dashboard:** http://`[jetson-ip]`:3000
- **API Docs:** http://`[jetson-ip]`:8000/docs
- **Backend Health:** http://`[jetson-ip]`:8000/health

Find Jetson IP: `arp-scan -l` (or check your router)

---

## ðŸ› ï¸ Manual/Advanced Options

### Scout Edition (Jetson Nano 8GB)
```bash
cd ./deploy
sudo bash install_scout.sh
```

### Pro Edition (Jetson Orin NX 16GB)
```bash
cd ./deploy
sudo bash install_pro.sh
```

### Development Mode (Laptop)
```bash
docker-compose -f docker-compose.dev.yml up -d
```

---

## ðŸ“‹ Prerequisites

### Hardware Requirements

**Scout Edition:**
- NVIDIA Jetson Nano 8GB
- 128GB+ SD card or SSD
- 5V 4A power supply
- USB camera or CSI camera
- Optional: Coral TPU USB accelerator

**Pro Edition:**
- NVIDIA Jetson Orin NX 16GB
- 256GB+ NVMe SSD
- Power supply (19V)
- USB/CSI camera
- Optional: Coral TPU M.2 accelerator

**Development (Laptop):**
- 8GB+ RAM
- 10GB free disk space
- Docker & Docker Compose
- Any modern OS (Linux/macOS/Windows+WSL2)

### Software Prerequisites

- JetPack 5.0+ (for Jetson devices)
- Docker 20.10+
- Docker Compose 1.29+
- Git

---

## ðŸš€ Installation Steps

### 1. Prepare Jetson Device

**Flash JetPack:**
```bash
# Download SDK Manager from NVIDIA
# Flash JetPack 5.1+ to SD card/NVMe
```

**First Boot Setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl nano htop

# Check NVIDIA setup
nvidia-smi  # Should show GPU info
```

### 2. Run Installer

**For Scout (Nano):**
```bash
cd /opt
git clone https://github.com/Piraten-ai/navi-main.git
cd navi-main/deploy
sudo bash install_scout.sh
```

**For Pro (Orin):**
```bash
cd /opt
git clone https://github.com/Piraten-ai/navi-main.git
cd navi-main/deploy
sudo bash install_pro.sh
```

**What the installer does:**
1. Installs Docker & Docker Compose
2. Installs NVIDIA Container Toolkit
3. Optimizes power/performance settings
4. Creates swap space (4GB/8GB)
5. Pulls Docker images
6. Builds custom images
7. Starts all services
8. Pulls Ollama model

â±ï¸ **Installation time:** 15-30 minutes (depending on internet speed)

### 3. Verify Installation

```bash
# Check services
docker-compose ps

# Check logs
docker-compose logs -f backend

# Test health endpoint
curl http://localhost:8000/health

# Access dashboard
open http://localhost:3000
```

---

## âš™ï¸ Configuration

### Environment Variables

Edit `.env` file to customize:

```bash
# Core settings
ENVIRONMENT=production
DEV_MODE=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://aads:password@postgres:5432/aads

# Ollama model
OLLAMA_MODEL=llama3.2:1b  # Scout: 1b, Pro: full model

# Performance
WS_MAX_CONNECTIONS=10  # Scout: 10, Pro: 50
BATCH_SIZE=1           # Scout: 1, Pro: 4
FPS_TARGET=15          # Scout: 15, Pro: 30

# Camera
MOCK_CAMERA=false      # Set to true for testing without camera
```

### Docker Compose Profiles

**Full stack (default):**
```bash
docker-compose up -d
```

**Development mode:**
```bash
docker-compose -f docker-compose.dev.yml up -d
```

**Individual services:**
```bash
docker-compose up -d backend  # Backend only
docker-compose up -d frontend # Frontend only
```

---

## ðŸ”§ Management

### Start/Stop Services

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Restart single service
docker-compose restart backend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Update System

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Pull new Ollama model if needed
docker exec aads-navi-ollama ollama pull llama3.2
```

### Database Management

```bash
# Backup database
docker exec aads-postgres pg_dump -U aads aads > backup.sql

# Restore database
cat backup.sql | docker exec -i aads-postgres psql -U aads aads

# Connect to database
docker exec -it aads-postgres psql -U aads
```

---

## ðŸ“Š Monitoring

### System Resources

**Jetson stats:**
```bash
# Install jtop
sudo -H pip3 install jetson-stats

# Monitor
sudo jtop
```

**Docker stats:**
```bash
docker stats
```

**Check temperatures:**
```bash
cat /sys/devices/virtual/thermal/thermal_zone*/temp
```

### Service Health

**Backend:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/status
```

**Frontend:**
```bash
curl http://localhost:3000
```

**API Docs:**
```
http://localhost:8000/docs
```

---

## ðŸ› Troubleshooting

### Services Won't Start

**Check logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Common issues:**
- Insufficient memory: Check swap is active (`free -h`)
- Port conflicts: Check ports 3000, 8000 are free
- Permission issues: Ensure user is in docker group

### Camera Not Working

**Test camera:**
```bash
# Check device
ls /dev/video*

# Test with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera:', cap.isOpened())"
```

**Solutions:**
- Ensure camera is plugged in
- Check permissions: `sudo chmod 666 /dev/video0`
- Try mock mode: Set `MOCK_CAMERA=true` in `.env`

### Ollama Model Issues

**Pull model manually:**
```bash
docker exec aads-navi-ollama ollama pull llama3.2:1b
```

**Check available models:**
```bash
docker exec aads-navi-ollama ollama list
```

### Performance Issues

**Scout (Nano):**
- Reduce FPS: Set `FPS_TARGET=10`
- Use smaller model: `OLLAMA_MODEL=llama3.2:1b`
- Check cooling: Ensure heatsink/fan working

**Pro (Orin):**
- Enable max performance: `sudo nvpmodel -m 0`
- Max clocks: `sudo jetson_clocks`
- Check power supply: Ensure adequate wattage

### Memory Issues

**Check memory:**
```bash
free -h
docker stats
```

**Solutions:**
- Ensure swap is active
- Reduce batch size
- Restart services: `docker-compose restart`
- Clear cache: `docker system prune -a`

---

## ðŸ”’ Security

### Production Recommendations

1. **Change default passwords** in `.env`
2. **Enable firewall:**
   ```bash
   sudo ufw allow 22    # SSH
   sudo ufw allow 3000  # Frontend (or use reverse proxy)
   sudo ufw enable
   ```
3. **Use reverse proxy** (nginx) for HTTPS
4. **Disable root SSH:** Edit `/etc/ssh/sshd_config`
5. **Regular updates:** `sudo apt update && sudo apt upgrade`

### Network Isolation

For maximum security (offline operation):
```bash
# Disable WiFi/Ethernet after installation
sudo nmcli radio wifi off
```

---

## ðŸ“– Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **Testing Guide:** [TESTING.md](../TESTING.md)
- **Build Specification:** [BUILD_SPEC.md](../BUILD_SPEC.md)
- **GitHub Repository:** https://github.com/Piraten-ai/navi-main

---

## ðŸ†˜ Support

**Logs location:** `/opt/navi-main/logs/`
**Data location:** `/opt/navi-main/data/`
**Config:** `/opt/navi-main/.env`

---

ðŸ§Š **"When satellites fail, we survive."** âš“

