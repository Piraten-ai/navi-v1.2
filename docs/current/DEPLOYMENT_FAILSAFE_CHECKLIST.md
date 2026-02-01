# 🛑 DEPLOYMENT FAILSAFE CHECKLIST

**Purpose:** Prevent premature deployment and ensure complete understanding of system before work begins.

**Required Reading Before Any Work:** ⚠️ MANDATORY

---

## PRE-DEPLOYMENT KNOWLEDGE REQUIREMENTS

### ✅ SECTION 1: System Architecture Understanding

**MUST KNOW BEFORE PROCEEDING:**

- [ ] **Network Layout**
  - Jetson (AI/Vision): `192.168.39.151` (ssh: navi@, pw: 1122)
  - Raspberry Pi (Control): `192.168.39.142` (ssh: navi@, pw: 1122)
  - Tablet (Dashboard): `192.168.39.102` (ssh: [user]@, pw: 1122)
  - IP Camera (EZVIZ): `192.168.39.200` (ONVIF PTZ ready)

- [ ] **Backend Service Location**
  - Path: `/home/navi/AADS/backend`
  - Running on: Jetson Nano (7.4GB RAM)
  - Process: `python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Status: Currently running (NOT in Docker)

- [ ] **Memory Constraints**
  - Total Jetson: 7.4GB
  - Backend using: ~633MB
  - Available: ~5.5GB
  - AI Model: phi3:mini (lightweight, not llama2)
  - Redis: NOT running (disabled to save memory)

- [ ] **Branch/Version Info**
  - Production Branch: `production` (at commit `f317eb8b`)
  - Contains: PTZ camera control + SenseHAT display + NMEA autopilot
  - Status: Deployed and running on Jetson

---

### ✅ SECTION 2: PTZ Camera Control System

**MUST UNDERSTAND BEFORE ENABLING PTZ:**

- [ ] **What PTZ Does**
  - Controls EZVIZ IP camera (192.168.39.200)
  - Pan: ±180° (left/right)
  - Tilt: ±90° (up/down)
  - Zoom: 0.0 to 1.0
  - Tracks detected objects automatically

- [ ] **9 API Endpoints Available**
  1. `GET /api/v1/ptz/status` → Camera position & connection
  2. `POST /api/v1/ptz/connect` → Establish ONVIF connection
  3. `POST /api/v1/ptz/disconnect` → Close connection
  4. `POST /api/v1/ptz/pan-left` → Pan left with speed/duration
  5. `POST /api/v1/ptz/pan-right` → Pan right with speed/duration
  6. `POST /api/v1/ptz/tilt-up` → Tilt up with speed/duration
  7. `POST /api/v1/ptz/tilt-down` → Tilt down with speed/duration
  8. `POST /api/v1/ptz/move` → Absolute position (pan, tilt, zoom)
  9. `POST /api/v1/ptz/scan` → Auto-scan patterns (sweep/circle/figure8)
  10. `POST /api/v1/ptz/track` → Track object by bounding box

- [ ] **Configuration Requirements**
  - `PTZ_ENABLED=true` (in .env)
  - `CAMERA_IP=192.168.39.200`
  - `CAMERA_PORT=8000`
  - `CAMERA_USER=admin`
  - `CAMERA_PASS=admin` (or actual password)

- [ ] **When Camera Connects**
  - Backend logs: `📷 PTZ camera connected - Ready for tracking!`
  - Broadcasts status via WebSocket
  - Position updates every movement

---

### ✅ SECTION 3: Integration Points

**MUST KNOW HOW SYSTEMS CONNECT:**

- [ ] **Backend ↔ Navi AI**
  - Navi can detect threats (Vakten module)
  - Navi can command: `await ptz_controller.track_object(bbox)`
  - Navi can announce: `"Threat spotted: [class]"`

- [ ] **Backend ↔ Frontend**
  - Web/SDL/Android frontends get camera status via WebSocket
  - Can control camera from UI (needs UI implementation)
  - See all 9 endpoints in API docs

- [ ] **Backend ↔ Camera**
  - ONVIF protocol over network
  - Connection happens on startup if `PTZ_ENABLED=true`
  - Automatic reconnection if camera powers on later

- [ ] **Current Dependencies**
  - onvif-zeep (Python library for ONVIF)
  - FastAPI WebSocket for status broadcasting
  - Pydantic for request validation

---

## ⚠️ CRITICAL WARNINGS

### DO NOT PROCEED IF:

❌ **You don't understand the memory constraints**
- Jetson Nano has 7.4GB total
- Cannot run heavy services (like full llama2 or Redis)
- phi3:mini is the correct choice

❌ **You haven't verified network connectivity**
- Jetson must reach camera at 192.168.39.200
- Camera must be powered on and connected to network
- ONVIF service must be running on camera

❌ **You don't know the current service status**
- Backend IS running (not stopped waiting for deployment)
- PTZ module IS loaded but camera NOT connected yet (expected)
- No errors detected in initialization

❌ **You want to enable features without testing**
- Always test endpoints locally first
- Always check logs for errors
- Never deploy untested code to production

❌ **You're unclear about what "PTZ_ENABLED=true" means**
- It auto-connects to camera on backend startup
- If camera is offline, connection fails gracefully (warning logged)
- Camera can be powered on later and will auto-connect

---

## 🔍 VERIFICATION CHECKLIST

**Run these commands to verify system state BEFORE work:**

```bash
# 1. SSH to Jetson
ssh navi@192.168.39.151

# 2. Check backend is running
curl http://localhost:8000/health
# Expected: 200 OK with health status

# 3. Check PTZ module is loaded
curl http://localhost:8000/api/v1/ptz/status
# Expected: 200 OK with {"connected": false, ...}

# 4. Check memory situation
free -h
# Should show: Available: ~5.5GB

# 5. Verify configuration
cat /home/navi/AADS/backend/.env | grep PTZ
# Should show: PTZ_ENABLED=true
# Should show: CAMERA_IP=192.168.39.200

# 6. Check if camera is reachable (from Jetson)
ping -c 2 192.168.39.200
# Expected: 2 packets received (or: unreachable if powered off)
```

**All checks must PASS before proceeding.**

---

## 📋 APPROVED WORK SEQUENCE

### Phase 1: Knowledge Verification ✅
- [ ] Read entire this document
- [ ] Run all 6 verification commands above
- [ ] Confirm all checks pass
- [ ] Document any deviations

### Phase 2: Camera Connection Test
- [ ] Power on EZVIZ camera
- [ ] Wait 30 seconds for network registration
- [ ] Verify camera is reachable: `ping 192.168.39.200`
- [ ] Call: `curl -X POST http://192.168.39.151:8000/api/v1/ptz/connect`
- [ ] Expected response: `{"status": "connected", ...}`

### Phase 3: API Testing
- [ ] Test pan-left: `curl -X POST "http://192.168.39.151:8000/api/v1/ptz/pan-left?speed=0.3&duration=2"`
- [ ] Test pan-right: `curl -X POST "http://192.168.39.151:8000/api/v1/ptz/pan-right?speed=0.3&duration=2"`
- [ ] Test absolute move: `curl -X POST ... -d '{"pan_deg": 90, "tilt_deg": 30, "zoom": 0}'`
- [ ] Watch camera physically move ← **Confirm this happens**

### Phase 4: Integration Testing
- [ ] Open dashboard/frontend
- [ ] Verify camera feed visible
- [ ] Verify PTZ status broadcasts to UI
- [ ] Manual control from UI (if implemented)

### Phase 5: Navi AI Integration
- [ ] Test threat detection (show object to camera)
- [ ] Verify Navi detects it: `Threat detected: [class]`
- [ ] Verify camera auto-tracks object
- [ ] Verify announcement: `"Tracking [object]"`

### Phase 6: Production Deployment
- [ ] All 5 phases complete and logged
- [ ] No errors in backend logs
- [ ] No memory pressure (available > 3GB)
- [ ] System stable for 5+ minutes under use
- [ ] Create commit: "feat(ptz): Verified working PTZ camera control"

---

## 🚨 EMERGENCY PROCEDURES

### If Backend Crashes:

```bash
# Check what went wrong
ssh navi@192.168.39.151
tail -100 /home/navi/AADS/backend/app.log

# Restart backend
cd /home/navi/AADS/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &

# Verify it restarted
curl http://localhost:8000/health
```

### If Camera Won't Connect:

```bash
# Check if camera is reachable
ping -c 2 192.168.39.200

# If NO response:
# 1. Verify camera is powered on
# 2. Check camera network settings (IP should be 192.168.39.200)
# 3. Check network cable/WiFi connection

# Try manual connection
curl -X POST http://192.168.39.151:8000/api/v1/ptz/connect

# Check backend logs for ONVIF errors
tail -50 /home/navi/AADS/backend/app.log | grep -i "ptz\|onvif\|camera"
```

### If Memory is High:

```bash
# Check what's using memory
free -h
ps aux --sort=-%mem | head -10

# If backend is > 1GB, restart it:
pkill -f "uvicorn app.main"
cd /home/navi/AADS/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

---

## 📖 DOCUMENTATION REFERENCES

**Before work, read these:**
1. `/docs/current/PTZ_CAMERA_CONTROL.md` - Full API reference
2. `/backend/app/modules/ptz_control.py` - PTZ controller implementation
3. `/backend/app/main.py` - Backend initialization and endpoints

**For troubleshooting:**
1. Backend logs: `/home/navi/AADS/backend/app.log`
2. System memory: `free -h` on Jetson
3. Network: `ping 192.168.39.200` and `curl http://localhost:8000/docs`

---

## ✋ SIGN-OFF REQUIREMENT

**Before ANY work on PTZ/Camera features:**

Whoever is doing the work must:

1. ✅ Read this entire document (required)
2. ✅ Run all 6 verification commands (all must pass)
3. ✅ Log results with timestamp
4. ✅ Document any deviations from expected state
5. ✅ Get approval from team lead if anything is different

**DO NOT SKIP THIS CHECKLIST**

This prevents:
- Deploying broken code to production
- Wasting time on misconfigured systems
- Destroying working systems with premature changes
- Repeating the same mistakes

---

## 📝 DEPLOYMENT LOG TEMPLATE

```
DATE: 2026-02-XX
PERSON: [Name]
SYSTEM: Jetson Nano (192.168.39.151)

VERIFICATION RESULTS:
[ ] Backend health: PASS/FAIL
[ ] PTZ status: PASS/FAIL
[ ] Memory: PASS/FAIL
[ ] Config: PASS/FAIL
[ ] Camera reachable: PASS/FAIL
[ ] All 6 checks: PASS/FAIL

CAMERA CONNECTION TEST:
[ ] Camera powered on
[ ] Camera reachable
[ ] API connect call successful
[ ] Physical camera movement observed

DEVIATIONS FROM EXPECTED:
[List any differences from this document]

APPROVAL:
Team Lead: ________________
Date: ________________

NOTES:
[Any issues encountered or solutions applied]
```

---

**Last Updated:** 2026-02-01
**Version:** 1.0 - PRODUCTION READY
**Next Review:** After first successful deployment

