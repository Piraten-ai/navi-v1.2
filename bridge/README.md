# Raspberry Pi Bridge Service (Current)

Primary references:
- docs/current/COMPLETE_TECHNICAL_REFERENCE.md
- docs/current/HARDWARE_PLAN.md
- docs/current/BRIDGE_SPEC.md

Purpose: read Arduino serial data and Sense HAT telemetry and forward it to Jetson.

Expected input:
- One JSON object per line from the Arduino, for example:
  {"timestamp":"2026-01-25T12:00:00Z","signals":{"rpm":1200,"temp_c":62.1}}

Expected output:
- HTTP POST to the configured Jetson endpoint.

Configuration (environment variables):
- JETSON_HOST (default: 192.168.39.196)
- JETSON_PORT (default: 8000)
- SERIAL_DEVICE (default: /dev/ttyACM0)
- SERIAL_BAUD (default: 115200)
- SERIAL_ENABLED (default: true)
- SERIAL_REQUIRED (default: true)
- SERIAL_DEVICE_2 (optional: second serial source)
- SERIAL_BAUD_2 (default: 115200)
- BRIDGE_ENDPOINT (default: /api/v1/bridge/analog)
- SENSE_HAT_ENABLED (default: auto)
- SENSE_HAT_INTERVAL (default: 2.0)

Sense HAT signals are posted with source `sense_hat` and the `sense_*` signal keys.
If you enable `SERIAL_DEVICE_2` in Docker, also add the matching `/dev/tty*` device mapping.

## Serial simulation (for Pi)

Use this to simulate Arduino serial data with a virtual port:

```bash
./simulate_serial.sh
```

Then start the bridge with:

```bash
SERIAL_DEVICE=/tmp/ttyV0 docker compose --profile bridge -f docker-compose.pi.yml up -d
```
