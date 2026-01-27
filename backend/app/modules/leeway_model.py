"""Leeway (sideforce) modeling.

Provides a small, dependency-free function to estimate signed leeway angle (deg)
from wind and boat conditions. Designed for unit testing and later integration.

Conventions
- rel_wind_deg: apparent wind angle relative to bow, degrees in [-180, 180]
  with starboard positive and port negative (common marine convention).
- Return value: signed leeway (deg). Positive sign corresponds to the sign of
  the sine of rel_wind_deg (i.e., opposite sides for +/- angles), ensuring
  estimate(+theta) == -estimate(-theta).

Model (method="simple")
- Magnitude grows with wind speed and with lateral wind component ~ |sin(AWA)|
- Magnitude decreases with boat speed (more way reduces drift)
- |leeway| = min( K * (wind^2 / max(boat_speed, eps)) * |sin(rel)|, max_deg )
- Sign = sign(sin(rel))

Notes
- All inputs are in knots and degrees.
- Method and parameters default to settings if not provided explicitly.
"""

from __future__ import annotations

import math
from typing import Optional

from ..core.config import settings


def _normalize_rel_wind_deg(angle: float) -> float:
    a = ((angle + 180.0) % 360.0) - 180.0
    # Map -180 to +180 for stability (sin(-180) == sin(180) == 0)
    if a <= -180.0:
        a = 180.0
    return a


def estimate_leeway(
    wind_speed_kn: float,
    boat_speed_kn: float,
    rel_wind_deg: float,
    *,
    method: Optional[str] = None,
    k: Optional[float] = None,
    max_deg: Optional[float] = None,
) -> float:
    """Estimate signed leeway angle (degrees).

    Parameters
    - wind_speed_kn: true/apparent wind speed over water (knots)
    - boat_speed_kn: boat speed through water (knots)
    - rel_wind_deg: apparent wind angle relative to bow (deg), starboard +
    - method: optional override ("simple" or future variants)
    - k: scaling coefficient override (defaults to settings.LEWAY_K)
    - max_deg: clamp limit override (defaults to settings.LEWAY_MAX_DEG)
    """
    m = (method or settings.LEWAY_METHOD).lower()
    K = settings.LEWAY_K if k is None else float(k)
    max_abs = settings.LEWAY_MAX_DEG if max_deg is None else float(max_deg)

    # Guard rails
    ws = max(0.0, float(wind_speed_kn))
    bs = max(0.0, float(boat_speed_kn))
    rel = _normalize_rel_wind_deg(float(rel_wind_deg))

    if m == "simple":
        # Component lateral to the hull ~ sin(rel)
        s = math.sin(math.radians(rel))
        # Quadratic in wind, inverse linear in boat speed
        eps = 0.1  # to avoid division by zero; roughly 0.1 kn
        magnitude = K * (ws * ws) / max(bs, eps) * abs(s)
        value = math.copysign(magnitude, s)
        # Clamp to maximum absolute leeway
        if value > max_abs:
            return max_abs
        if value < -max_abs:
            return -max_abs
        return value

    # Future: "visir2" or other empirical variants
    raise ValueError(f"Unsupported leeway method: {m}")
