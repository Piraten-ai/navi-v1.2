**Status**: Legacy doc. Review against current stack (Jetson + Pi + PC). Primary references: docs/current/COMPLETE_TECHNICAL_REFERENCE.md, docs/current/HARDWARE_PLAN.md, docs/current/BRIDGE_SPEC.md.
# Arctic Map Data Integration

The Navigator module now includes comprehensive Arctic maritime map data for the Svalbard region.

## Available Data

### 1. Coastlines
- **Spitsbergen** - Main island
- **Nordaustlandet** - Northeast island
- **EdgeÃ¸ya** - Edge island
- **BarentsÃ¸ya** - Barents island

### 2. Sea Areas (NAVAREA I)
- **Norwegian Sea** (65-72Â°N, 0-15Â°E) - Major shipping lane to Arctic
- **Barents Sea** (70-80Â°N, 20-60Â°E) - Arctic sea with seasonal ice
- **Greenland Sea** (70-80Â°N, -20-10Â°E) - Western Arctic approach
- **Svalbard Waters** (76-81Â°N, 10-30Â°E) - Ice Warning Zone

### 3. Ice Zones
- **Marginal Ice Zone** - Variable ice concentration 10-80% (year-round)
- **Fast Ice Zone** - Land-fast ice, navigation prohibited (Oct-Jul)
- **Polar Ice Edge** - Permanent ice cap boundary

### 4. Navigation Waypoints
- **Longyearbyen** (78.2232Â°N, 15.6267Â°E) - Main port
- **Ny-Ã…lesund** (78.9247Â°N, 11.9308Â°E) - Northernmost settlement
- **BjÃ¸rnÃ¸ya** (74.5Â°N, 19.0Â°E) - Bear Island
- **Isfjorden Entrance** (78.0Â°N, 13.5Â°E) - Main fjord entrance
- **Storfjorden** (77.5Â°N, 19.0Â°E) - Channel between islands
- **Hinlopen Strait** (79.5Â°N, 18.5Â°E) - Narrow ice-prone passage

### 5. Safe Harbors
- **Longyearbyen Harbor** - Depth: 15m, Full facilities
- **Ny-Ã…lesund Harbor** - Depth: 10m, Limited facilities  
- **Barentsburg** - Depth: 12m, Medium capacity

### 6. Shipping Lanes
- **Longyearbyen Approach** - Standard route from Norwegian mainland
- **North Passage** - Seasonal route (Jun-Sep only)
- **Eastern Route** - Via Storfjorden (heavy ice risk)

### 7. Hazard Zones
- **Northwest Ice Field** - 20nm radius ice hazard
- **Northeast Polar Approach** - 50nm radius critical ice zone
- **Storfjorden Banks** - 10nm radius shallow water

## API Usage

### Get Map Info for Position
```bash
GET /api/v1/navigator/map_info?lat=78.2232&lon=15.6267
```

**Response:**
```json
{
  "position": {"lat": 78.2232, "lon": 15.6267},
  "sea_area": "Svalbard Waters",
  "nearby_waypoints": [
    {
      "id": "longyearbyen",
      "name": "Longyearbyen",
      "coords": [78.2232, 15.6267],
      "type": "port",
      "distance_nm": 0.0,
      "description": "Main settlement and port in Svalbard"
    }
  ],
  "ice_zones": [
    {
      "id": "marginal_ice_zone",
      "name": "Marginal Ice Zone",
      "severity": "MODERATE",
      "description": "Variable ice concentration 10-80%",
      "season": "year-round"
    }
  ],
  "nearest_harbor": {
    "id": "longyearbyen_harbor",
    "name": "Longyearbyen Harbor",
    "coords": [78.2232, 15.6267],
    "distance_nm": 0.0,
    "depth_m": 15.0,
    "facilities": ["fuel", "supplies", "medical", "repair"]
  },
  "nearby_coastlines": ["spitsbergen"]
}
```

### Route Planning with Map Data
```bash
POST /api/v1/navigator/plan_route
  ?origin_lat=78.2232&origin_lng=15.6267
  &dest_lat=79.0&dest_lng=16.0
  &avoid_ice=true
```

**Response now includes:**
```json
{
  "origin": {"lat": 78.2232, "lng": 15.6267},
  "destination": {"lat": 79.0, "lng": 16.0},
  "distance_nm": 52.3,
  "hazards": [
    {
      "type": "ice",
      "name": "Northwest Ice Field",
      "severity": "WARNING",
      "center": [79.5, 12.0],
      "radius_nm": 20,
      "source": "map_data"
    }
  ],
  "advice": [
    "WARNING: Marginal Ice Zone - Variable ice concentration 10-80%",
    "CAUTION: 1 hazard(s) detected along route"
  ],
  "map_info": {
    "origin_sea_area": "Svalbard Waters",
    "destination_sea_area": "Svalbard Waters",
    "nearby_waypoints": [...],
    "ice_zones": [...],
    "nearest_harbor": {...}
  }
}
```

## Python Module Usage

```python
from data import map_data

# Get sea area
area = map_data.get_sea_area(78.2232, 15.6267)
# Returns: "Svalbard Waters"

# Find nearby waypoints
waypoints = map_data.get_nearby_waypoints(78.2232, 15.6267, max_distance_nm=100)
# Returns: List of waypoint dictionaries sorted by distance

# Check for ice zones
ice_zones = map_data.get_ice_zones_in_area(78.2232, 15.6267, radius_deg=5.0)
# Returns: List of ice zone dictionaries

# Find nearest safe harbor
harbor = map_data.get_nearest_harbor(78.2232, 15.6267)
# Returns: Harbor dictionary with facilities and distance

# Get hazards near route
hazards = map_data.get_hazards_near_route((78.0, 15.0), (79.0, 16.0), threshold_nm=50)
# Returns: List of hazard dictionaries
```

## Data Sources

Map data is based on:
- Norwegian Hydrographic Service nautical charts
- Norwegian Meteorological Institute ice data
- Norwegian Polar Institute geographic data
- NAVAREA I navigation warnings

**Note:** This is simplified data for demonstration. Production systems should use official nautical charts and real-time ice data from proper sources (Norwegian Ice Service, AARI, etc.).

## Future Enhancements

- Real-time ice chart integration (Met.no Ice Service API)
- Weather routing optimization
- Automatic waypoint generation
- AIS traffic data overlay
- Depth contours and bathymetry
- Current and tide predictions
- Visibility and sea state forecasts

