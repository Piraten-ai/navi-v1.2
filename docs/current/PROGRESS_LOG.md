# Progress Log

Date: 2026-01-25

## Completed

- Cleaned root structure and archived duplicate docs/scripts into versioned folders.
- Created current docs in `docs/current` aligned to Jetson + Pi + PC split.
- Added `docker-compose.pi.yml` for Pi UI and bridge profile.
- Added a Qt/QML native frontend scaffold in `frontend-qt/` for the Pi touch UI.
- Added systemd auto-start unit, env template, and build scripts for the Qt/QML UI.
- Wired the Qt/QML UI to `/health`, `/api/v1/status`, and bridge endpoints for live panels.
- Added dashboard panels for map slot, compass, wind, vitals, and module statuses in Qt/QML.
- Added SignalK-backed map with course trail, gauge visibility settings, and night mode.
- Added vessel profile settings, map source controls, and Navi chat UI in the Qt/QML frontend.
- Locked the UI map to offline MBTiles tile sources and updated settings for local tiles.
- Added KAP-to-MBTiles conversion guidance and script for offline charts.
- Added offline tileserver compose + systemd unit and wired tile URL env support.
- Added GPIO kiosk unlock service and env template for stopping/starting the UI.
- Added NAVTEX history/summary endpoints and NAVTEX summary/full report handling in Navi.
- Added a "solo-arctic" vessel profile preset for the native UI.
- Added NAVTEX dashboard widget and offline wiki viewer in the native UI.
- Added bridge service skeleton (`bridge/`) and bridge spec.
- Implemented `/api/v1/bridge/analog` endpoint with WebSocket broadcast and in-memory latest state.
- Added InfluxDB logging for bridge signals.
- Added bridge signal panel to the dashboard.
- Normalized env configs into `config/` and updated compose files.
- Removed hardcoded IP defaults from frontend and backend defaults.
- Added `docs/current/HARDWARE_PLAN.md` with roles, wiring, and sensor map.
- Moved hardware manuals into `docs/hardware-manuals`.
- Added legacy headers to non-current markdown docs and updated testing guide for bridge simulation.
- Archived legacy markdown docs into docs/old_versions/v1.0/legacy and kept only current entry docs + guides.
- Added PC simulation workflow (Signal K + bridge simulator) with run scripts.
- Added config/backend.env.sim for non-mock Signal K simulation.
- Updated docs to reflect new PC simulation and compose usage.
- Fixed Navi AI assistant communication issues between frontend and backend.
- Implemented robust personality loading for Navi with multiple fallback paths.
- Added graceful mock mode for Navi when Ollama service is unavailable.
- Aligned Navi API endpoints with frontend expectations and ensured consistent JSON schema.
- Synchronized frontend `useNavi` hook and `Navi.tsx` with updated backend API.
- Fixed missing initialization of Navi and Vakten modules in the backend lifecycle.
- Added comprehensive logging to Navi chat endpoints to facilitate debugging.
- Ensured `httpx.AsyncClient` is re-initialized if closed during long-running sessions.
- Identified and documented the requirement for Docker container restarts after code changes.
- Added Sense HAT telemetry ingestion in the Pi bridge with optional enable/disable flags.
- Added optional second serial source support for a second serial device.
- Updated bridge docs and hardware plan with Sense HAT + GPIO extension cable notes.
- Updated Pi compose to pass Sense HAT/serial configuration and map I2C device.
- Added cardinal-direction heading text for the Qt/QML dashboard gauges.
- Added a compass overlay widget to the Qt/QML map panel, tied to the Show Compass toggle.
- Fixed Qt/QML Label letterSpacing usage and added startup logging to diagnose UI load issues on Windows.
- Reworked the Qt/QML gauge panel into a configurable grid with per-cell gauge selection and saved layout.
- Set the default gauge grid to 3x3 and added camera/log overlay placeholders on the map panel to match the intended layout.
- Applied the neon Arctic UI styling pass with compass badge, camera/autopilot/log overlays, and updated gauge panel visuals.
- Replaced the top map overlay row with logo + camera feed + autopilot panels and added AADS_LOGO_PATH support.
- Moved the logo/camera/autopilot row above the map so it no longer overlays the map view.
- Moved Vakten alerts into the gauge panel header and added a map/camera toggle with inset swapping.
- Broke the Qt/QML dashboard into reusable modules (TopBar, MapPanel, GaugePanel).
- Extracted the remaining QML views (Dashboard/Bridge/Navi/Wiki/Settings) into standalone components.

## Notes

- Bridge endpoint is live; persistence uses InfluxDB when token is configured.
- Pi controls D7/D8 for maintenance shutdowns.
