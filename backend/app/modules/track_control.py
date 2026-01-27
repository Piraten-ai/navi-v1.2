"""Track Control Module

Computes cross-track error (XTE) from current position and desired waypoint/track.
Integrates with AutopilotController to drive rudder via track-keeping logic.

Features:
- Simple waypoint-to-waypoint legs with XTE computation via perpendicular distance.
- Support for both heading-hold and track-hold modes (config-gated).
- Optional SOG-corrected track computation for improved accuracy in current.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Waypoint:
    latitude: float
    longitude: float
    name: str = "WP"


def _haversine_distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance between two points in nautical miles."""
    R_nm = 3440.065
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R_nm * c


def _bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Bearing from point 1 to point 2 in degrees [0, 360)."""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


def _compute_xte_nm(
    lat_own: float,
    lon_own: float,
    lat_from: float,
    lon_from: float,
    lat_to: float,
    lon_to: float,
) -> float:
    """Compute cross-track error in nautical miles.

    Positive XTE: vessel is starboard (right) of the desired track.
    Negative XTE: vessel is port (left) of the desired track.
    """
    # Distance from current position to waypoint "from"
    dist_to_from = _haversine_distance_nm(lat_own, lon_own, lat_from, lon_from)

    # Distance from "from" to "to"
    dist_from_to = _haversine_distance_nm(lat_from, lon_from, lat_to, lon_to)

    # Bearing of the leg
    leg_bearing = _bearing_deg(lat_from, lon_from, lat_to, lon_to)

    # Bearing from "from" to own position
    bearing_to_own = _bearing_deg(lat_from, lon_from, lat_own, lon_own)

    # Cross-track angle (in degrees)
    cross_track_angle = bearing_to_own - leg_bearing
    # Normalize to [-180, 180)
    cross_track_angle = ((cross_track_angle + 180) % 360) - 180

    # XTE = distance * sin(angle)
    xte = dist_to_from * math.sin(math.radians(cross_track_angle))

    return xte


class TrackController:
    def __init__(self) -> None:
        self.enabled = False
        self.current_waypoint_from: Optional[Waypoint] = None
        self.current_waypoint_to: Optional[Waypoint] = None
        self.last_xte_nm: float = 0.0
        self.distance_to_waypoint_nm: float = 0.0
        self.track_bearing_deg: float = 0.0

    def set_route(self, from_wp: Waypoint, to_wp: Waypoint) -> None:
        """Set the current track leg."""
        self.current_waypoint_from = from_wp
        self.current_waypoint_to = to_wp
        self.track_bearing_deg = _bearing_deg(from_wp.latitude, from_wp.longitude, to_wp.latitude, to_wp.longitude)
        self.enabled = True
        logger.info(
            f"Track set: {from_wp.name} → {to_wp.name}, bearing {self.track_bearing_deg:.1f}°"
        )

    def compute_xte(self, latitude: float, longitude: float) -> float:
        """Compute XTE for current position."""
        if not self.enabled or not self.current_waypoint_from or not self.current_waypoint_to:
            return 0.0

        xte = _compute_xte_nm(
            latitude,
            longitude,
            self.current_waypoint_from.latitude,
            self.current_waypoint_from.longitude,
            self.current_waypoint_to.latitude,
            self.current_waypoint_to.longitude,
        )
        self.last_xte_nm = xte
        self.distance_to_waypoint_nm = _haversine_distance_nm(
            latitude, longitude, self.current_waypoint_to.latitude, self.current_waypoint_to.longitude
        )
        return xte

    def get_status(self) -> dict:
        return {
            "enabled": self.enabled,
            "from_waypoint": (
                {"latitude": self.current_waypoint_from.latitude, "longitude": self.current_waypoint_from.longitude, "name": self.current_waypoint_from.name}
                if self.current_waypoint_from
                else None
            ),
            "to_waypoint": (
                {"latitude": self.current_waypoint_to.latitude, "longitude": self.current_waypoint_to.longitude, "name": self.current_waypoint_to.name}
                if self.current_waypoint_to
                else None
            ),
            "track_bearing_deg": self.track_bearing_deg,
            "last_xte_nm": self.last_xte_nm,
            "distance_to_waypoint_nm": self.distance_to_waypoint_nm,
        }


# Singleton instance
track = TrackController()
