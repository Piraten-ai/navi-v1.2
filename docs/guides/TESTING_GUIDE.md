# Testing Guide - Current Stack (Jetson + Pi + PC)

## Quick Start Testing

### Prerequisites
- Docker + Docker Compose installed
- Backend and frontend code pulled

---

## Test 1: Stack Health (PC Dev)

### Start Full Stack
```bash
docker compose -f docker-compose.dev.yml up -d
```

### Start Full Simulation (recommended)
```bash
scripts/sim/run-pc-sim.ps1
# or
scripts/sim/run-pc-sim.sh
```

### Open Browser
```
http://localhost:3000
```

### Test Steps
1. Open **DASHBOARD** module
2. **Verify:**
   - Connection status: "Connected" (green)
   - Position displays and updates
   - Gauges update every 1-2 seconds

### Quick Health Check
```bash
curl http://localhost:8001/health
```

---

## Test 2: Bridge Payload (PC Dev)

### Send a test payload
```bash
curl -X POST http://localhost:8001/api/v1/bridge/analog \
  -H "Content-Type: application/json" \
  -d "{\"timestamp\":\"2026-01-25T12:00:00Z\",\"signals\":{\"rpm\":1200,\"temp_c\":62.1}}"
```

### Verify
- Dashboard shows the Analog Bridge panel
- GET /api/v1/bridge/analog returns latest payload

## Test 2b: Serial Simulation (Pi)

```bash
cd bridge
./simulate_serial.sh
```

Then run:

```bash
SERIAL_DEVICE=/tmp/ttyV0 docker compose --profile bridge -f docker-compose.pi.yml up -d
```

---

## Test 3: AI Chat (Navi)

### Ollama (Local)
```bash
ollama pull mistral
# In config/backend.env.dev or config/backend.env.sim
OLLAMA_BASE_URL=http://navi:11434
OLLAMA_MODEL=mistral
```

### Test Steps
1. Open **NAVI** module
2. Send a message
3. Verify response appears

---

## Test 4: Module Icons & Navigation

1. Verify bottom navigation icons render
2. Click each module and confirm content loads

---

## Test 5: Settings & Configuration

1. Open Settings
2. Toggle Battle Mode (B key)
3. Verify theme changes

---

## Test 6: Local Signal K Server (Simulation)

### Configure backend
```bash
# In config/backend.env.sim
SIGNALK_SERVER_URL=ws://signalk:3000/signalk/v1/stream
SIGNALK_MOCK_DATA=false
```

### Verify
- Dashboard shows real vessel data

---

## Troubleshooting Common Issues

- Backend not running: `docker compose ps`
- WebSocket down: check `VITE_WS_URL`
- Bridge not showing: check POST /api/v1/bridge/analog

