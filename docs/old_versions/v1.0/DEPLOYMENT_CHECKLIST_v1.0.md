# AADS PRO - Production Deployment Checklist
## Version 4.2.0-JETSON
## Date: 2026-01-23

---

## ✅ Pre-Sensor Mounting Status

All critical fixes have been completed. System is **READY FOR SENSOR MOUNTING**.

---

## 1. Quick Status Overview

| Component | Status | Notes |
|-----------|--------|-------|
| React Build | ✅ PASS | No errors, 5.95s build time |
| Mock Data Removed | ✅ DONE | Dashboard using real data only |
| AI Models | ✅ READY | All 5 modules operational |
| Signal K | ✅ READY | Production config verified |
| Gauges | ✅ READY | 4 gauges configured |
| UI Proportions | ✅ FIXED | Responsive CSS implemented |
| Technical Report | ✅ DONE | Complete documentation |

---

## 2. Before You Mount Sensors

### 2.1 Create Production Environment File

**Location:** `backend/.env`

```bash
# Copy this template and fill in your values
cp backend/.env.example backend/.env
```

**Critical Settings:**
```bash
# MUST BE SET TO FALSE FOR PRODUCTION
DEV_MODE=false
MOCK_CAMERA=false  # When camera is connected
NMEA_MOCK_DATA=false
SIGNALK_MOCK_DATA=false

# Verify these URLs match your network
OLLAMA_BASE_URL=http://192.168.39.196:11434
REDIS_URL=redis://192.168.39.196:6379/0
INFLUXDB_URL=http://192.168.39.196:8086

# Enable hardware monitoring
HARDWARE_MONITOR_ENABLED=true
FAN_CONTROL_ENABLED=true
NMEA_ENABLED=true
SIGNALK_ENABLED=true
```

### 2.2 Verify Signal K Server

```bash
# Test Signal K is running
curl http://localhost:3000/signalk/v1/api/

# Should return JSON with server info
```

### 2.3 Verify Ollama AI Service

```bash
# Check Ollama is running
curl http://192.168.39.196:11434/api/tags

# Download production model if not present
ollama pull llama3.2
```

---

## 3. Sensor Connection Guide

### 3.1 GPS/NMEA Sensor
- **Port:** `/dev/ttyUSB0` (default)
- **Baud Rate:** 4800
- **Test Command:**
  ```bash
  python -c "import serial; s=serial.Serial('/dev/ttyUSB0', 4800, timeout=1); print(s.readline())"
  ```
- **Expected Output:** NMEA sentences like `$GPGGA,123456.00,5912.1234,N,01034.5678,E...`

### 3.2 Signal K Sensors
All sensors should feed into Signal K server which AADS consumes:

**Required Sensors:**
- [ ] GPS/Position (`navigation.position`)
- [ ] Speed sensor (`navigation.speedOverGround`)
- [ ] Compass/Heading (`navigation.headingMagnetic`)
- [ ] Depth sounder (`environment.depth.belowTransducer`)
- [ ] Water temperature (`environment.water.temperature`)

**Optional Sensors:**
- [ ] Wind speed/direction (`environment.wind.*`)
- [ ] Air temperature (`environment.outside.temperature`)
- [ ] Engine RPM (`propulsion.*.revolutions`)
- [ ] Fuel levels (`tanks.fuel.*`)

### 3.3 Camera (YOLO Vision)
- **Type:** USB camera or Jetson CSI camera
- **Device ID:** Default is `0`
- **Configuration:**
  ```bash
  # Set in .env
  MOCK_CAMERA=false
  CAMERA_DEVICE_ID=0
  CAMERA_WIDTH=1920
  CAMERA_HEIGHT=1080
  ```
- **Test Command:**
  ```bash
  python -c "import cv2; cap=cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera FAIL')"
  ```

---

## 4. First Boot Procedure

### 4.1 Start Backend
```bash
cd backend
source venv/bin/activate  # If using virtual environment
python -m app.main
```

**Watch for:**
- ✅ `NMEA reader started`
- ✅ `Signal K connected`
- ✅ `Ollama health check: OK`
- ✅ `Hardware monitor started`
- ✅ `WebSocket server running`

### 4.2 Start Frontend
```bash
cd frontend
npm run dev
# Or for production build:
npm run build && npm run preview
```

### 4.3 Open Browser
Navigate to: `http://localhost:5173` (dev) or `http://localhost:4173` (preview)

---

## 5. Verification Tests

### 5.1 Gauge Data Flow
1. Go to **DASHBOARD** module
2. Verify gauges show:
   - Speed (should update with boat movement)
   - Heading (should update with compass)
   - Depth (should show current depth)
   - Temperature (should show water temp)
3. If not connected to Signal K, warning should appear

### 5.2 AI Models Test
```bash
# Test NAVI Chat
curl -X POST http://localhost:8000/api/v1/navi/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello NAVI, can you hear me?"}'

# Test Medical Assessment
curl -X POST http://localhost:8000/api/v1/legen/assess \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["headache", "nausea"], "severity": "medium"}'
```

### 5.3 Gordon System Monitor
1. Open **ENGIN** (Ingeniøren) module
2. Verify displays:
   - CPU usage %
   - Memory usage %
   - Disk usage %
   - Temperature (if sensor available)
   - Fan speed %
   - Leeway angle
   - Drift speed

---

## 6. Production Monitoring

### 6.1 Key Metrics to Watch

**System Health:**
- CPU usage should be < 80% under normal load
- Memory usage should be < 85%
- Temperature should be < 75°C
- Fan should auto-adjust based on temp

**Data Flow:**
- Signal K connection: Green dot in header
- NMEA data: Check timestamp updates
- AI responses: Should be < 5s response time

### 6.2 Log Files

**Backend Logs:**
```bash
tail -f backend/logs/aads.log
```

**Watch for:**
- `ERROR` - Critical issues
- `WARNING` - Non-critical but investigate
- `INFO` - Normal operation logs

---

## 7. Troubleshooting

### Issue: Gauges Show 0 Values
**Cause:** Signal K not connected
**Fix:**
1. Verify Signal K server: `curl http://localhost:3000/signalk/v1/api/`
2. Check `SIGNALK_SERVER_URL` in `.env`
3. Restart backend service

### Issue: NAVI Not Responding
**Cause:** Ollama service down
**Fix:**
1. Check Ollama: `curl http://192.168.39.196:11434/api/tags`
2. Restart Ollama service
3. Verify model downloaded: `ollama list`

### Issue: GPS Not Working
**Cause:** Serial port permissions or wrong port
**Fix:**
1. Check port exists: `ls -l /dev/ttyUSB0`
2. Add user to dialout group: `sudo usermod -a -G dialout $USER`
3. Reboot
4. Verify NMEA sentences: `cat /dev/ttyUSB0`

### Issue: High CPU Usage
**Cause:** YOLO running on CPU instead of GPU
**Fix:**
1. Verify CUDA: `nvidia-smi`
2. Check PyTorch GPU: `python -c "import torch; print(torch.cuda.is_available())"`
3. Reinstall PyTorch with CUDA support if False

### Issue: Temperature Sensor Not Available
**Cause:** Jetson thermal zones not accessible
**Fix:**
- This is normal on some systems
- Gordon will show "N/A" for temperature
- Fan control will use default curve

---

## 8. Daily Operation Checklist

### Before Departure
- [ ] Verify backend running: `systemctl status aads-backend` (if using systemd)
- [ ] Check Signal K connection (green dot in UI)
- [ ] Verify GPS lock (position updating)
- [ ] Test NAVI response: "Hey NAVI, system check"
- [ ] Check fuel levels (if sensor connected)
- [ ] Verify camera feed (Vision module)

### During Operation
- [ ] Monitor CPU temperature (should stay < 75°C)
- [ ] Watch for anomaly alerts (YOLO detections)
- [ ] Check XTE (Cross-Track Error) if using autopilot
- [ ] Monitor wind leeway compensation
- [ ] Review Gordon health score (should be > 70)

### After Return
- [ ] Save voyage logs
- [ ] Review anomaly detections
- [ ] Check for system warnings in logs
- [ ] Update medical records if incidents occurred
- [ ] Backup telemetry data (InfluxDB export if needed)

---

## 9. Performance Baselines

### Expected Performance (Jetson Orin Nano)

**System Resources:**
- Idle CPU: 15-25%
- Active CPU (with YOLO): 40-60%
- Memory: 2-4 GB
- Temperature: 45-65°C (ambient dependent)
- Fan speed: 30-70% (auto-controlled)

**Response Times:**
- NAVI chat response: 2-5 seconds
- Medical assessment: 3-6 seconds
- YOLO detection frame: 30-60 FPS (GPU)
- Signal K update latency: < 1 second
- Gauge refresh rate: 1 Hz

**Network:**
- WebSocket latency: < 50ms (local network)
- Signal K latency: < 100ms
- Ollama API: < 2s (model dependent)

---

## 10. Emergency Procedures

### If System Becomes Unresponsive
1. Do NOT force shutdown immediately
2. Check if process is running: `ps aux | grep python`
3. Try graceful restart: `pkill -SIGTERM python`
4. Wait 10 seconds for shutdown
5. If hung, force kill: `pkill -9 python`
6. Check logs for cause before restart

### If Navigation Data Lost
1. Check Signal K server status
2. Verify NMEA GPS still connected
3. Fallback to manual navigation
4. System will show warning: "Not connected to Signal K"
5. Last known values will be displayed

### If AI Models Fail
1. Navigation and monitoring will continue
2. Chat features will be unavailable
3. Medical assessments will fallback to protocol list
4. System remains operational for core functions

---

## 11. Support and Documentation

**Full Technical Report:** `TECHNICAL_REPORT.md`
**Configuration Reference:** `backend/app/core/config.py`
**API Documentation:** `http://localhost:8000/docs` (when backend running)

**Key Contacts:**
- System Version: AADS PRO v4.2.0-JETSON
- Build Date: 2026-01-23
- Platform: NVIDIA Jetson Orin Nano

---

## ✅ SYSTEM STATUS: READY FOR DEPLOYMENT

All pre-checks completed successfully. System is production-ready for sensor mounting and sea trials.

**Last Updated:** 2026-01-23
**Next Review:** After first sensor integration test
