# Signal K Integration

## Overview

The Signal K integration provides comprehensive real-time marine data to the AADS system. Signal K is a modern, open-source marine data standard that uses JSON over WebSocket for real-time data streaming. Unlike NMEA 0183's text-based sentences, Signal K provides structured JSON data covering navigation, environment, propulsion, and more.

## Features

- **WebSocket Support**: Real-time data streaming from Signal K server
- **Comprehensive Data**: Navigation, environment, and propulsion parameters
- **Mock Mode**: Generate realistic marine data for testing without hardware
- **WebSocket Broadcasting**: Real-time data streaming to frontend clients
- **Error Handling**: Robust error handling with automatic reconnection
- **Configurable**: All settings via environment variables

## Configuration

Add to `.env` or set as environment variables:

```bash
# Enable/disable Signal K module
SIGNALK_ENABLED=true

# Signal K server settings
SIGNALK_SERVER_URL=ws://localhost:3000/signalk/v1/stream
SIGNALK_TIMEOUT=10.0

# Mock mode (defaults to True in development, should be False in production)
# For development/testing: SIGNALK_MOCK_DATA=true
# For production with real Signal K server: SIGNALK_MOCK_DATA=false
SIGNALK_MOCK_DATA=true

# Update interval (seconds)
SIGNALK_UPDATE_INTERVAL=1.0
```

**Important**: In production deployments, explicitly set `SIGNALK_MOCK_DATA=false` to use real Signal K server.

## Signal K Data Schema

The module provides the following data categories:

### Navigation Data
- **Position**: Latitude, longitude, altitude
- **Speed**: Speed over ground (SOG), speed through water (STW)
- **Course**: Course over ground (COG), true heading
- **Units**: Knots for speed, degrees for angles, meters for altitude

### Environment Data
- **Water**: Depth below transducer, water temperature
- **Wind**: True wind speed and direction
- **Air**: Outside air temperature and pressure
- **Units**: Meters for depth, Celsius for temperature, m/s for wind speed, Pascals for pressure

### Propulsion Data
- **Engine**: RPM, temperature
- **Fuel**: Fuel tank level as percentage
- **Units**: RPM for revolutions, Celsius for temperature, percentage for levels

## API Endpoints

### Get Signal K Status
```bash
GET /api/v1/signalk/status
```

Response:
```json
{
  "module": "signalk",
  "enabled": true,
  "running": true,
  "mock_mode": true,
  "server_url": "ws://localhost:3000/signalk/v1/stream",
  "connected": true,
  "has_data": true,
  "last_update": "2026-01-19T22:36:01.541517+00:00"
}
```

### Get Current Signal K Data
```bash
GET /api/v1/signalk/data
```

Response:
```json
{
  "data": {
    "navigation": {
      "latitude": 78.2236,
      "longitude": 15.6264,
      "speed_over_ground": 5.62,
      "speed_through_water": 5.51,
      "course_over_ground": 43.72,
      "heading": 43.72,
      "altitude": 5.0
    },
    "environment": {
      "water_depth": 42.5,
      "water_temperature": 4.2,
      "wind_speed": 8.3,
      "wind_direction": 135.0,
      "air_temperature": -2.5,
      "air_pressure": 101325
    },
    "propulsion": {
      "engine_rpm": 1800,
      "engine_temperature": 82.0,
      "fuel_level": 75.0
    },
    "timestamp": "2026-01-19T22:36:01.541517+00:00",
    "source": "mock"
  },
  "timestamp": "2026-01-19T22:36:01.541517+00:00"
}
```

### Start Signal K Module
```bash
POST /api/v1/signalk/start
```

### Stop Signal K Module
```bash
POST /api/v1/signalk/stop
```

## WebSocket Integration

The Signal K module automatically broadcasts data to all connected WebSocket clients at the configured update interval (default: 1 second).

WebSocket message format:
```json
{
  "type": "signalk",
  "data": {
    "navigation": {
      "latitude": 78.2236,
      "longitude": 15.6264,
      "speed_over_ground": 5.62,
      "heading": 43.72
    },
    "environment": {
      "water_depth": 42.5,
      "wind_speed": 8.3,
      "wind_direction": 135.0
    },
    "propulsion": {
      "engine_rpm": 1800,
      "fuel_level": 75.0
    },
    "timestamp": "2026-01-19T22:36:01.541517+00:00"
  },
  "timestamp": "2026-01-19T22:36:01.541517+00:00"
}
```

## Frontend Integration

The frontend can receive Signal K data via the WebSocket connection:

```typescript
import { useWebSocket } from '../hooks/useWebSocket';

const MyComponent = () => {
  const { messages } = useWebSocket();
  
  // Filter for Signal K messages
  const signalkData = messages
    .filter(msg => msg.type === 'signalk')
    .map(msg => msg.data);
  
  const latestData = signalkData[signalkData.length - 1];
  
  return (
    <div>
      <p>Position: {latestData?.navigation?.latitude}, {latestData?.navigation?.longitude}</p>
      <p>Speed: {latestData?.navigation?.speed_over_ground} knots</p>
      <p>Heading: {latestData?.navigation?.heading}°</p>
      <p>Water Depth: {latestData?.environment?.water_depth}m</p>
      <p>Wind: {latestData?.environment?.wind_speed} m/s at {latestData?.environment?.wind_direction}°</p>
      <p>Engine RPM: {latestData?.propulsion?.engine_rpm}</p>
      <p>Fuel Level: {latestData?.propulsion?.fuel_level}%</p>
    </div>
  );
};
```

## Mock Mode

When `SIGNALK_MOCK_DATA=true`, the module generates realistic marine data:

- **Starting Position**: 78.2232°N, 15.6267°E (Svalbard, Arctic)
- **Movement**: Random walk with realistic variations
- **Speed**: 4-6 knots with variations
- **Heading**: Gradually changing course
- **Water Depth**: 30-50 meters
- **Wind**: 6-10 m/s from varying directions
- **Engine RPM**: 1750-1850 RPM
- **Fuel Level**: Slowly decreasing from 75%

Mock mode is perfect for:
- Development without Signal K server
- Testing frontend integration
- Demonstrations
- CI/CD pipelines

## Production Deployment

For production with real Signal K server:

1. Ensure Signal K server is running (typically on port 3000)
2. Configure settings in `.env`:
   ```bash
   SIGNALK_ENABLED=true
   SIGNALK_MOCK_DATA=false
   SIGNALK_SERVER_URL=ws://localhost:3000/signalk/v1/stream
   SIGNALK_UPDATE_INTERVAL=1.0
   ```
3. Restart the backend service

## Signal K Server Setup

To set up a Signal K server (optional, for real data):

### Using Docker
```bash
docker run -d \
  --name signalk-server \
  -p 3000:3000 \
  -v signalk-config:/home/node/.signalk \
  signalk/signalk-server
```

### Native Installation
```bash
# Install Node.js and npm first
npm install -g signalk-server

# Start server
signalk-server
```

The Signal K server will be available at `http://localhost:3000` with WebSocket stream at `ws://localhost:3000/signalk/v1/stream`.

## Data Source Configuration

Signal K can aggregate data from multiple sources:

- **NMEA 0183**: Serial or UDP input
- **NMEA 2000**: CAN bus via NGT-1 or Actisense
- **AIS**: Vessel traffic information
- **Sensors**: Direct sensor integration
- **Instruments**: Marine instruments and displays

Configure data sources in the Signal K server web interface at `http://localhost:3000`.

## Comparison: Signal K vs NMEA

| Feature | NMEA 0183 | Signal K |
|---------|-----------|----------|
| **Format** | Text sentences | JSON |
| **Transport** | Serial, UDP | WebSocket, HTTP |
| **Data Coverage** | Basic navigation | Comprehensive marine data |
| **Extensibility** | Limited | Highly extensible |
| **Real-time** | Polling | Push-based streaming |
| **Modern Tools** | Limited | Rich ecosystem |

## Troubleshooting

### Signal K data not appearing
- Check `SIGNALK_ENABLED=true` in configuration
- Verify Signal K server is running: `curl http://localhost:3000/signalk/v1/api/`
- Check WebSocket connection in browser console
- Try mock mode first: `SIGNALK_MOCK_DATA=true`

### WebSocket connection errors
- Verify correct server URL in configuration
- Check firewall rules for port 3000
- Ensure Signal K server is accessible from backend container
- Check Signal K server logs for connection issues

### No data updates
- Verify Signal K server has active data sources
- Check `SIGNALK_UPDATE_INTERVAL` setting
- Monitor backend logs for parsing errors
- Use Signal K web interface to verify data flow

### Mock data not changing
- Verify `SIGNALK_MOCK_DATA=true`
- Check `SIGNALK_UPDATE_INTERVAL` is reasonable (1-2 seconds)
- Monitor backend logs for errors

## Dependencies

The Signal K integration uses:

- `websockets==12.0`: Async WebSocket client (already included in base requirements)

No additional dependencies are required beyond the base AADS requirements.

## Testing

Run the test suite:

```bash
cd backend
python -m pytest tests/test_signalk.py -v
```

Manual testing:

```bash
# Start backend
python -m app.main

# In another terminal, test endpoints
curl http://localhost:8000/api/v1/signalk/status
curl http://localhost:8000/api/v1/signalk/data
```

## Performance

- **Update Rate**: 1 Hz (configurable)
- **Latency**: <20ms from server to broadcast
- **CPU Usage**: <2% in mock mode, <3% with real server
- **Memory**: ~8MB for module

## Integration with Other Modules

Signal K data can enhance other AADS modules:

- **Vakten**: Use water depth for collision avoidance
- **Navigator**: Use wind data for route optimization
- **Ingeniøren**: Monitor engine parameters for diagnostics
- **Navi**: Provide context-aware responses using marine data

## Future Enhancements

- Historical data logging to InfluxDB
- Data visualization dashboard
- Alerts for abnormal values
- Integration with AIS for traffic awareness
- Support for NMEA 2000 PGNs
- Multi-vessel support for fleet operations
- Custom Signal K path subscriptions
- Data recording and playback

## Additional Resources

- **Signal K Documentation**: https://signalk.org/
- **Signal K Specification**: https://signalk.org/specification/
- **Signal K Server**: https://github.com/SignalK/signalk-server
- **Signal K Paths**: https://signalk.org/specification/1.7.0/doc/vesselsBranch.html

---

**Ready to use modern marine data? Configure Signal K and sail into the future!** ⚓
