"""
Arctic Maritime Map Data
========================
Static geographic data for navigation and route planning in Arctic waters.
Includes sea areas, coastlines, ice zones, and navigational reference points.
"""

from typing import Dict, List, Tuple

# Svalbard archipelago coordinates (major islands)
SVALBARD_COASTLINES = {
    "spitsbergen": [
        (80.5, 18.0),
        (79.9, 16.5),
        (78.9, 14.5),
        (78.2, 13.5),
        (77.5, 15.0),
        (76.5, 16.5),
        (76.7, 18.0),
        (77.5, 20.5),
        (78.5, 22.5),
        (79.5, 23.0),
        (80.5, 21.5),
        (80.7, 19.5),
        (80.5, 18.0),
    ],
    "nordaustlandet": [
        (80.5, 23.0),
        (80.2, 21.5),
        (79.5, 21.0),
        (79.2, 22.5),
        (79.5, 24.5),
        (80.0, 26.0),
        (80.5, 27.0),
        (80.8, 25.5),
        (80.5, 23.0),
    ],
    "edgeoya": [
        (78.3, 22.5),
        (78.0, 21.5),
        (77.5, 22.0),
        (77.8, 24.0),
        (78.3, 24.5),
        (78.5, 23.5),
        (78.3, 22.5),
    ],
    "barentsoya": [
        (78.5, 20.5),
        (78.3, 19.0),
        (77.8, 19.5),
        (77.7, 21.0),
        (78.0, 21.5),
        (78.5, 21.0),
        (78.5, 20.5),
    ],
}

# Norwegian Sea areas (NAVAREA I)
SEA_AREAS = {
    "norwegian_sea": {
        "name": "Norwegian Sea",
        "bounds": [(65.0, 0.0), (72.0, 0.0), (72.0, 15.0), (65.0, 15.0)],
        "description": "Major shipping lane to Arctic",
    },
    "barents_sea": {
        "name": "Barents Sea",
        "bounds": [(70.0, 20.0), (80.0, 20.0), (80.0, 60.0), (70.0, 60.0)],
        "description": "Arctic sea area with seasonal ice",
    },
    "greenland_sea": {
        "name": "Greenland Sea",
        "bounds": [(70.0, -20.0), (80.0, -20.0), (80.0, 10.0), (70.0, 10.0)],
        "description": "Western Arctic approach",
    },
    "svalbard_waters": {
        "name": "Svalbard Waters",
        "bounds": [(76.0, 10.0), (81.0, 10.0), (81.0, 30.0), (76.0, 30.0)],
        "description": "Arctic archipelago waters - Ice Warning Zone",
    },
}

# Ice zones (seasonal variation - this is winter/spring)
ICE_ZONES = {
    "marginal_ice_zone": {
        "name": "Marginal Ice Zone",
        "coords": [(79.5, 15.0), (81.0, 20.0), (82.0, 25.0), (80.0, 30.0)],
        "severity": "MODERATE",
        "description": "Variable ice concentration 10-80%",
        "season": "year-round",
    },
    "fast_ice_zone": {
        "name": "Fast Ice Zone",
        "coords": [(80.5, 16.0), (82.0, 18.0), (82.5, 22.0), (81.0, 24.0)],
        "severity": "HIGH",
        "description": "Land-fast ice, navigation prohibited",
        "season": "October-July",
    },
    "polar_ice_edge": {
        "name": "Polar Ice Edge",
        "coords": [(81.0, 10.0), (83.0, 15.0), (84.0, 25.0), (82.0, 35.0)],
        "severity": "CRITICAL",
        "description": "Permanent ice cap boundary",
        "season": "permanent",
    },
}

# Navigational waypoints and reference points
WAYPOINTS = {
    "longyearbyen": {
        "name": "Longyearbyen",
        "coords": (78.2232, 15.6267),
        "type": "port",
        "description": "Main settlement and port in Svalbard",
    },
    "ny_alesund": {
        "name": "Ny-Ålesund",
        "coords": (78.9247, 11.9308),
        "type": "research_station",
        "description": "Northernmost civilian settlement",
    },
    "bjornoya": {
        "name": "Bjørnøya (Bear Island)",
        "coords": (74.5, 19.0),
        "type": "island",
        "description": "Isolated island south of Svalbard",
    },
    "isfjorden_entrance": {
        "name": "Isfjorden Entrance",
        "coords": (78.0, 13.5),
        "type": "navigational",
        "description": "Main fjord entrance to Longyearbyen",
    },
    "storfjorden": {
        "name": "Storfjorden",
        "coords": (77.5, 19.0),
        "type": "strait",
        "description": "Channel between Spitsbergen and Edgeøya",
    },
    "hinlopen_strait": {
        "name": "Hinlopen Strait",
        "coords": (79.5, 18.5),
        "type": "strait",
        "description": "Narrow passage, ice-prone",
    },
}

# Shipping lanes and recommended routes
SHIPPING_LANES = {
    "longyearbyen_approach": {
        "name": "Longyearbyen Approach",
        "waypoints": [
            (76.0, 15.0),  # Entry from south
            (77.0, 14.5),
            (78.0, 15.0),
            (78.2, 15.6),  # Longyearbyen
        ],
        "description": "Standard approach from Norwegian mainland",
    },
    "north_passage": {
        "name": "North Spitsbergen Passage",
        "waypoints": [
            (78.2, 15.6),  # Longyearbyen
            (79.0, 12.0),
            (79.8, 11.5),
            (80.5, 13.0),
        ],
        "description": "Northern route, seasonal (June-September)",
    },
    "eastern_route": {
        "name": "Eastern Svalbard Route",
        "waypoints": [
            (78.2, 15.6),  # Longyearbyen
            (78.5, 18.0),
            (79.0, 20.0),
            (79.5, 22.0),
        ],
        "description": "Via Storfjorden, heavy ice risk",
    },
}

# Hazard zones
HAZARD_ZONES = {
    "ice_hazard_1": {
        "name": "Northwest Ice Field",
        "center": (79.5, 12.0),
        "radius_nm": 20,
        "type": "ice",
        "severity": "WARNING",
    },
    "ice_hazard_2": {
        "name": "Northeast Polar Approach",
        "center": (80.5, 25.0),
        "radius_nm": 50,
        "type": "ice",
        "severity": "CRITICAL",
    },
    "shallow_water_1": {
        "name": "Storfjorden Banks",
        "center": (77.0, 18.5),
        "radius_nm": 10,
        "type": "shallow",
        "severity": "CAUTION",
    },
}

# Safe harbors and anchorages
SAFE_HARBORS = {
    "longyearbyen_harbor": {
        "name": "Longyearbyen Harbor",
        "coords": (78.2232, 15.6267),
        "depth_m": 15.0,
        "capacity": "unlimited",
        "facilities": ["fuel", "supplies", "medical", "repair"],
    },
    "ny_alesund_harbor": {
        "name": "Ny-Ålesund Harbor",
        "coords": (78.9247, 11.9308),
        "depth_m": 10.0,
        "capacity": "limited",
        "facilities": ["fuel", "supplies"],
    },
    "barentsburg": {
        "name": "Barentsburg",
        "coords": (78.0642, 14.2333),
        "depth_m": 12.0,
        "capacity": "medium",
        "facilities": ["fuel", "supplies"],
    },
}


def get_nearby_coastlines(lat: float, lon: float, max_distance_deg: float = 2.0) -> List[Tuple[str, List[Tuple[float, float]]]]:
    """Get coastlines near a given position"""
    nearby = []
    for name, points in SVALBARD_COASTLINES.items():
        for point in points:
            dist = ((point[0] - lat) ** 2 + (point[1] - lon) ** 2) ** 0.5
            if dist <= max_distance_deg:
                nearby.append((name, points))
                break
    return nearby


def get_sea_area(lat: float, lon: float) -> str:
    """Determine which sea area a position is in"""
    for area_id, area_data in SEA_AREAS.items():
        bounds = area_data["bounds"]
        # Simple bounding box check
        min_lat = min(p[0] for p in bounds)
        max_lat = max(p[0] for p in bounds)
        min_lon = min(p[1] for p in bounds)
        max_lon = max(p[1] for p in bounds)

        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return area_data["name"]

    return "Unknown Sea Area"


def get_nearby_waypoints(lat: float, lon: float, max_distance_nm: float = 50.0) -> List[Dict]:
    """Get waypoints within range"""
    from math import radians, sin, cos, asin, sqrt

    nearby = []
    for wp_id, wp_data in WAYPOINTS.items():
        wp_lat, wp_lon = wp_data["coords"]

        # Haversine distance
        lat1, lon1 = radians(lat), radians(lon)
        lat2, lon2 = radians(wp_lat), radians(wp_lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        distance_nm = 3440.065 * c  # Earth radius in nautical miles

        if distance_nm <= max_distance_nm:
            nearby.append(
                {
                    "id": wp_id,
                    "name": wp_data["name"],
                    "coords": wp_data["coords"],
                    "type": wp_data["type"],
                    "distance_nm": round(distance_nm, 1),
                    "description": wp_data["description"],
                }
            )

    return sorted(nearby, key=lambda x: x["distance_nm"])


def get_ice_zones_in_area(lat: float, lon: float, radius_deg: float = 3.0) -> List[Dict]:
    """Get ice zones near a position"""
    zones = []
    for zone_id, zone_data in ICE_ZONES.items():
        for point in zone_data["coords"]:
            dist = ((point[0] - lat) ** 2 + (point[1] - lon) ** 2) ** 0.5
            if dist <= radius_deg:
                zones.append(
                    {
                        "id": zone_id,
                        "name": zone_data["name"],
                        "severity": zone_data["severity"],
                        "description": zone_data["description"],
                        "season": zone_data["season"],
                    }
                )
                break
    return zones


def get_hazards_near_route(origin: Tuple[float, float], destination: Tuple[float, float], threshold_nm: float = 25.0) -> List[Dict]:
    """Get hazards that may affect a planned route"""
    from math import radians, sin, cos, asin, sqrt

    hazards = []
    # Simplified: check hazards near origin or destination
    for hazard_id, hazard_data in HAZARD_ZONES.items():
        center_lat, center_lon = hazard_data["center"]

        for point in [origin, destination]:
            lat, lon = point
            lat1, lon1 = radians(lat), radians(lon)
            lat2, lon2 = radians(center_lat), radians(center_lon)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            distance_nm = 3440.065 * c

            if distance_nm <= (hazard_data["radius_nm"] + threshold_nm):
                hazards.append(
                    {
                        "id": hazard_id,
                        "name": hazard_data["name"],
                        "type": hazard_data["type"],
                        "severity": hazard_data["severity"],
                        "center": hazard_data["center"],
                        "radius_nm": hazard_data["radius_nm"],
                    }
                )
                break

    return hazards


def get_nearest_harbor(lat: float, lon: float) -> Dict:
    """Find nearest safe harbor"""
    from math import radians, sin, cos, asin, sqrt

    nearest = None
    min_distance = float("inf")

    for harbor_id, harbor_data in SAFE_HARBORS.items():
        h_lat, h_lon = harbor_data["coords"]

        lat1, lon1 = radians(lat), radians(lon)
        lat2, lon2 = radians(h_lat), radians(h_lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        distance_nm = 3440.065 * c

        if distance_nm < min_distance:
            min_distance = distance_nm
            nearest = {
                "id": harbor_id,
                "name": harbor_data["name"],
                "coords": harbor_data["coords"],
                "distance_nm": round(distance_nm, 1),
                "depth_m": harbor_data["depth_m"],
                "facilities": harbor_data["facilities"],
            }

    return nearest
