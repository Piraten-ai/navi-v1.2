# START HERE

This guide points you to the current, authoritative docs and the correct run targets.

## Current system split

- Jetson: backend + AI + sensors + storage
- Raspberry Pi: UI + Arduino analog bridge
- PC: development + training

## First read

1) docs/current/COMPLETE_TECHNICAL_REFERENCE.md
2) docs/current/AADS_WIKI.md
3) docs/current/AADS_DEPLOYMENT_READY.md

## If you are deploying

- Jetson: `docker-compose.yml` and verify /health
- Raspberry Pi: `docker-compose.pi.yml` for UI and bridge
- PC: `docker-compose.dev.yml` for dev/training
  - Simulation: `scripts/sim/run-pc-sim.ps1` or `scripts/sim/run-pc-sim.sh`

## Source layout (top level)

```
backend/   FastAPI backend + AI modules
bridge/    Raspberry Pi bridge service
config/    Env files per target
docs/      Current, guides, reference, archived
frontend/  UI dashboard
scripts/   Utilities and workflows
```

## Notes

- Lightweight dev mode is no longer used
- Keep all new docs in docs/current
- Old versions are archived in docs/old_versions/v1.0

## House rules

- Keep the root clean: avoid new top-level files unless necessary
- Put new documentation in docs/current and update docs/current/PROGRESS_LOG.md
- Use the correct compose file for the target device (Jetson, Pi, or dev)
- Keep scripts in scripts/ and archive old ones in scripts/old_versions
- Prefer small, reversible changes over large refactors

