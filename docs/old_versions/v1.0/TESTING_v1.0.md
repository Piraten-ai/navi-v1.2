# AADS Testing Guide

Comprehensive testing guide for the AADS (Arctic Autonomy Decision Support) system.

---

## 🧪 Quick Test

```bash
# Start system
docker-compose up -d

# Wait for services to start
sleep 10

# Run quick health check
curl http://localhost:8000/health
curl http://localhost:3000

# Check all modules
curl http://localhost:8000/api/v1/status
```

✅ **Expected:** All services return 200 OK

---

## 📋 Pre-Flight Checks

### 1. Docker Services

```bash
docker-compose ps
```

**Expected output:** All services "Up"
```
NAME                STATUS
aads-backend        Up
aads-frontend       Up
aads-postgres       Up
aads-influxdb       Up
aads-redis          Up
aads-minio          Up
aads-navi-ollama    Up
```

### 2. Network Connectivity

```bash
# Check internal networking
docker network ls | grep aads

# Test inter-service communication
docker exec aads-backend curl http://redis:6379
docker exec aads-backend curl http://navi:11434/api/tags
```

### 3. Database Connectivity

```bash
# PostgreSQL
docker exec aads-postgres psql -U aads -c "SELECT version();"

# Redis
docker exec aads-redis redis-cli PING

# InfluxDB
curl http://localhost:8086/health
```

---

## 🔌 API Endpoint Tests

### Core Endpoints

**Health Check:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**System Status:**
```bash
curl http://localhost:8000/api/v1/status
# Expected: Full system status with all modules
```

**API Documentation:**
```bash
curl http://localhost:8000/docs
# Expected: OpenAPI/Swagger docs (HTML)
```

### Module Endpoints

**Vakten (Vision):**
```bash
# Get status
curl http://localhost:8000/api/v1/vakten/status

# Get detections
curl http://localhost:8000/api/v1/vakten/detections

# Start detection (POST)
curl -X POST http://localhost:8000/api/v1/vakten/start
```

**Navi (AI Assistant):**
```bash
# Get status
curl http://localhost:8000/api/v1/navi/status

# Chat (POST)
curl -X POST "http://localhost:8000/api/v1/navi/chat?message=What%20is%20the%20system%20status"

# Get history
curl http://localhost:8000/api/v1/navi/history
```

**Navigator (NAVTEX):**
```bash
# Get status
curl http://localhost:8000/api/v1/navigator/status

# Parse NAVTEX (POST)
curl -X POST "http://localhost:8000/api/v1/navigator/parse_navtex" \
  -H "Content-Type: application/json" \
  -d '{"message": "ZCZC EA01\nICE WARNING 73-45N 025-30E\nNNNN"}'

# Get hazards
curl http://localhost:8000/api/v1/navigator/hazards
```

**Legen (Medical):**
```bash
# Get status
curl http://localhost:8000/api/v1/legen/status

# Medical assessment (POST)
curl -X POST "http://localhost:8000/api/v1/legen/assess" \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["hypothermia", "cold"], "severity": "medium"}'

# Get protocol
curl http://localhost:8000/api/v1/legen/protocol/hypothermia
```

**Psykologen (Mental Health):**
```bash
# Get status
curl http://localhost:8000/api/v1/psykologen/status

# Check-in (POST)
curl -X POST "http://localhost:8000/api/v1/psykologen/checkin?mood_score=7"
```

**Ingeniøren (Engineering):**
```bash
# Get status
curl http://localhost:8000/api/v1/ingenioren/status

# Get diagnostics
curl http://localhost:8000/api/v1/ingenioren/diagnostics

# Get metrics
curl http://localhost:8000/api/v1/ingenioren/metrics

# Optimize (POST)
curl -X POST http://localhost:8000/api/v1/ingenioren/optimize
```

---

## 🌐 WebSocket Tests

### Using wscat

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:8000/ws

# Send subscription message
{"type": "subscribe", "topics": ["vakten", "navi"]}

# Wait for messages (should see heartbeats)
```

### Using Python

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Subscribe
        await websocket.send(json.dumps({
            "type": "subscribe",
            "topics": ["vakten", "navi"]
        }))
        
        # Receive messages
        for i in range(5):
            message = await websocket.recv()
            print(f"Received: {message}")

asyncio.run(test_websocket())
```

---

## 🎨 Frontend Tests

### Manual UI Testing

1. **Open dashboard:** http://localhost:3000
2. **Check Arctic theme:** Toxic green, arctic blue colors visible
3. **Battle mode:** Press 'B' key - should turn red
4. **Navigation:** Click all 8 module buttons
5. **Status indicators:** Check online/offline, threat level
6. **Real-time updates:** Watch for WebSocket data

### Component Checklist

- [ ] Map component loads
- [ ] Instruments show gauges
- [ ] Vakten displays detections
- [ ] Navi chat interface works
- [ ] Navigator shows NAVTEX messages
- [ ] Legen medical interface loads
- [ ] Psykologen wellness interface loads
- [ ] Ingeniøren diagnostics display

---

## 🤖 AI Module Tests

### Vakten (Vision)

**Mock Mode Test:**
```bash
# Start detection
curl -X POST http://localhost:8000/api/v1/vakten/start

# Wait a few seconds
sleep 5

# Get detections
curl http://localhost:8000/api/v1/vakten/detections
```

**Expected:** Mock detections generated

**Real Camera Test:**
```bash
# Ensure camera is connected
ls /dev/video*

# Set MOCK_CAMERA=false in .env
# Restart backend
docker-compose restart backend

# Start detection
curl -X POST http://localhost:8000/api/v1/vakten/start
```

### Navi (AI Assistant)

**Mock Mode Test:**
```bash
curl -X POST "http://localhost:8000/api/v1/navi/chat?message=What%20is%20the%20status"
```

**Expected:** Simple keyword-based response

**Ollama Test:**
```bash
# Check Ollama is running
docker exec aads-navi-ollama ollama list

# Chat with Navi
curl -X POST "http://localhost:8000/api/v1/navi/chat?message=Explain%20Arctic%20navigation"
```

**Expected:** Intelligent AI-generated response

### Navigator (NAVTEX)

**Sample NAVTEX Test:**
```bash
curl -X POST "http://localhost:8000/api/v1/navigator/parse_navtex" \
  -H "Content-Type: application/json" \
  -d '{"message": "ZCZC EA01\nNAVAREA I 001/26\nNORWEGIAN SEA\nICE WARNING\nICEBERG REPORTED 73-45N 025-30E\nDRIFTING SOUTHEAST 0.5 KNOTS\nALL SHIPS NAVIGATE WITH CAUTION\nNNNN"}'
```

**Expected:** Parsed message with coordinates extracted

---

## 📊 Performance Tests

### Latency Benchmarks

**API Response Time:**
```bash
time curl http://localhost:8000/health
# Target: < 50ms
```

**WebSocket Latency:**
```bash
# Use wscat and measure round-trip time
# Target: < 10ms
```

### Throughput Tests

**API Requests per Second:**
```bash
# Install apache bench
sudo apt install apache2-utils

# Test endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Target: > 1000 req/s
```

### Resource Usage

**Memory:**
```bash
docker stats --no-stream
# Scout: < 6GB total
# Pro: < 12GB total
```

**CPU:**
```bash
docker stats --no-stream
# Scout: < 70% average
# Pro: < 50% average
```

**GPU (if applicable):**
```bash
nvidia-smi
# Check GPU utilization
```

---

## 🔒 Security Tests

### Authentication

```bash
# Test JWT token generation (if implemented)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'
```

### Input Validation

```bash
# Test SQL injection prevention
curl -X POST "http://localhost:8000/api/v1/navi/chat?message='; DROP TABLE users; --"

# Expected: Sanitized, no SQL execution
```

### Privacy (Psykologen)

```bash
# Verify mental health data is local-only
curl http://localhost:8000/api/v1/psykologen/status

# Check that sensitive data is NOT in response
# Should only see aggregated statistics
```

---

## 🌐 Offline Capability Tests

### 1. Disconnect Network

```bash
# Disconnect WiFi/Ethernet
sudo nmcli radio wifi off

# Or using ifconfig
sudo ifconfig eth0 down
```

### 2. Test Core Functionality

All core endpoints should still work:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/status
curl http://localhost:8000/api/v1/vakten/status
```

### 3. Test Data Buffering

- Create alerts/logs while offline
- Reconnect network
- Verify data is synced (if cloud sync enabled)

---

## 🐛 Error Scenarios

### Service Failure

**Test graceful degradation:**
```bash
# Stop Redis
docker-compose stop redis

# Backend should still respond (degraded mode)
curl http://localhost:8000/health
```

### Database Connection Loss

```bash
# Stop PostgreSQL
docker-compose stop postgres

# System should handle gracefully
curl http://localhost:8000/health
```

### Camera Failure

```bash
# Unplug camera or set invalid device
# Vakten should fall back to mock mode
curl http://localhost:8000/api/v1/vakten/status
```

---

## 📝 Test Checklist

### Pre-Deployment

- [ ] All Docker services start
- [ ] Health endpoints respond
- [ ] Database connections work
- [ ] WebSocket connections stable
- [ ] Frontend loads without errors
- [ ] All 6 AI modules respond
- [ ] API documentation accessible

### Functional Testing

- [ ] Vakten detects objects (mock or real)
- [ ] Navi responds to questions
- [ ] Navigator parses NAVTEX correctly
- [ ] Legen provides medical guidance
- [ ] Psykologen wellness check works
- [ ] Ingeniøren diagnostics accurate

### Performance Testing

- [ ] API latency < 50ms (p95)
- [ ] WebSocket latency < 10ms
- [ ] Throughput > 1000 req/s
- [ ] Memory usage within limits
- [ ] CPU usage within limits

### Security Testing

- [ ] Input validation works
- [ ] No SQL injection vulnerabilities
- [ ] Privacy guarantees enforced (Psykologen)
- [ ] Sensitive data not logged

### Offline Testing

- [ ] System works without internet
- [ ] Data buffering functions
- [ ] Local storage persists
- [ ] Reconnection syncs data

### User Experience

- [ ] UI loads quickly (< 2s)
- [ ] Arctic theme displays correctly
- [ ] Battle mode toggle works
- [ ] Navigation intuitive
- [ ] Real-time updates smooth

---

## 🎯 Success Criteria

✅ **Minimum Viable Product:**
1. System boots successfully
2. All services healthy
3. Backend API responds
4. Frontend dashboard loads
5. Vakten processes video feed
6. Navi responds intelligently
7. System survives 24+ hours offline
8. No critical security vulnerabilities

✅ **Production Ready:**
1. All MVP criteria met
2. Performance targets achieved
3. Security tests passed
4. Stress tested (1000+ requests)
5. Error handling validated
6. Documentation complete
7. Deployment scripts tested

---

## 🆘 Troubleshooting Tests

If tests fail, check:
1. **Logs:** `docker-compose logs -f`
2. **Status:** `docker-compose ps`
3. **Resources:** `docker stats`
4. **Network:** `docker network inspect aads-network`
5. **Config:** Check `.env` file

---

🧊 **"Test in safety, deploy with confidence."** ⚓
