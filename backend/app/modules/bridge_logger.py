"""Bridge telemetry logger for Arduino analog signals."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping

from app.core.config import settings
from app.core.logging import get_logger

try:
    from influxdb_client import InfluxDBClient
    from influxdb_client.client.write_api import SYNCHRONOUS

    INFLUXDB_AVAILABLE = True
except Exception:  # pragma: no cover
    INFLUXDB_AVAILABLE = False


logger = get_logger(__name__)


class BridgeLogger:
    """Writes bridge signals to InfluxDB when configured."""

    def __init__(self) -> None:
        self._client = None
        self._write_api = None
        self._enabled = False

    def enable(self) -> bool:
        if not INFLUXDB_AVAILABLE or not settings.INFLUXDB_URL:
            logger.warning("InfluxDB unavailable or not configured; bridge logging disabled")
            return False
        if not settings.INFLUXDB_TOKEN:
            logger.warning("InfluxDB token missing; bridge logging disabled")
            return False

        try:
            self._client = InfluxDBClient(
                url=settings.INFLUXDB_URL,
                token=settings.INFLUXDB_TOKEN,
                org=settings.INFLUXDB_ORG,
            )
            self._write_api = self._client.write_api(write_options=SYNCHRONOUS)
            self._enabled = True
            logger.info(f"Bridge logger enabled: {settings.INFLUXDB_URL}")
            return True
        except Exception as exc:
            logger.error(f"Failed to initialize bridge logger: {exc}")
            self._enabled = False
            return False

    def write(self, signals: Mapping[str, float | int], source: str, ts: str | None = None) -> None:
        if not self._enabled or not self._write_api:
            return

        timestamp = ts or datetime.now(timezone.utc).isoformat()
        fields = []
        for key, value in signals.items():
            if isinstance(value, int):
                fields.append(f"{key}={value}i")
            else:
                fields.append(f"{key}={value}")

        if not fields:
            return

        line = f"bridge_analog,source={source} " + ",".join(fields) + f" {int(datetime.fromisoformat(timestamp).timestamp() * 1_000_000_000)}"
        try:
            self._write_api.write(bucket=settings.INFLUXDB_BUCKET, record=line)
        except Exception as exc:
            logger.warning(f"Bridge logger write failed: {exc}")

    def close(self) -> None:
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
