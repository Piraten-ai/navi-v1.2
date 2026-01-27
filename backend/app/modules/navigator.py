"""
Navigator - Route Intelligence & NAVTEX Parsing Module
Semantic parsing of navigation messages and route optimization
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add data directory to path for map data
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from data import map_data
logger = logging.getLogger(__name__)


class NavtexMessage:
    """NAVTEX message structure"""

    def __init__(self, id: str, message_type: str, content: str):
        self.id = id
        self.message_type = message_type
        self.content = content
        self.timestamp = datetime.utcnow()
        self.coordinates: List[Tuple[float, float]] = []
        self.severity = "INFO"
        self.parsed_data: Dict = {}

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.message_type,
            "content": self.content,
            "coordinates": [[lat, lng] for lat, lng in self.coordinates],
            "severity": self.severity,
            "parsed_data": self.parsed_data,
            "timestamp": self.timestamp.isoformat(),
        }


class NavigatorModule:
    """Navigation intelligence and NAVTEX parsing"""

    def __init__(self):
        self.messages: List[NavtexMessage] = []
        self.current_route: Optional[Dict] = None
        logger.info("Navigator initialized")

    def parse_navtex(self, raw_message: str) -> NavtexMessage:
        """Parse NAVTEX message"""
        # Extract message ID
        id_match = re.search(r"ZCZC\s+(\w+)", raw_message)
        msg_id = id_match.group(1) if id_match else "UNKNOWN"

        # Determine message type
        msg_type = self._classify_message(raw_message)

        # Create message object
        message = NavtexMessage(msg_id, msg_type, raw_message)

        # Extract coordinates
        message.coordinates = self._extract_coordinates(raw_message)

        # Determine severity
        message.severity = self._assess_severity(raw_message, msg_type)

        # Parse specific data
        message.parsed_data = self._parse_details(raw_message, msg_type)

        self.messages.append(message)
        logger.info(f"Parsed NAVTEX message: {msg_id} ({msg_type})")

        return message

    def get_navtex_messages(self, limit: int = 20) -> List[Dict]:
        """Return recent NAVTEX messages as dicts (newest first)."""
        if limit <= 0:
            return []
        recent = list(reversed(self.messages[-limit:]))
        return [msg.to_dict() for msg in recent]

    def get_navtex_latest(self) -> Optional[Dict]:
        """Return the latest NAVTEX message as a dict."""
        if not self.messages:
            return None
        return self.messages[-1].to_dict()

    def get_navtex_summary(self, limit: int = 10) -> Dict:
        """Return a summary of recent NAVTEX messages."""
        recent = self.messages[-limit:] if limit > 0 else []
        counts_by_type: Dict[str, int] = {}
        counts_by_severity: Dict[str, int] = {}
        warnings: List[Dict] = []

        for msg in recent:
            counts_by_type[msg.message_type] = counts_by_type.get(msg.message_type, 0) + 1
            counts_by_severity[msg.severity] = counts_by_severity.get(msg.severity, 0) + 1
            if msg.severity in ["WARNING", "CRITICAL"]:
                warnings.append(msg.to_dict())

        return {
            "total": len(recent),
            "counts_by_type": counts_by_type,
            "counts_by_severity": counts_by_severity,
            "warnings": warnings[-5:],  # up to 5 recent warnings
            "latest": self.messages[-1].to_dict() if self.messages else None,
        }

    def _classify_message(self, content: str) -> str:
        """Classify NAVTEX message type"""
        content_upper = content.upper()

        if "ICE" in content_upper and "WARNING" in content_upper:
            return "ICE_WARNING"
        elif "GALE" in content_upper or "STORM" in content_upper:
            return "WEATHER_WARNING"
        elif "NAVIGATIONAL WARNING" in content_upper:
            return "NAV_WARNING"
        elif "SAR" in content_upper or "SEARCH" in content_upper:
            return "SAR"
        elif "PIRACY" in content_upper:
            return "SECURITY_WARNING"
        else:
            return "GENERAL"

    def _extract_coordinates(self, content: str) -> List[Tuple[float, float]]:
        """Extract coordinates from NAVTEX message"""
        coordinates = []

        # Pattern: 73-45N 025-30E or 7345N 02530E
        patterns = [
            r"(\d{2})-?(\d{2})([NS])\s+(\d{3})-?(\d{2})([EW])",  # With dashes
            r"(\d{4})([NS])\s+(\d{5})([EW])",  # Compact format
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if len(match.groups()) == 6:  # Format with dashes
                    lat_deg, lat_min, lat_dir, lng_deg, lng_min, lng_dir = match.groups()
                    lat = float(lat_deg) + float(lat_min) / 60
                    lng = float(lng_deg) + float(lng_min) / 60
                elif len(match.groups()) == 4:  # Compact format
                    lat_str, lat_dir, lng_str, lng_dir = match.groups()
                    lat = float(lat_str[:2]) + float(lat_str[2:]) / 60
                    lng = float(lng_str[:3]) + float(lng_str[3:]) / 60
                else:
                    continue

                if lat_dir == "S":
                    lat = -lat
                if lng_dir == "W":
                    lng = -lng

                coord = (lat, lng)
                # Avoid duplicates from overlapping patterns
                if coord not in coordinates:
                    coordinates.append(coord)

        return coordinates

    def _assess_severity(self, content: str, msg_type: str) -> str:
        """Assess message severity"""
        content_upper = content.upper()

        if "IMMEDIATE" in content_upper or "URGENT" in content_upper:
            return "CRITICAL"
        elif "WARNING" in content_upper or msg_type.endswith("_WARNING"):
            return "WARNING"
        elif "CAUTION" in content_upper:
            return "CAUTION"
        else:
            return "INFO"

    def _parse_details(self, content: str, msg_type: str) -> Dict:
        """Parse message-specific details"""
        details = {}

        if msg_type == "ICE_WARNING":
            # Extract drift information
            drift_match = re.search(r"DRIFTING\s+(\w+)\s+([\d.]+)\s+KNOTS", content, re.IGNORECASE)
            if drift_match:
                details["drift_direction"] = drift_match.group(1)
                details["drift_speed"] = float(drift_match.group(2))

            # Extract ice type
            if "ICEBERG" in content.upper():
                details["ice_type"] = "iceberg"
            elif "FLOE" in content.upper():
                details["ice_type"] = "ice_floe"
            else:
                details["ice_type"] = "ice"

        elif msg_type == "WEATHER_WARNING":
            # Extract wind speed
            wind_match = re.search(r"(\d+)\s*KTS?", content, re.IGNORECASE)
            if wind_match:
                details["wind_speed_kts"] = int(wind_match.group(1))

        return details

    def plan_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        avoid_ice: bool = True,
        optimize_for: str = "fuel",
        include_map_hazards: bool = False,
    ) -> Dict:
        """Plan route with hazard avoidance and map data integration"""
        # Calculate basic route
        route = {
            "origin": {"lat": origin[0], "lng": origin[1]},
            "destination": {"lat": destination[0], "lng": destination[1]},
            "waypoints": [],
            "distance_nm": self._calculate_distance(origin, destination),
            "eta_hours": None,
            "hazards": [],
            "advice": [],
            "map_info": {},
        }

        # Add map data context
        try:
            # Sea areas
            origin_sea = map_data.get_sea_area(origin[0], origin[1])
            dest_sea = map_data.get_sea_area(destination[0], destination[1])
            route["map_info"]["origin_sea_area"] = origin_sea
            route["map_info"]["destination_sea_area"] = dest_sea

            # Nearby waypoints
            nearby_wps = map_data.get_nearby_waypoints(origin[0], origin[1], max_distance_nm=100.0)
            if nearby_wps:
                route["map_info"]["nearby_waypoints"] = nearby_wps[:3]  # Top 3 closest

            # Ice zones
            ice_zones = map_data.get_ice_zones_in_area(origin[0], origin[1], radius_deg=5.0)
            if ice_zones:
                route["map_info"]["ice_zones"] = ice_zones
                if avoid_ice:
                    for zone in ice_zones:
                        if zone["severity"] in ["HIGH", "CRITICAL"]:
                            route["advice"].append(f"WARNING: {zone['name']} - {zone['description']}")

            if include_map_hazards:
                # Static hazards from map data
                map_hazards = map_data.get_hazards_near_route(origin, destination, threshold_nm=50.0)
                for hazard in map_hazards:
                    route["hazards"].append(
                        {
                            "type": hazard["type"],
                            "name": hazard["name"],
                            "severity": hazard["severity"],
                            "center": hazard["center"],
                            "radius_nm": hazard["radius_nm"],
                            "source": "map_data",
                        }
                    )

            # Nearest harbor for emergency
            nearest_harbor = map_data.get_nearest_harbor(origin[0], origin[1])
            if nearest_harbor:
                route["map_info"]["nearest_harbor"] = nearest_harbor

        except Exception as e:
            logger.warning(f"Failed to load map data: {e}")

        # Check for NAVTEX hazards along route
        for msg in self.messages:
            if msg.severity in ["CRITICAL", "WARNING"]:
                # Check if hazard is near route (simplified)
                for coord in msg.coordinates:
                    if self._is_near_route(coord, origin, destination, threshold_nm=50):
                        route["hazards"].append(
                            {
                                "type": msg.message_type,
                                "position": coord,
                                "severity": msg.severity,
                                "message": msg.content[:100],
                                "source": "navtex",
                            }
                        )

        # Generate routing advice
        if route["hazards"]:
            route["advice"].append(f"CAUTION: {len(route['hazards'])} hazard(s) detected along route")
            if avoid_ice:
                ice_hazards = [h for h in route["hazards"] if "ice" in h.get("type", "").lower() or "ICE" in h.get("type", "")]
                if ice_hazards:
                    route["advice"].append(f"Recommend course alteration to avoid {len(ice_hazards)} ice hazard(s)")
        else:
            route["advice"].append("Route clear of known hazards")

        self.current_route = route
        return route

    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate great circle distance in nautical miles"""
        import math

        lat1, lng1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lng2 = math.radians(point2[0]), math.radians(point2[1])

        dlat = lat2 - lat1
        dlng = lng2 - lng1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius in nautical miles
        r_nm = 3440.065

        return r_nm * c

    def _is_near_route(
        self,
        point: Tuple[float, float],
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        threshold_nm: float = 50,
    ) -> bool:
        """Check if point is near the route"""
        # Simplified: check if point is within threshold of either origin or destination
        dist_to_origin = self._calculate_distance(point, origin)
        dist_to_dest = self._calculate_distance(point, destination)

        return dist_to_origin < threshold_nm or dist_to_dest < threshold_nm

    def get_hazards(self, severity: Optional[str] = None) -> List[Dict]:
        """Get current hazards"""
        messages = self.messages

        if severity:
            messages = [m for m in messages if m.severity == severity]

        return [m.to_dict() for m in messages if m.severity in ["CRITICAL", "WARNING"]]

    def get_map_info(self, lat: float, lon: float) -> Dict:
        """Get map data for a specific position"""
        try:
            info = {
                "position": {"lat": lat, "lon": lon},
                "sea_area": map_data.get_sea_area(lat, lon),
                "nearby_waypoints": map_data.get_nearby_waypoints(lat, lon, max_distance_nm=100.0),
                "ice_zones": map_data.get_ice_zones_in_area(lat, lon, radius_deg=5.0),
                "nearest_harbor": map_data.get_nearest_harbor(lat, lon),
                "nearby_coastlines": [name for name, _ in map_data.get_nearby_coastlines(lat, lon, max_distance_deg=2.0)],
            }
            return info
        except Exception as e:
            logger.error(f"Failed to get map info: {e}")
            return {"error": str(e)}

    def get_status(self) -> Dict:
        """Get module status"""
        return {
            "module": "navigator",
            "status": "ready",
            "messages_parsed": len(self.messages),
            "active_warnings": len([m for m in self.messages if m.severity == "WARNING"]),
            "critical_alerts": len([m for m in self.messages if m.severity == "CRITICAL"]),
            "current_route": self.current_route is not None,
        }


# Global instance
navigator = NavigatorModule()
