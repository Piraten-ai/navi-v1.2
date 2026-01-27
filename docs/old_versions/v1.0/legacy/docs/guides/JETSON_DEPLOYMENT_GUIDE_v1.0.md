**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# NAVI Deployment Checklist for Jetson (192.168.39.196)

**Jetson Details:**
- IP: 192.168.39.196
- OS: Ubuntu (NVIDIA Jetson)
- User: navi
- Docker: Available

---

## Pre-Deployment Checklist

### âœ… Code & Config Ready
- [x] Frontend dashboard complete (React + Tailwind)
- [x] Voice system complete (Piper TTS + Whisper STT)
- [x] Autopilot + track control + emergency behaviors integrated
- [x] All dependencies added to requirements.txt
- [x] Docker images updated with audio libs (libsndfile1, espeak-ng, alsa-utils)
- [x] docker-compose.yml configured with voice volumes
- [x] All code pushed to GitHub (main branch)

---

## Step 1: SSH to Jetson & Clone Latest

```bash
ssh navi@192.168.39.196

# Clone/pull latest repo
cd ~/navi-main  # or wherever deployed
git clone https://github.com/Piraten-ai/navi.git  # if new
git pull origin main  # if already cloned
```

---

## Step 2: Create Model & Audio Directories

```bash
mkdir -p models/piper audio
```

---

## Step 3: Download Piper Voice Model

**One-time download (on Jetson or pre-stage):**

```bash
cd models/piper

# Download Navi-inspired voice (energetic, high-pitched)
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Verify files exist
ls -lah en_US-lessac-medium*

cd ../..
```

**Model Size:** ~75 MB (ONNX is lightweight)

**Alternative Voices** (if lessac too robotic):
```bash
# en_US-amy-medium - bright, urgent female
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json
```

---

## Step 4: Download "Hey Listen!" MP3 (Optional)

**For critical alert sound prefix:**

```bash
# Fair-use Zelda "Hey Listen" sound
curl -o audio/hey_listen.mp3 "https://www.myinstants.com/media/sounds/hey_listen.mp3"

# Or manually download from https://www.myinstants.com/ and scp to Jetson
scp ~/Downloads/hey_listen.mp3 navi@192.168.39.196:~/navi-main/audio/
```

**If not available, system gracefully skips audio and logs warning.**

---

## Step 5: Verify Directory Structure

```bash
tree -L 2
# Should show:
# .
# â”œâ”€â”€ models/piper/
# â”‚   â”œâ”€â”€ en_US-lessac-medium.onnx
# â”‚   â””â”€â”€ en_US-lessac-medium.onnx.json
# â”œâ”€â”€ audio/
# â”‚   â””â”€â”€ hey_listen.mp3  (optional)
# â”œâ”€â”€ backend/
# â”œâ”€â”€ frontend/
# â”œâ”€â”€ docker-compose.yml
# â””â”€â”€ ...
```

---

## Step 6: Build Docker Images

```bash
# From repo root
docker-compose build --no-cache backend frontend

# This will:
# - Install all Python deps from requirements.txt (including piper-tts, whisper, pygame, etc.)
# - Install audio system libs (libsndfile1, espeak-ng, alsa-utils)
# - Mount ./models/piper and ./audio as read-only volumes in containers
```

**First build:** 10-15 minutes (downloading base images, pip packages)

---

## Step 7: Start Services

```bash
docker-compose up -d

# Check logs
docker-compose logs -f backend  # Should see "Voice system initialized" if VOICE_ENABLED=true
docker-compose logs -f frontend  # Should see Nginx starting on port 3000
```

**Wait for services to stabilize (~30 seconds)**

---

## Step 8: Verify Connectivity

**From Jetson terminal:**

```bash
# Test backend
curl http://localhost:8000/docs  # FastAPI Swagger UI (should return HTML)
# Or: curl http://localhost:8000/api/v1/vakten/status

# Test frontend
curl http://localhost:3000  # Should return HTML

# Test WebSocket connection
nc -zv localhost 8000  # Should show "succeeded"
```

**From dev machine (Windows):**

```powershell
# Test from browser or curl
curl http://192.168.39.196:8000/docs          # Backend API
curl http://192.168.39.196:3000               # Frontend dashboard
# WebSocket should auto-connect when visiting dashboard
```

---

## Step 9: Test Voice System

**From Frontend Dashboard:**

1. Open http://192.168.39.196:3000/autonomy
2. Click **Autonomy** module (new red button at bottom)
3. Dashboard should show:
   - Map with GPS position
   - Hardware gauges (CPU/GPU temps)
   - Autopilot status
   - Wind display
   - Alerts panel
   - **Voice Controls** (mic button at bottom)

**Test Microphone:**

1. Click **Mic button** (blue)
2. Speak: "navi status"
3. After 5s or manual stop, audio sent to backend
4. Backend transcribes via Whisper STT
5. You should hear TTS response: "All systems nominal. Ready for your command."

**If audio doesn't work:**

```bash
# Check backend logs for errors
docker-compose logs backend | grep -i "voice\|piper\|whisper"

# Verify model files mounted
docker exec aads-backend ls -la /app/models/piper/
docker exec aads-backend ls -la /app/audio/
```

---

## Step 10: Verify All Modules

**Check each module loads:**

1. Dashboard âœ“
2. Map âœ“
3. Instruments âœ“
4. Vakten (Vision) âœ“
5. Navi (AI Chat) âœ“
6. Navigator âœ“
7. Legen âœ“
8. Psykologen âœ“
9. Ingenioren âœ“
10. **Autonomy** âœ“ (new)

---

## Troubleshooting

### Voice Not Working

```bash
# Check Whisper model auto-download (happens on first STT)
docker exec aads-backend python -c "import whisper; print(whisper.available_models())"

# Check Piper voice model path
docker exec aads-backend ls -la /app/models/piper/

# Check volume mounts
docker inspect aads-backend | grep -A 20 "Mounts"
```

### Audio Device Issues

```bash
# Jetson might need ALSA config
docker exec aads-backend aplay -l  # List audio devices

# If no device, restart docker with host network (advanced):
# docker-compose.yml: network_mode: "host" (not recommended for security)
```

### Models Not Found

```bash
# Re-check directory permissions
chmod -R 755 models/ audio/

# Rebuild and restart
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

---

## Post-Deployment

### Monitor Logs

```bash
# Real-time backend logs
docker-compose logs -f backend

# Real-time frontend logs
docker-compose logs -f frontend

# Save logs for analysis
docker-compose logs > deployment_$(date +%Y%m%d_%H%M%S).log
```

### Auto-Restart on Reboot

```bash
# Enable auto-restart (already in docker-compose with restart: unless-stopped)
systemctl enable docker  # Ensure Docker starts on boot

# Or use cron
crontab -e
# Add: @reboot cd ~/navi-main && docker-compose up -d
```

### Performance Monitoring

```bash
# Check CPU/GPU usage during voice inference
docker stats

# Jetson-specific (if jtop available)
jtop

# Expected during STT (Whisper):
# - GPU: ~500 MB (if using GPU)
# - CPU: ~30-40% for tiny.en model
# - Latency: 2-5 seconds for 5s audio clip
```

---

## Success Indicators

âœ… **All systems ready when:**

- [ ] Docker-compose services running (`docker ps` shows aads-backend, aads-frontend, postgres, influxdb, redis, navi)
- [ ] Frontend accessible at http://192.168.39.196:3000
- [ ] Autonomy dashboard module loads with map, gauges, voice controls
- [ ] Mic button can record 5-second voice command
- [ ] TTS response plays back (if audio hardware available)
- [ ] WebSocket connection shows green "Connected" badge
- [ ] Backend logs show "Voice system initialized" (if VOICE_ENABLED=true)

---

## Deployment Complete! ðŸš€

**NAVI is now live on Jetson 192.168.39.196**

**Arctic Autonomy Dashboard URL:** http://192.168.39.196:3000/autonomy

**API Documentation:** http://192.168.39.196:8000/docs

**Next Steps:**
- Configure GPS/Signal K inputs (if available)
- Tune autopilot PID gains for your vessel
- Test emergency behaviors (collision avoidance, steering loss)
- Validate voice commands in marine environment
- Monitor telemetry in InfluxDB

**"When satellites fail, we survive."** âš“

---

*Last Updated: January 23, 2026*  
*Deployment Target: Jetson Orin Nano / Orin NX (Ubuntu 22.04 LTS)*  
*Docker Version: 20.10+ (check with `docker --version`)*

