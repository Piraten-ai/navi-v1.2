# 🚀 QUICK START - Sensor Mounting Day
## AADS PRO v4.2.0-JETSON

---

## ✅ PRE-FLIGHT CHECK (ALL PASSED)

- [x] React Error #31 fixed
- [x] Mock data removed
- [x] UI responsive
- [x] All AI models ready
- [x] Signal K configured
- [x] Build: **0 errors, 0 warnings**

**Status: READY FOR SENSORS** ✅

---

## 🔌 TODAY'S TASKS - SENSOR CONNECTION

### Step 1: Backend Configuration (5 min)
```bash
cd backend
cp .env.example .env
nano .env
```

**Set these values:**
```bash
DEV_MODE=false
NMEA_MOCK_DATA=false
SIGNALK_MOCK_DATA=false
HARDWARE_MONITOR_ENABLED=true
NMEA_ENABLED=true
SIGNALK_ENABLED=true
```

### Step 2: Verify Services (2 min)
```bash
# Check Signal K
curl http://localhost:3000/signalk/v1/api/

# Check Ollama
curl http://192.168.39.196:11434/api/tags

# Should see llama3.2 model
```

### Step 3: Connect GPS (10 min)
```bash
# Test NMEA GPS connection
ls -l /dev/ttyUSB0

# Read raw NMEA sentences
cat /dev/ttyUSB0

# Should see: $GPGGA,123456.00,5912.1234,N...
```

**If permission denied:**
```bash
sudo usermod -a -G dialout $USER
# Then reboot
```

### Step 4: Start Backend (1 min)
```bash
cd backend
python -m app.main
```

**Watch for:**
- ✅ `NMEA reader started`
- ✅ `Signal K connected`
- ✅ `Ollama health check: OK`

### Step 5: Start Frontend (1 min)
```bash
cd frontend
npm run dev
```

Open browser: `http://localhost:5173`

### Step 6: Verify Data Flow (5 min)

1. **Go to DASHBOARD module**
   - Speed gauge should update
   - Heading gauge should update
   - Depth gauge should update
   - Temperature gauge should update

2. **Check connection status**
   - Header should show: `● BACKEND` (green)
   - No "Not connected to Signal K" warning

3. **Test NAVI AI**
   - Go to NAVI AI module
   - Type: "Hello NAVI"
   - Should get response in 2-5 seconds

4. **Check GORDON (Ingeniøren)**
   - Go to ENGIN module
   - Should show:
     - CPU usage %
     - Memory usage %
     - Temperature
     - Fan speed

---

## 📋 SENSOR CHECKLIST

### Required Sensors (Connect to Signal K)
- [ ] GPS/GNSS (NMEA or NMEA2000)
- [ ] Speed sensor (paddlewheel or log)
- [ ] Compass/Heading (magnetic or GPS)
- [ ] Depth sounder (transducer)
- [ ] Water temperature (integrated with depth)

### Optional Sensors
- [ ] Wind speed/direction
- [ ] Air temperature
- [ ] Engine RPM
- [ ] Fuel level

---

## 🐛 QUICK TROUBLESHOOTING

### Gauges Show 0
**Problem:** Signal K not connected
**Fix:**
```bash
# Verify Signal K running
curl http://localhost:3000/signalk/v1/api/
# Restart backend
```

### NAVI Not Responding
**Problem:** Ollama down
**Fix:**
```bash
# Check Ollama
curl http://192.168.39.196:11434/api/tags
# If failed, restart Ollama service
```

### GPS Not Working
**Problem:** Serial port permissions
**Fix:**
```bash
sudo usermod -a -G dialout $USER
sudo reboot
```

---

## 📞 DOCUMENTATION

- **Complete Guide:** `TECHNICAL_REPORT.md`
- **Deployment Steps:** `DEPLOYMENT_CHECKLIST.md`
- **Bug Fixes:** `HOTFIX_REACT_ERROR_31.md`
- **Today's Changes:** `FIXES_APPLIED_2026-01-23.md`

---

## 🎯 SUCCESS CRITERIA

By end of today, you should have:
- ✅ All sensors connected to Signal K
- ✅ Gauges showing real-time data
- ✅ NAVI AI responding to chat
- ✅ GORDON showing system metrics
- ✅ No errors in console

---

## 🚨 IMPORTANT NOTES

1. **MOCK_CAMERA=true** still set - Change to `false` when camera connected
2. **Gordon is NOT AI** - It's a system monitor (can add Edge AI later)
3. **Type checking added** - React Error #31 is fixed
4. **Responsive UI** - Works on different screen sizes now

---

**System Ready:** YES ✅
**Build Status:** SUCCESS
**Time to Mount:** NOW 🔧

Good luck with the sensor installation! 🚢
