# AADS Native Frontend (Qt/QML)

This is a native Qt/QML frontend for the Raspberry Pi touch UI. The existing web
frontend remains in `frontend/`.

## Runtime configuration

Set these environment variables to point the UI at the backend:

- `AADS_API_URL` (default: `http://localhost:8001`)
- `AADS_WS_URL` (default: `ws://localhost:8001/ws`)
- `AADS_SIGNALK_URL` (default: `http://localhost:3001`)
- `AADS_TILES_URL` (default: `http://localhost:8080/styles/raster/`)
- `AADS_WIKI_PATH` (default: `/opt/aads/docs/current/AADS_WIKI.md`)

On the Pi you will typically use the Jetson host, e.g.:

```
export AADS_API_URL=http://<jetson-ip>:8000
export AADS_WS_URL=ws://<jetson-ip>:8000/ws
export AADS_SIGNALK_URL=http://<jetson-ip>:3001
export AADS_TILES_URL=http://localhost:8080/styles/raster/
export AADS_WIKI_PATH=/opt/aads/docs/current/AADS_WIKI.md
```

## Windows build (Qt 6)

1) Install Qt 6 (Desktop) and CMake.
2) Open a developer terminal:

```
cd frontend-qt
cmake -S . -B build
cmake --build build --config Release
```

Run:

```
build\Release\aads_ui.exe
```

Or use:

```
scripts\build-win.ps1
scripts\run-win.ps1
```

## Raspberry Pi build (64-bit)

Install Qt 6 and build tools:

```
sudo apt update
sudo apt install -y qt6-base-dev qt6-declarative-dev qt6-websockets-dev qt6-location-dev qt6-positioning-dev cmake build-essential
```

Build:

```
cd frontend-qt
cmake -S . -B build
cmake --build build -j
./build/aads_ui
```

Or use:

```
./scripts/build-pi.sh
./build/aads_ui
```

## Pi auto-start (systemd)

```
sudo mkdir -p /opt/aads
sudo rsync -a --delete ./frontend-qt/ /opt/aads/frontend-qt/
sudo cp /opt/aads/frontend-qt/aads-ui.env.example /opt/aads/frontend-qt/aads-ui.env
sudo nano /opt/aads/frontend-qt/aads-ui.env
sudo cp /opt/aads/frontend-qt/systemd/aads-ui.service /etc/systemd/system/aads-ui.service
sudo systemctl daemon-reload
sudo systemctl enable --now aads-ui.service
```

## Kiosk unlock (GPIO)

This adds a long-press GPIO unlock to stop/start the UI service.

1) Install gpiozero:

```
sudo apt install -y python3-gpiozero
```

2) Install the env file and service:

```
sudo cp /opt/aads/frontend-qt/systemd/aads-kiosk-unlock.env.example /etc/aads-kiosk-unlock.env
sudo nano /etc/aads-kiosk-unlock.env
sudo cp /opt/aads/frontend-qt/systemd/aads-kiosk-unlock.service /etc/systemd/system/aads-kiosk-unlock.service
sudo systemctl daemon-reload
sudo systemctl enable --now aads-kiosk-unlock.service
```

Default wiring uses GPIO17 (pin 11) pulled up; connect the button to GND.

## Notes

- The UI polls `/health` every 2 seconds and keeps a WebSocket open to `/ws`.
- The left rail is touch-first navigation for Dashboard, Bridge, Navi, Settings.
- The map uses the QtLocation OSM plugin with a local MBTiles tile server (offline).
- Set the tile URL in Settings to your local server (default: `http://localhost:8080/styles/raster/`).
- Track length and widget visibility can be customized in the Settings view and saved per vessel profile.
- For KAP charts, convert them to MBTiles and serve them locally (see `frontend-qt/tileserver/README.md`).
- Copy the docs to the Pi (e.g., `/opt/aads/docs/current/`) for the offline Wiki view.
