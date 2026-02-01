# PTZ Camera Control System

## Overview

The AADS system now includes full Pan/Tilt/Zoom (PTZ) control for ONVIF-compatible IP cameras (tested with EZVIZ H6c).

This enables:
- Real-time camera positioning via API
- Object tracking and auto-centering on detected targets
- Automated scanning patterns
- Integration with Navi AI for autonomous camera control

## Configuration

Enable PTZ in your `.env`:

```bash
# IP Camera (ONVIF)
CAMERA_IP=192.168.39.200
CAMERA_PORT=8000
CAMERA_USER=admin
CAMERA_PASS=admin
PTZ_ENABLED=true
```

## API Reference

### Connection Management

**Connect to camera:**
```bash
POST /api/v1/ptz/connect
```
Response: `{"status": "connected", "camera_ip": "192.168.39.200"}`

**Disconnect:**
```bash
POST /api/v1/ptz/disconnect
```

**Get status:**
```bash
GET /api/v1/ptz/status
```
Response:
```json
{
  "connected": true,
  "camera_ip": "192.168.39.200",
  "position": {
    "pan_deg": 45.0,
    "tilt_deg": 20.0,
    "zoom": 0.5
  }
}
```

### Basic Movement

**Pan left:**
```bash
POST /api/v1/ptz/pan-left?speed=0.5&duration=1.0
```
- `speed`: 0.0-1.0 (strength)
- `duration`: seconds

**Pan right:**
```bash
POST /api/v1/ptz/pan-right?speed=0.5&duration=1.0
```

**Tilt up:**
```bash
POST /api/v1/ptz/tilt-up?speed=0.5&duration=1.0
```

**Tilt down:**
```bash
POST /api/v1/ptz/tilt-down?speed=0.5&duration=1.0
```

### Absolute Positioning

**Move to position:**
```bash
POST /api/v1/ptz/move
Content-Type: application/json

{
  "pan_deg": 90.0,
  "tilt_deg": 30.0,
  "zoom": 0.5
}
```
- `pan_deg`: -180 to 180 (left to right)
- `tilt_deg`: -90 to 90 (down to up)
- `zoom`: 0.0 to 1.0

**Home position (center, reset):**
```bash
POST /api/v1/ptz/home
```

### Automated Scanning

**Start auto-scan:**
```bash
POST /api/v1/ptz/scan
Content-Type: application/json

{
  "duration_sec": 30.0,
  "pan_speed": 0.3,
  "scan_type": "sweep"
}
```

**Scan types:**
- `"sweep"` - Left/right oscillation (default)
- `"circle"` - Circular patrol pattern
- `"figure8"` - Figure-8 tracking pattern

### Object Tracking

**Track detected object:**
```bash
POST /api/v1/ptz/track
Content-Type: application/json

{
  "bbox": [100, 150, 400, 500],
  "frame_width": 1920,
  "frame_height": 1080
}
```

Where `bbox` is `[x1, y1, x2, y2]` (pixel coordinates).

The camera will automatically adjust to center the object in frame.

## WebSocket Integration

PTZ status updates broadcast via WebSocket:

```json
{
  "type": "ptz_status",
  "data": {
    "connected": true,
    "camera_ip": "192.168.39.200",
    "position": {
      "pan_deg": 45.0,
      "tilt_deg": 20.0,
      "zoom": 0.5
    }
  }
}
```

## Navi AI Integration (Coming Soon)

The PTZ system is designed to integrate with Navi AI for autonomous camera control:

```python
# Navi detects a threat
detection = vakten.detect_threats()

# Command PTZ to track it
await ptz_controller.track_object(detection.bbox)

# Auto-announce discovery
await navi.speak(f"Threat detected at {detection.class_name}")
```

## Troubleshooting

**"Connection failed"**
- Verify `CAMERA_IP` and `CAMERA_PORT` are correct
- Check camera credentials in `CAMERA_USER`/`CAMERA_PASS`
- Ensure camera is on network and ONVIF service is running

**"Camera not connected" on API calls**
- Ensure `PTZ_ENABLED=true` and camera connected successfully
- Check logs for initialization errors

**Jerky/slow movement**
- Reduce `duration` parameter for snappier response
- Increase `speed` for faster pan/tilt

## ONVIF Specification

Your camera must support:
- ONVIF Media Service (GetProfiles)
- ONVIF PTZ Service (ContinuousMove, AbsoluteMove, Stop)

Tested with:
- ✅ EZVIZ H6c

## Performance Notes

- Pan/Tilt commands complete within 100-500ms depending on distance
- Object tracking updates 10 times/second when enabled
- Auto-scan patterns run until timeout or manual stop
- All operations non-blocking (async)

## Example: Sweep and Report

```bash
#!/bin/bash

# Start 20-second sweep scan
curl -X POST http://localhost:8000/api/v1/ptz/scan \
  -H "Content-Type: application/json" \
  -d '{"duration_sec": 20, "pan_speed": 0.4, "scan_type": "sweep"}'

# Wait and return to home
sleep 21
curl -X POST http://localhost:8000/api/v1/ptz/home

# Report status
curl http://localhost:8000/api/v1/ptz/status
```

