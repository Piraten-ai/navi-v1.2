# AADS System Verification Checklist

Use this checklist to verify the AADS system is ready for testing or deployment.

## Repository Structure

- [ ] README.md (project overview)
- [ ] START_HERE.md (quick start)
- [ ] DOCUMENTATION_INDEX.md (root index)
- [ ] docs/current/COMPLETE_TECHNICAL_REFERENCE.md
- [ ] docs/current/HARDWARE_PLAN.md
- [ ] docs/current/BRIDGE_SPEC.md
- [ ] docs/current/AADS_DEPLOYMENT_READY.md
- [ ] docs/current/PROGRESS_LOG.md
- [ ] docs/guides/TESTING_GUIDE.md
- [ ] docs/guides/VERIFICATION_CHECKLIST.md
- [ ] docker-compose.yml (Jetson backend)
- [ ] docker-compose.pi.yml (Raspberry Pi UI/bridge)
- [ ] docker-compose.dev.yml (PC dev/training)
- [ ] config/backend.env.jetson
- [ ] config/backend.env.dev
- [ ] config/backend.env.sim

## Backend Files

- [ ] backend/requirements.txt
- [ ] backend/Dockerfile
- [ ] backend/Dockerfile.dev
- [ ] backend/app/main.py
- [ ] backend/app/core/config.py
- [ ] backend/app/modules/

## Frontend Files

- [ ] frontend/package.json
- [ ] frontend/Dockerfile
- [ ] frontend/Dockerfile.dev
- [ ] frontend/src/App.tsx
- [ ] frontend/src/components/
- [ ] frontend/src/hooks/

## Bridge Files

- [ ] bridge/main.py
- [ ] bridge/requirements.txt
- [ ] bridge/README.md

## Simulation (PC)

- [ ] scripts/sim/run-pc-sim.ps1
- [ ] scripts/sim/run-pc-sim.sh
- [ ] scripts/sim/simulators/run_simulators.py

## Manual Verification

### PC Dev/Simulation
```bash
docker compose -f docker-compose.dev.yml up -d
# or
scripts/sim/run-pc-sim.ps1
```

### Jetson
```bash
docker compose -f docker-compose.yml up -d
curl http://localhost:8000/health
```

### Raspberry Pi
```bash
docker compose -f docker-compose.pi.yml up -d
```

## Functional Tests

- [ ] Backend health endpoint responds (dev: http://localhost:8001/health)
- [ ] WebSocket connection establishes
- [ ] Bridge POST /api/v1/bridge/analog accepted
- [ ] Dashboard shows bridge signals
- [ ] Signal K data updates in UI

## Notes

- Use docs/current as the source of truth.
- Keep scripts in scripts/ and archive old versions in scripts/old_versions.

