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

Date: 2026-01-27

## Completed

- Added QML singleton registration via `qml/qmldir` and aligned imports to the QML root.
- Moved profile persistence logic into `qml/utils/ProfileHandler.js` and simplified Main.qml startup profile flow.
- Reworked SettingsView to use ProfileHandler directly with grouped rows and embedded helper components.
- Updated SignalLogic utilities and trimmed gauge catalog to the focused dashboard set.
- Rebuilt GaugePanel to use CircularGauge + Logic.resolve with direct aadsClient input.
- Updated Theme palette to Arctic HUD colors with battleMode and compatibility aliases.
- Switched CircularGauge to arc-based HUD style and refreshed GaugePanel layout styling.
- Adjusted Main background gradient to the new dark cyan-to-black backdrop.
- Added red night-vision mode palette and toggle, plus an N-key shortcut for red mode.
- Added HUD glow effect on gauge arcs and dynamic header text/animation for night mode.
- Added HistoryGraph sparkline component and rebuilt NaviView as a tactical chat log.
- Wired HistoryGraph to live engine temp/RPM data and connected Navi chat to aadsClient history + send.
- Rebuilt MapPanel for fully offline tiles with red-mode shader filter and HUD coordinates overlay.
- Mounted FastAPI tileserver for offline maps and ensured tiles directory exists.
- Added FlightRecorder for in-memory telemetry history plus `/api/v1/history/{sensor_key}` endpoint.
- Logged key Signal K metrics (speed, depth, RPM, engine temp) into the flight recorder.
- Injected Signal K telemetry into Navi's tactical system prompt for concise, data-grounded replies.
- Added thermal zone fallback for Ingenioren CPU temperature readings.
- Mapped `./map/tiles` into the dev backend container for offline tile serving.
- Updated Qt CMake QML module list to include new QML/JS files and set QML policies.
- Removed stale `navMap` reference from Main.qml to prevent runtime errors.
- Dropped QtGraphicalEffects usage (Glow/imports) to fix missing module crash on Qt 6 builds.
- Added defensive QML defaults/guards to prevent undefined uiSettings/gaugeGrid runtime warnings.
- Replaced MapPanel ShaderEffect with a red overlay to avoid Qt6 .qsb shader errors.
- Removed invalid StackView transition assignments causing QML warnings.
- Guarded SettingsView/ProfileHandler profile actions when uiSettings is not ready.
- Expanded SignalLogic gauge catalog with categories/units and added gauge selection UI in Settings.
- Restored dashboard header cards (logo, compass/wind, autopilot, NAVTEX) and map visibility toggle.
- Tuned Theme palette for more cohesive Arctic HUD contrast.
- Adjusted gauge grid persistence to avoid profile defaults overwriting saved settings.
- Added gauge grid change listener so UI updates immediately when Settings writes gauge JSON.
- Rebuilt DashboardView layout to match the reference HUD (left column, dual camera row, map overlays, bottom chat, right gauges).
- Added expanded gauge catalog + categorized display names and grid editor in Settings.
- Added Qt Multimedia camera wiring in DashboardView with J1455 device selection fallback and dual VideoOutput feeds.
- Reworked DashboardView layout to match the reference HUD (camera/log top row, map overlays, chat dock, right gauges).
- Added optional HistoryGraph visibility toggle via GaugePanel showHistory flag (default off).
- Dropped Qt6MultimediaQuick CMake dependency to match installed Qt modules while keeping QML QtMultimedia runtime.
- Fixed main.cpp logo path initialization order (appDir before env defaults).

## Notes

- Bridge endpoint is live; persistence uses InfluxDB when token is configured.
- Pi controls D7/D8 for maintenance shutdowns.
