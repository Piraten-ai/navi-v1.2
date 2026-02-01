"""Autopilot Controller

Coordinates sensor inputs (Signal K), wind smoothing, leeway modeling, and the
AutopilotPID to produce rudder commands. Runs as an optional background task,
config-gated, with simple setpoint management (heading hold).

This module does not write to hardware directly; a pluggable sink can be
provided to forward rudder commands to CAN/NMEA2000 or other outputs.
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Callable, Optional, Awaitable, Dict, Any

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.autopilot_pid import AutopilotPID
from app.modules.wind_estimator import WindEstimator
from app.modules.leeway_model import estimate_leeway

logger = get_logger(__name__)


def _wrap_angle(angle_deg: float) -> float:
    a = (angle_deg + 180.0) % 360.0 - 180.0
    return a


@dataclass
class AutopilotState:
    enabled: bool = False
    mode: str = "standby"  # standby, compass, wind, gps
    desired_heading_deg: Optional[float] = None
    last_rudder_deg: float = 0.0
    last_update_ts: float = 0.0
    last_awa_deg: Optional[float] = None
    last_aws_kn: Optional[float] = None
    last_leeway_deg: Optional[float] = None


class AutopilotController:
    def __init__(self) -> None:
        self.state = AutopilotState()
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._pid = AutopilotPID()
        self._wind: Optional[WindEstimator] = None
        if settings.WIND_ESTIMATOR_ENABLED:
            self._wind = WindEstimator()
        self._broadcast: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
        self._output_sinks: list[Callable[[float], Awaitable[None] | None]] = []
        self._signalk_provider: Optional[Callable[[], Dict[str, Any]]] = None
        self._last_step_time: Optional[float] = None

    def configure(
        self,
        *,
        signalk_provider: Callable[[], Dict[str, Any]],
        broadcast: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        output_sinks: Optional[list[Callable[[float], Awaitable[None] | None]]] = None,
    ) -> None:
        self._signalk_provider = signalk_provider
        self._broadcast = broadcast
        self._output_sinks = output_sinks or []

    async def start(self) -> None:
        if self._task and not self._task.done():
            logger.warning("AutopilotController already running")
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_loop())
        logger.info("AutopilotController started", extra={"interval": settings.AUTOPILOT_UPDATE_INTERVAL})

    async def stop(self) -> None:
        if not self._task:
            return
        self._stop_event.set()
        self.state.enabled = False
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None
        logger.info("AutopilotController stopped")

    def enable(self, desired_heading_deg: Optional[float] = None) -> None:
        self.state.enabled = True
        if self.state.mode == "standby":
            self.state.mode = "compass"  # Auto-switch to compass mode when enabling
        if desired_heading_deg is not None:
            self.state.desired_heading_deg = desired_heading_deg % 360.0
        self._pid.reset()
        self._last_step_time = None
        logger.info("Autopilot enabled", extra={"desired_heading": self.state.desired_heading_deg, "mode": self.state.mode})

    def disable(self) -> None:
        self.state.enabled = False
        self.state.mode = "standby"
        self.state.last_rudder_deg = 0.0
        logger.info("Autopilot disabled")

    def set_mode(self, mode: str) -> None:
        """Set autopilot mode: standby, compass, wind, gps"""
        valid_modes = ["standby", "compass", "wind", "gps"]
        if mode not in valid_modes:
            logger.warning(f"Invalid autopilot mode: {mode}")
            return
        
        old_mode = self.state.mode
        self.state.mode = mode
        
        if mode == "standby":
            self.state.enabled = False
            self.state.last_rudder_deg = 0.0
        else:
            self.state.enabled = True
            self._pid.reset()
            self._last_step_time = None
        
        logger.info(f"Autopilot mode changed", extra={"old_mode": old_mode, "new_mode": mode})

    def set_heading(self, heading_deg: float) -> None:
        self.state.desired_heading_deg = heading_deg % 360.0
        logger.info("Autopilot desired heading updated", extra={"desired_heading": self.state.desired_heading_deg})

    def adjust_heading(self, delta_deg: float) -> None:
        """Adjust heading by delta degrees (for ±1°, ±10° buttons)"""
        if self.state.desired_heading_deg is not None:
            self.state.desired_heading_deg = (self.state.desired_heading_deg + delta_deg) % 360.0
            logger.info("Autopilot heading adjusted", extra={"delta": delta_deg, "new_heading": self.state.desired_heading_deg})

    def tack(self, side: str) -> None:
        """Execute tack: shift heading by ~100 degrees"""
        if self.state.desired_heading_deg is not None:
            # Shift by 100 degrees to ensure crossing the wind
            delta = 100.0 if side.lower() == "starboard" else -100.0
            self.state.desired_heading_deg = (self.state.desired_heading_deg + delta) % 360.0
            logger.info(f"Tack initiated to {side}", extra={"delta": delta, "new_heading": self.state.desired_heading_deg})

    def gybe(self, side: str) -> None:
        """Execute gybe: shift heading by ~140 degrees"""
        if self.state.desired_heading_deg is not None:
            # Shift by 140 degrees for a deep gybe
            delta = 140.0 if side.lower() == "starboard" else -140.0
            self.state.desired_heading_deg = (self.state.desired_heading_deg + delta) % 360.0
            logger.info(f"Gybe initiated to {side}", extra={"delta": delta, "new_heading": self.state.desired_heading_deg})

    def emergency_stop(self) -> None:
        """Emergency stop - center rudder and standby"""
        self.state.enabled = False
        self.state.mode = "standby"
        self.state.last_rudder_deg = 0.0
        self._pid.reset()
        logger.warning("EMERGENCY STOP activated")

    def get_status(self) -> Dict[str, Any]:
        return {
            "enabled": self.state.enabled,
            "mode": self.state.mode,
            "desired_heading_deg": self.state.desired_heading_deg,
            "last_rudder_deg": self.state.last_rudder_deg,
            "last_update_ts": self.state.last_update_ts,
            "last_awa_deg": self.state.last_awa_deg,
            "last_aws_kn": self.state.last_aws_kn,
            "last_leeway_deg": self.state.last_leeway_deg,
        }

    async def _run_loop(self) -> None:
        try:
            while not self._stop_event.is_set():
                try:
                    await self._step_once()
                except Exception as e:
                    logger.error(f"Autopilot step error: {e}", exc_info=True)
                await asyncio.sleep(settings.AUTOPILOT_UPDATE_INTERVAL)
        except asyncio.CancelledError:
            pass

    async def _emit(self, rudder_deg: float) -> None:
        self.state.last_rudder_deg = rudder_deg
        self.state.last_update_ts = time.time()
        msg = {
            "type": "autopilot",
            "data": {
                "rudder_deg": rudder_deg,
                "enabled": self.state.enabled,
                "desired_heading_deg": self.state.desired_heading_deg,
                "awa_deg": self.state.last_awa_deg,
                "aws_kn": self.state.last_aws_kn,
                "leeway_deg": self.state.last_leeway_deg,
                "timestamp": self.state.last_update_ts,
            },
        }
        if self._broadcast:
            try:
                await self._broadcast(msg)
            except Exception:
                logger.debug("Broadcast failed (autopilot)")
        
        for sink in self._output_sinks:
            try:
                r = sink(rudder_deg)
                if asyncio.iscoroutine(r):
                    await r
            except Exception as e:
                logger.warning(f"Output sink failed: {e}")

    async def _step_once(self) -> None:
        if not self.state.enabled or not self._signalk_provider:
            return
        data = self._signalk_provider()
        nav = data.get("navigation", {})
        env = data.get("environment", {})

        heading = nav.get("heading")
        lat = nav.get("latitude")
        lon = nav.get("longitude")
        stw_kn = nav.get("speed_through_water")
        wind_dir_true = env.get("wind_direction")
        wind_speed_ms = env.get("wind_speed")
        if heading is None or wind_dir_true is None or wind_speed_ms is None or stw_kn is None:
            # insufficient data
            return

        awa_deg = _wrap_angle(wind_dir_true - heading)  # using true wind as proxy
        aws_kn = max(0.0, float(wind_speed_ms)) * 1.94384
        self.state.last_awa_deg = awa_deg
        self.state.last_aws_kn = aws_kn

        # Smooth wind if enabled
        if self._wind:
            self._wind.add_sample(awa_deg=awa_deg, aws_kn=aws_kn)
            wstate = self._wind.get_state()
            awa_deg = wstate.get("awa_deg", awa_deg)
            aws_kn = wstate.get("aws_kn", aws_kn)
            self.state.last_awa_deg = awa_deg
            self.state.last_aws_kn = aws_kn

        # Leeway estimate (optional)
        leeway_deg = 0.0
        if settings.LEWAY_ENABLED:
            try:
                leeway_deg = estimate_leeway(
                    wind_speed_kn=aws_kn,
                    boat_speed_kn=max(0.1, float(stw_kn)),
                    rel_wind_deg=awa_deg,
                )
            except Exception as e:
                logger.debug(f"Leeway estimate failed: {e}")
                leeway_deg = 0.0
        self.state.last_leeway_deg = leeway_deg

        # Compute XTE if track control enabled
        xte_nm = 0.0
        if lat is not None and lon is not None:
            try:
                from app.modules.track_control import track
                xte_nm = track.compute_xte(lat, lon)
            except Exception as e:
                logger.debug(f"XTE computation failed: {e}")

        # Check emergency conditions and override if needed
        from app.modules.emergency_behaviors import emergency
        override_rudder = emergency.state.override_rudder_deg

        # Errors
        desired = self.state.desired_heading_deg
        hdg_err = _wrap_angle((desired - heading) if desired is not None else 0.0)
        # Apply leeway as bias to heading error (steer into the wind)
        hdg_err_eff = _wrap_angle(hdg_err + leeway_deg)

        now = time.time()
        dt = None if self._last_step_time is None else max(0.0, now - self._last_step_time)
        self._last_step_time = now

        if override_rudder is not None:
            # Emergency override active
            rudder = override_rudder
        else:
            # Normal PID computation
            rudder = self._pid.compute_rudder(
                xte_nm=xte_nm,
                heading_error_deg=hdg_err_eff,
                apparent_wind_offset_deg=awa_deg,
                dt=dt,
            )

        await self._emit(rudder)


# Singleton instance
autopilot = AutopilotController()
