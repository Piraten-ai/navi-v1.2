"""Autopilot Telemetry Logger

Logs autopilot state (rudder, errors, wind, leeway) to InfluxDB for monitoring and playback.
Background task; config-gated.
"""
from __future__ import annotations

import asyncio
import time
from typing import Optional, Any, Awaitable, Callable

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Optional InfluxDB support
try:
    from influxdb_client import InfluxDBClient
    from influxdb_client.client.write_api import SYNCHRONOUS

    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False


class AutopilotTelemetryLogger:
    def __init__(self) -> None:
        self._client: Optional[Any] = None
        self._write_api: Optional[Any] = None
        self._enabled = False
        self._task: Optional[asyncio.Task] = None
        self._state_provider: Optional[Callable[[], dict[str, Any]]] = None

    def enable(self, state_provider: Callable[[], dict[str, Any]]) -> bool:
        """Start logging.

        Args:
            state_provider: callable that returns autopilot state dict

        Returns:
            True if enabled, False if unavailable
        """
        if not INFLUXDB_AVAILABLE or not settings.INFLUXDB_URL:
            logger.warning("InfluxDB unavailable or not configured; autopilot telemetry logging disabled")
            return False

        try:
            self._client = InfluxDBClient(
                url=settings.INFLUXDB_URL, token=settings.INFLUXDB_TOKEN, org=settings.INFLUXDB_ORG
            )
            self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
            self._state_provider = state_provider
            self._enabled = True
            logger.info(f"Autopilot telemetry logger enabled: {settings.INFLUXDB_URL}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize InfluxDB for autopilot telemetry: {e}")
            return False

    async def start(self, interval_sec: float = 1.0) -> None:
        """Start background logging task."""
        if not self._enabled:
            logger.warning("Autopilot telemetry not enabled")
            return

        self._task = asyncio.create_task(self._run_loop(interval_sec))
        logger.info(f"Autopilot telemetry logging started (interval: {interval_sec}s)")

    async def stop(self) -> None:
        """Stop background logging task."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._client:
            self._client.close()
        logger.info("Autopilot telemetry logging stopped")

    async def _run_loop(self, interval_sec: float) -> None:
        try:
            while True:
                try:
                    if self._state_provider:
                        state = self._state_provider()
                        self._write_telemetry(state)
                    await asyncio.sleep(interval_sec)
                except Exception as e:
                    logger.warning(f"Error writing telemetry: {e}")
                    await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    def _write_telemetry(self, state: dict[str, Any]) -> None:
        """Write autopilot state to InfluxDB."""
        if not self._write_api:
            return

        try:
            timestamp = int(time.time() * 1_000_000_000)  # nanoseconds
            fields = {
                "rudder_deg": float(state.get("rudder_deg", 0.0)),
                "desired_heading_deg": float(state.get("desired_heading_deg", 0.0)),
                "awa_deg": float(state.get("awa_deg", 0.0)),
                "aws_kn": float(state.get("aws_kn", 0.0)),
                "leeway_deg": float(state.get("leeway_deg", 0.0)),
                "xte_nm": float(state.get("xte_nm", 0.0)),
            }
            tags = {
                "module": "autopilot",
                "enabled": str(state.get("enabled", False)),
            }
            line_protocol = self._build_line_protocol("autopilot_state", tags, fields, timestamp)
            self._write_api.write(bucket=settings.INFLUXDB_BUCKET, record=line_protocol)
            logger.debug("Autopilot telemetry written to InfluxDB")
        except Exception as e:
            logger.warning(f"Failed to write autopilot telemetry: {e}")

    @staticmethod
    def _build_line_protocol(measurement: str, tags: dict, fields: dict, timestamp: int) -> str:
        """Build InfluxDB line protocol string."""
        tag_str = ",".join(f"{k}={v}" for k, v in tags.items())
        field_str = ",".join(f"{k}={v}" for k, v in fields.items())
        return f"{measurement},{tag_str} {field_str} {timestamp}"


# Singleton instance
telemetry_logger = AutopilotTelemetryLogger()
