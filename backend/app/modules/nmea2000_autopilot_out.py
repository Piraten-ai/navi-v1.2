"""NMEA2000 Autopilot Output

Encodes rudder angle and heading setpoint commands as NMEA2000 PGNs for transmission
over a CAN bus. Designed to integrate with the autopilot controller as an optional output
sink. Gracefully degrades when python-can is unavailable.

PGNs:
- 127245 (Rudder): angle in radians
- 127250 (Vessel Heading): true heading in radians, plus rates
"""
from __future__ import annotations

import math
import time
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Optional python-can support
try:
    import can
    CAN_AVAILABLE = True
except ImportError:
    CAN_AVAILABLE = False


class NMEA2000RudderCommand:
    """Encodes PGN 127245 (Rudder) for CAN transmission."""

    # PGN 127245: Rudder
    PGN = 127245
    PRIORITY = 3
    PDU_FORMAT = 0xF1  # PDU Format for 127245

    @staticmethod
    def encode(rudder_deg: float) -> bytes:
        """Encode rudder command to PGN 127245 payload.

        Args:
            rudder_deg: Rudder angle in degrees (-45 to +45 typical)

        Returns:
            7-byte payload
        """
        # Convert degrees to radians (-π to +π radians ≈ -180 to +180 deg)
        rudder_rad = math.radians(rudder_deg)
        # Clamp to reasonable range for encoding
        rudder_rad = max(-math.pi, min(math.pi, rudder_rad))

        payload = bytearray(7)
        # Byte 0-1: Rudder angle (int16, 1/32768 rad resolution)
        rudder_raw = int(rudder_rad * 32768 / math.pi)
        payload[0] = rudder_raw & 0xFF
        payload[1] = (rudder_raw >> 8) & 0xFF
        # Remaining bytes reserved/unused
        payload[2:] = [0xFF] * 5

        return bytes(payload)


class NMEA2000HeadingCommand:
    """Encodes PGN 127250 (Vessel Heading) for CAN transmission (simplified)."""

    # PGN 127250: Vessel Heading
    PGN = 127250
    PRIORITY = 3
    PDU_FORMAT = 0xF2

    @staticmethod
    def encode(heading_deg: float, rate_deg_s: float = 0.0) -> bytes:
        """Encode heading setpoint to PGN 127250 payload (simplified).

        This is a placeholder; actual PGN 127250 encoding is complex and varies by device.

        Args:
            heading_deg: True heading in degrees (0-360)
            rate_deg_s: Rate of change in deg/s (typically small)

        Returns:
            8-byte payload
        """
        # Normalize heading to [0, 360)
        heading_deg = heading_deg % 360.0
        # Convert to radians
        heading_rad = math.radians(heading_deg)
        # Clamp rate to reasonable range
        rate_rad_s = math.radians(max(-5.0, min(5.0, rate_deg_s)))

        payload = bytearray(8)
        # Byte 0-1: Heading (uint16, 1/32768 rad resolution)
        heading_raw = int(heading_rad * 32768 / math.pi) & 0xFFFF
        payload[0] = heading_raw & 0xFF
        payload[1] = (heading_raw >> 8) & 0xFF
        # Byte 2-3: Rate (int16 rad/s, 1/128 resolution)
        rate_raw = int(rate_rad_s * 128) & 0xFFFF
        payload[2] = rate_raw & 0xFF
        payload[3] = (rate_raw >> 8) & 0xFF
        # Remaining bytes reserved/unused
        payload[4:] = [0xFF] * 4

        return bytes(payload)


class NMEA2000AutopilotOutput:
    """Sends rudder and heading commands over CAN bus as NMEA2000 PGNs."""

    def __init__(self, interface: str = "can0", bitrate: int = 250000) -> None:
        self.interface = interface
        self.bitrate = bitrate
        self.bus: Optional[Any] = None
        self._last_rudder_deg: Optional[float] = None
        self._last_heading_deg: Optional[float] = None

    def connect(self) -> bool:
        """Establish CAN connection.

        Returns:
            True if connected, False if unavailable or failed.
        """
        if not CAN_AVAILABLE:
            logger.warning("python-can unavailable; NMEA2000 autopilot output disabled")
            return False

        try:
            self.bus = can.interface.Bus(self.interface, bitrate=self.bitrate, bustype="socketcan")
            logger.info(f"NMEA2000 CAN bus connected: {self.interface} @ {self.bitrate} bps")
            return True
        except Exception as e:
            logger.error(f"Failed to connect CAN bus: {e}")
            return False

    def disconnect(self) -> None:
        """Close CAN connection."""
        if self.bus:
            try:
                self.bus.shutdown()
            except Exception:
                pass
            self.bus = None

    def send_rudder(self, rudder_deg: float) -> bool:
        """Send rudder command via CAN.

        Args:
            rudder_deg: Rudder angle in degrees

        Returns:
            True if sent, False if failed or unavailable.
        """
        if not self.bus:
            return False

        try:
            payload = NMEA2000RudderCommand.encode(rudder_deg)
            # CAN ID for PGN 127245: format depends on NMEA2000 implementation
            # Simplified: use standard extended ID format
            can_id = (NMEA2000RudderCommand.PRIORITY << 26) | NMEA2000RudderCommand.PGN
            msg = can.Message(arbitration_id=can_id, data=payload, is_extended_id=True)
            self.bus.send(msg)
            self._last_rudder_deg = rudder_deg
            logger.debug(f"Sent rudder command: {rudder_deg:.1f}° via PGN 127245")
            return True
        except Exception as e:
            logger.warning(f"Failed to send rudder command: {e}")
            return False

    def send_heading(self, heading_deg: float, rate_deg_s: float = 0.0) -> bool:
        """Send heading setpoint via CAN.

        Args:
            heading_deg: True heading in degrees
            rate_deg_s: Rate of change in deg/s

        Returns:
            True if sent, False if failed or unavailable.
        """
        if not self.bus:
            return False

        try:
            payload = NMEA2000HeadingCommand.encode(heading_deg, rate_deg_s)
            can_id = (NMEA2000HeadingCommand.PRIORITY << 26) | NMEA2000HeadingCommand.PGN
            msg = can.Message(arbitration_id=can_id, data=payload, is_extended_id=True)
            self.bus.send(msg)
            self._last_heading_deg = heading_deg
            logger.debug(f"Sent heading command: {heading_deg:.1f}° via PGN 127250")
            return True
        except Exception as e:
            logger.warning(f"Failed to send heading command: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get output module status."""
        return {
            "connected": self.bus is not None,
            "interface": self.interface,
            "bitrate": self.bitrate,
            "last_rudder_deg": self._last_rudder_deg,
            "last_heading_deg": self._last_heading_deg,
            "can_available": CAN_AVAILABLE,
        }


# Singleton instance (can be configured during autopilot setup)
nmea2000_autopilot = NMEA2000AutopilotOutput(interface=settings.NMEA2000_INTERFACE)
