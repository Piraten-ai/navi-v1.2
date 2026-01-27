"""Autopilot PID controller for course keeping based on XTE and heading error.

This module implements a lightweight Autopilot controller that computes a rudder
command (in degrees) from:
- Cross-Track Error (XTE) in nautical miles: lateral offset from desired track
- Heading error in degrees: desired course over ground minus current heading
- Optional wind compensation: use apparent wind angle to bias rudder

NOTE: This module focuses on control math only. It does not integrate with CAN/NMEA.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from app.core.config import settings


@dataclass
class _PID:
    kp: float
    ki: float
    kd: float
    integral: float = 0.0
    last_error: float = 0.0
    last_time: Optional[float] = None

    def reset(self) -> None:
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = None

    def step(self, error: float, dt: Optional[float] = None) -> float:
        now = time.time()
        if dt is None:
            if self.last_time is None:
                dt = 0.0
            else:
                dt = max(0.0, now - self.last_time)
        self.last_time = now

        p = self.kp * error
        self.integral += error * dt
        # anti-windup clamp
        self.integral = max(-100.0, min(100.0, self.integral))
        i = self.ki * self.integral
        d = 0.0
        if dt > 0.0:
            d = self.kd * (error - self.last_error) / dt
        self.last_error = error
        return p + i + d


def _wrap_angle(angle_deg: float) -> float:
    """Wrap angle to [-180, 180)."""
    a = (angle_deg + 180.0) % 360.0 - 180.0
    return a


class AutopilotPID:
    """Compute rudder commands from XTE and heading error.

    Conventions:
    - Positive rudder = starboard, Negative rudder = port
    - Positive heading error = need to turn starboard to reach desired heading
    - Positive XTE means vessel is to starboard of track; command port rudder
    """

    def __init__(self,
                 kp_xte: float | None = None,
                 ki_xte: float | None = None,
                 kd_xte: float | None = None,
                 kp_hdgt: float | None = None,
                 max_rudder_deg: float | None = None,
                 min_rudder_deg: float | None = None,
                 wind_gain: float | None = None,
                 wind_compensation: Optional[bool] = None):
        self.pid_xte = _PID(
            kp=settings.AUTOPILOT_KP_XTE if kp_xte is None else kp_xte,
            ki=settings.AUTOPILOT_KI_XTE if ki_xte is None else ki_xte,
            kd=settings.AUTOPILOT_KD_XTE if kd_xte is None else kd_xte,
        )
        self.kp_hdgt = settings.AUTOPILOT_KP_HDGT if kp_hdgt is None else kp_hdgt
        self.max_rudder = settings.AUTOPILOT_MAX_RUDDER_DEG if max_rudder_deg is None else max_rudder_deg
        self.min_rudder = settings.AUTOPILOT_MIN_RUDDER_DEG if min_rudder_deg is None else min_rudder_deg
        self.wind_gain = settings.AUTOPILOT_WIND_GAIN if wind_gain is None else wind_gain
        self.wind_comp = settings.AUTOPILOT_WIND_COMPENSATION if wind_compensation is None else wind_compensation

    def reset(self) -> None:
        self.pid_xte.reset()

    def compute_rudder(self,
                       xte_nm: float,
                       heading_error_deg: float,
                       apparent_wind_offset_deg: Optional[float] = None,
                       dt: Optional[float] = None) -> float:
        """Compute rudder command from errors.

        Args:
            xte_nm: Cross-track error in nautical miles (+ right of track)
            heading_error_deg: Desired - current heading (deg), wrapped to [-180, 180)
            apparent_wind_offset_deg: Positive if apparent wind from starboard side
            dt: seconds since last call
        Returns:
            Rudder command in degrees, port (-) to starboard (+), clamped and deadbanded.
        """
        # Ensure heading error wrapped
        hdgt_err = _wrap_angle(heading_error_deg)

        # XTE contribution (convert NM to deg via kp, etc.)
        # Positive XTE (starboard of track) → port rudder (negative), so use negative sign
        rudder_xte = - self.pid_xte.step(xte_nm, dt)

        # Heading contribution: positive error → starboard rudder
        rudder_hdgt = self.kp_hdgt * hdgt_err

        # Wind compensation: bias toward luffing into wind slightly
        rudder_wind = 0.0
        if self.wind_comp and apparent_wind_offset_deg is not None:
            # Positive wind offset (wind from starboard) → small starboard rudder to maintain course
            rudder_wind = self.wind_gain * _wrap_angle(apparent_wind_offset_deg)

        cmd = rudder_xte + rudder_hdgt + rudder_wind

        # Deadband: if small magnitude but non-zero, push to min effective
        sign = 1.0 if cmd >= 0 else -1.0
        if abs(cmd) < self.min_rudder:
            cmd = 0.0 if abs(cmd) < (0.5 * self.min_rudder) else sign * self.min_rudder

        # Clamp to limits
        if cmd > self.max_rudder:
            cmd = self.max_rudder
        elif cmd < -self.max_rudder:
            cmd = -self.max_rudder

        return cmd
