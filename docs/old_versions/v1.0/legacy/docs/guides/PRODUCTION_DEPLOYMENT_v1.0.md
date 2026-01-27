**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# Production Deployment Guide

## Overview
All mock data has been disabled for production. The system now uses **real data sources**:
- âœ… Navi AI - Real Ollama models (requires model download)
- âœ… Vakten - Real camera + YOLOv8 vision (requires OpenCV + ultralytics)
- âœ… NMEA GPS - Real GPS hardware (requires /dev/ttyUSB0 GPS module)
- âœ… Signal K - Real Signal K server (if available)

## Prerequisites

Before deploying, ensure your Jetson has:

### 1. GPS Hardware
```bash
# Check if GPS is available
ls -la /dev/ttyUSB*

# If no device, you can still test with USB-to-Serial GPS module
# Popular: u-blox, GlobalSat, etc.
```

### 2. Camera
```bash
# Check camera
ls -la /dev/video*

# Test camera
v4l2-ctl --list-devices
```

### 3. Ollama Model Downloaded
```bash
# Pull production model (4-6GB)
docker exec aads-navi-ollama ollama pull mistral

# Verify
docker exec aads-navi-ollama ollama list
```

### 4. Signal K Server (Optional)
If you have a Signal K server running:
```bash
# Configure in docker-compose.yml or environment
SIGNALK_SERVER_URL=ws://signalk-ip:3000/signalk/v1/stream
```

## Deployment Steps

### Step 1: Update Environment
```bash
cd ~/navi-main
git pull
```

### Step 2: Configure for Production
Copy production config:
```bash
cp .env.production .env
```

Or manually configure (edit `.env`):
```bash
# Key changes from development:
ENVIRONMENT=production
DEV_MODE=false
NMEA_MOCK_DATA=false
SIGNALK_MOCK_DATA=false
MOCK_CAMERA=false
```

### Step 3: Verify Hardware
```bash
# Check GPS
cat /dev/ttyUSB0  # Should see NMEA data ($GPGGA, $GPRMC, etc)
Ctrl+C to exit

# Check Camera
ffplay /dev/video0  # Should show video feed

# Check Ollama
docker exec aads-navi-ollama ollama list  # Should show models
```

### Step 4: Rebuild and Deploy
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Step 5: Verify Services
```bash
# Check all services running
docker ps

# Check backend logs
docker logs aads-backend | tail -50

# Test Navi AI
curl -X POST "http://localhost:8000/api/v1/navi/chat?message=Hello"
```

## Expected Behavior

### Navi (AI Assistant)
- **Before**: "Acknowledged: Hello. I'm here to assist." (mock response)
- **After**: Real AI response from Ollama (takes 2-5 seconds)
- **Requires**: Ollama model downloaded + real Ollama connection

### Vakten (Vision System)
- **Before**: Synthetic detections of ice/ships/people
- **After**: Real detections from camera feed
- **Requires**: USB camera + YOLOv8 model loaded

### NMEA GPS
- **Before**: Simulated position at 78.2232Â°N, 15.6267Â°E (Svalbard)
- **After**: Real GPS position from /dev/ttyUSB0
- **Requires**: GPS hardware connected via USB

### Signal K
- **Before**: Mock navigation data
- **After**: Real data from Signal K server
- **Requires**: Signal K server running and configured

## Troubleshooting

### Navi says "failed to reach navi system may be offline"
1. Check Ollama is running: `docker logs aads-navi-ollama`
2. Check model is downloaded: `docker exec aads-navi-ollama ollama list`
3. Check backend config: `docker logs aads-backend | grep Navi`

### GPS not working
1. Check device exists: `ls -la /dev/ttyUSB*`
2. Check baud rate: `stty -F /dev/ttyUSB0`  (should be 4800)
3. Check permission: `sudo chmod 666 /dev/ttyUSB0`
4. Check logs: `docker logs aads-backend | grep NMEA`

### Camera not loading
1. Check device: `ls -la /dev/video*`
2. Check OpenCV: `python3 -c "import cv2; print(cv2.__version__)"`
3. Check YOLO: `pip list | grep ultralytics`
4. Check logs: `docker logs aads-backend | grep Vakten`

### Performance Issues
If system is slow:
1. Reduce camera resolution: `CAMERA_WIDTH=1280 CAMERA_HEIGHT=720`
2. Use smaller Ollama model: `ollama pull neural-chat`
3. Reduce FPS: `CAMERA_FPS=15`
4. Increase timeouts: `OLLAMA_TIMEOUT=180`

## Rollback to Development

If you need to test with mock data:

```bash
cp .env.development .env
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

This will restore:
- Mock GPS data
- Mock Signal K data
- Mock camera detections
- Faster response times

## Configuration Reference

### Disable Specific Real Data Sources
If hardware not available, you can selectively enable mock mode:

```bash
# Use real Navi but mock GPS
NMEA_MOCK_DATA=true
SIGNALK_MOCK_DATA=false

# Use real GPS but mock camera
NMEA_MOCK_DATA=false
MOCK_CAMERA=true

# Use real everything except Signal K
SIGNALK_MOCK_DATA=true
```

## Production Checklist

Before deployment, verify:

- [ ] All containers build without errors
- [ ] Backend starts successfully: `curl http://localhost:8000/health`
- [ ] Frontend loads: `curl http://localhost:3000`
- [ ] GPS data appears in logs: `docker logs aads-backend | grep latitude`
- [ ] Camera feed works: Check in Vakten module UI
- [ ] Navi responds with real AI: Ask it a question
- [ ] WebSocket connected: Check browser console
- [ ] All 7 services running: `docker ps | wc -l` should be >= 7

## Monitoring

### Real-time logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f aads-navi-ollama
```

### Check data flow
```bash
# GPS data
docker exec aads-backend curl localhost:8000/api/v1/nmea/data

# Vision detections
docker exec aads-backend curl localhost:8000/api/v1/vakten/detections

# AI response
docker exec aads-backend curl -X POST localhost:8000/api/v1/navi/chat?message=test
```

## Performance Notes

### Typical Response Times (Production)
- Navi (AI): 2-5 seconds (depends on model and message length)
- Vakten (Vision): 30-50ms per frame (real-time)
- NMEA GPS: 10ms per update
- Signal K: Real-time streaming

### Hardware Requirements
- **Jetson Orin DevKit**: 8GB RAM, 12-core ARM (sufficient for all features)
- **GPU**: NVIDIA Tensor cores (used by Ollama and YOLOv8)
- **Storage**: 50GB+ (for models and data)

---

**Status**: âœ… Production-ready when hardware is available
**Last Updated**: January 22, 2026
**Version**: 1.0.0 Production

