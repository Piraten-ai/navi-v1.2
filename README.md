# AADS NAVI - Arctic Autonomy Decision Support System

AADS NAVI is an offline-first maritime decision support system built for Arctic operations.

Current hardware split:
- Jetson: backend, AI inference, sensor ingestion, storage
- Raspberry Pi: dashboard UI + Arduino analog bridge
- PC: development and training (full stack)

This repo is organized for clarity: current docs live in docs/current, older versions in docs/old_versions.
Environment configs live in config/.

## Start here

- docs/current/COMPLETE_TECHNICAL_REFERENCE.md
- docs/current/AADS_WIKI.md
- docs/current/AADS_DEPLOYMENT_READY.md

## Quick run targets

Jetson (production backend):
- Use `docker-compose.yml`
- Connect sensors and verify health endpoint

Raspberry Pi (UI + bridge):
- Use `docker-compose.pi.yml`
- Point UI to Jetson REST/WS endpoints
- Bridge service is behind a compose profile: `bridge`
  - Example: `docker compose --profile bridge -f docker-compose.pi.yml up -d`

PC (dev/training):
- Use `docker-compose.dev.yml`
- Use laptop only as a client
- For simulation: run `scripts/sim/run-pc-sim.ps1` or `scripts/sim/run-pc-sim.sh`

## Support docs

- docs/guides (setup, testing, deployment)
- docs/reference (deep technical topics)
- docs/archived (historical snapshots)

