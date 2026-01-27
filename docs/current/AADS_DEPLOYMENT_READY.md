# AADS Deployment Ready (Current)

Version: 1.1 (draft)
Last updated: 2026-01-25

This checklist reflects the split deployment:

- Jetson: backend + AI + sensors
- Raspberry Pi: UI + Arduino bridge
- PC: dev/training environment

---

## Jetson Deployment Checklist

- [ ] Use docker-compose.yml
- [ ] Backend stack builds and starts
- [ ] AI models present (YOLO, Ollama)
- [ ] Sensor devices visible (camera, NMEA, Signal K)
- [ ] REST health endpoint returns OK
- [ ] WebSocket stream is active
- [ ] Storage services reachable (Postgres, InfluxDB, Redis, MinIO)
- [ ] Bridge endpoint accepts payloads (POST /api/v1/bridge/analog)

## Raspberry Pi Deployment Checklist

- [ ] Use docker-compose.pi.yml
- [ ] UI starts on boot and connects to Jetson
- [ ] WebSocket updates visible in UI
- [ ] Arduino bridge running (compose profile: bridge)
- [ ] Analog signals converted and sent to Jetson
    - Example: docker compose --profile bridge -f docker-compose.pi.yml up -d
- [ ] Bridge panel visible in UI when signals arrive

## PC Dev/Training Checklist

- [ ] Use docker-compose.dev.yml
- [ ] For simulation, run scripts/sim/run-pc-sim.ps1 or scripts/sim/run-pc-sim.sh
- [ ] Simulation uses config/backend.env.sim (SIGNALK_MOCK_DATA=false)
- [ ] Full stack runs locally
- [ ] Training scripts run without lightweight mode
- [ ] Laptop can connect to UI on the PC

---

This document replaces the v1.0 deployment note stored in:

- docs/old_versions/v1.0/AADS_DEPLOYMENT_READY_v1.0.md

