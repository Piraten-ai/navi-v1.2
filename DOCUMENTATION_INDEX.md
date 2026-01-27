# Documentation Index

This index points to current docs and supporting references. All current docs live in docs/current.

## Current (authoritative)

- docs/current/COMPLETE_TECHNICAL_REFERENCE.md
- docs/current/AADS_WIKI.md
- docs/current/AADS_DEPLOYMENT_READY.md
- docs/current/BRIDGE_SPEC.md
- docs/current/HARDWARE_PLAN.md
- docs/current/PROGRESS_LOG.md

## Compose files

- docker-compose.yml (Jetson backend)
- docker-compose.pi.yml (Raspberry Pi UI/bridge)
- docker-compose.dev.yml (PC dev/training)

## Guides

- docs/guides/DOCUMENTATION_INDEX.md
- docs/guides/PRODUCTION_DEPLOYMENT.md
- docs/guides/TESTING_GUIDE.md
- docs/guides/VERIFICATION_CHECKLIST.md

## Reference

- docs/reference/GUI_REDESIGN.md
- docs/reference/GITHUB_ACTIONS_DOCKER.md
- docs/reference/MAP_DATA.md

## Archived

- docs/archived
- docs/old_versions/v1.0

## Hardware manuals

- docs/hardware-manuals

## Source layout (top level)

```
backend/   FastAPI backend + AI modules
bridge/    Raspberry Pi bridge service
config/    Env files per target
docs/      Current, guides, reference, archived
frontend/  UI dashboard
scripts/   Utilities and workflows
```
