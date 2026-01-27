**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# NMEA GPS Integration

## Overview

The NMEA GPS integration provides real-time position, speed, and heading data to the AADS system. The module supports both real GPS hardware via serial port and mock data generation for development/testing.

## Features

- **Serial Port Support**: Read NMEA sentences from GPS hardware via `/dev/ttyUSB0` (configurable)
- **NMEA Parsing**: Parse standard NMEA sentences (GGA, RMC, VTG, HDT)
- **Mock Mode**: Generate realistic GPS data for testing without hardware
- **WebSocket Broadcasting**: Real-time data streaming to frontend
- **Error Handling**: Robust error handling for serial port issues
- **Configurable**: All settings via environment variables

## Configuration

Add to `.env` or set as environment variables:

```bash
# Enable/disable NMEA GPS module
NMEA_ENABLED=true

# Serial port settings (for real GPS hardware)
NMEA_SERIAL_PORT=/dev/ttyUSB0
NMEA_BAUD_RATE=4800
NMEA_TIMEOUT=1.0

# Mock mode (defaults to True in development, should be False in production)
# For development/testing: NMEA_MOCK_DATA=true
# For production with real GPS: NMEA_MOCK_DATA=false
NMEA_MOCK_DATA=true

# Update interval (seconds)
NMEA_UPDATE_INTERVAL=1.0
```

**Important**: In production deployments, explicitly set `NMEA_MOCK_DATA=false` to use real GPS hardware.

## NMEA Sentences Supported

The module parses the following standard NMEA 0183 sentences:

- **GGA**: GPS Fix Data (position, altitude, satellites, quality)
- **RMC**: Recommended Minimum Navigation Information (position, speed, heading)
- **VTG**: Track Made Good and Ground Speed (speed, heading)
- **HDT**: Heading True (true heading)

## API Endpoints

### Get NMEA Status
```bash
GET /api/v1/nmea/status
```

Response:
```json
{
  "module": "nmea_gps",
  "enabled": true,
  "running": true,
  "mock_mode": true,
  "serial_port": "/dev/ttyUSB0",
  "baud_rate": 4800,
  "has_fix": true,
  "last_update": "2026-01-19T22:36:01.541517+00:00"
}
```

### Get Current NMEA Data
```bash
GET /api/v1/nmea/data
```

Response:
```json
{
  "data": {
    "latitude": 78.2236,
    "longitude": 15.6264,
    "speed": 4.62,
    "heading": 43.72,
    "altitude": 5.0,
    "timestamp": "2026-01-19T22:36:01.541517+00:00",
    "satellites": 11,
    "quality": "good",
    "raw": "$GPRMC,123519,A,78.2236,N,15.6264,E,4.6,43.7,230394,003.1,W*6A"
  },
  "timestamp": "2026-01-19T22:36:01.541517+00:00"
}
```

### Start NMEA Module
```bash
POST /api/v1/nmea/start
```

### Stop NMEA Module
```bash
POST /api/v1/nmea/stop
```

## WebSocket Integration

The NMEA module automatically broadcasts data to all connected WebSocket clients at the configured update interval (default: 1 second).

WebSocket message format:
```json
{
  "type": "nmea",
  "data": {
    "latitude": 78.2236,
    "longitude": 15.6264,
    "speed": 4.62,
    "heading": 43.72,
    "altitude": 5.0,
    "timestamp": "2026-01-19T22:36:01.541517+00:00",
    "satellites": 11,
    "quality": "good",
    "raw": "$GPRMC,123519,A,78.2236,N,15.6264,E,4.6,43.7,230394,003.1,W*6A"
  },
  "timestamp": "2026-01-19T22:36:01.541517+00:00"
}
```

## Frontend Integration

The frontend automatically receives NMEA data via the `useNMEA` hook:

```typescript
import { useNMEA } from '../hooks/useNMEA';

const MyComponent = () => {
  const nmeaData = useNMEA();
  
  return (
    <div>
      <p>Latitude: {nmeaData.latitude}</p>
      <p>Longitude: {nmeaData.longitude}</p>
      <p>Speed: {nmeaData.speed} knots</p>
      <p>Heading: {nmeaData.heading}Â°</p>
    </div>
  );
};
```

## Mock Mode

When `NMEA_MOCK_DATA=true`, the module generates realistic GPS data:

- **Starting Position**: 78.2232Â°N, 15.6267Â°E (Svalbard, Arctic)
- **Movement**: Random walk with realistic variations
- **Speed**: 4-6 knots with variations
- **Heading**: Gradually changing course
- **Satellites**: 8-12 visible satellites
- **Quality**: "good" GPS fix

Mock mode is perfect for:
- Development without GPS hardware
- Testing frontend integration
- Demonstrations
- CI/CD pipelines

## Production Deployment

For production with real GPS hardware:

1. Connect GPS receiver to serial port (typically `/dev/ttyUSB0`)
2. Configure settings in `.env`:
   ```bash
   NMEA_ENABLED=true
   NMEA_MOCK_DATA=false
   NMEA_SERIAL_PORT=/dev/ttyUSB0
   NMEA_BAUD_RATE=4800
   ```
3. Ensure user has permission to access serial port:
   ```bash
   sudo usermod -a -G dialout $USER
   ```
4. Restart the backend service

## Troubleshooting

### GPS data not appearing
- Check `NMEA_ENABLED=true` in configuration
- Verify serial port exists: `ls -l /dev/ttyUSB*`
- Check permissions: `groups` should include `dialout`
- Try mock mode first: `NMEA_MOCK_DATA=true`

### Serial port errors
- Verify correct port: `dmesg | grep tty`
- Check baud rate matches GPS device (commonly 4800 or 9600)
- Ensure no other processes are using the port
- Test with: `cat /dev/ttyUSB0` (should see NMEA sentences)

### No WebSocket updates
- Check WebSocket connection in browser console
- Verify backend logs show NMEA broadcasting
- Check `NMEA_UPDATE_INTERVAL` setting

## Dependencies

The NMEA integration requires:

- `pyserial==3.5`: Serial port communication
- `pynmea2==1.19.0`: NMEA sentence parsing

These are automatically installed with `pip install -r requirements.txt`.

## Testing

Run the test suite:

```bash
cd backend
python -m pytest tests/test_nmea.py -v
```

Manual testing:

```bash
# Start backend
python -m app.main

# In another terminal, test endpoints
curl http://localhost:8000/api/v1/nmea/status
curl http://localhost:8000/api/v1/nmea/data
```

## Performance

- **Update Rate**: 1 Hz (configurable)
- **Latency**: <10ms from read to broadcast
- **CPU Usage**: <1% in mock mode, <2% with real GPS
- **Memory**: ~5MB for module

## Future Enhancements

- Support for additional NMEA sentences (GSA, GSV, etc.)
- AIS integration (VDM/VDO sentences)
- Multiple GPS source support
- GPS quality/accuracy monitoring
- Track logging to database
- Waypoint navigation

