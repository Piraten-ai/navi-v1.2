"""NMEA 0183 Autopilot Output

Encodes navigation data as NMEA 0183 sentences ($GPAPB) to control the boat's
autopilot. This allows AADS to act as a navigator/chartplotter that the
main autopilot can follow in 'Track' or 'Nav' mode.
"""
from __future__ import annotations

import time
import serial
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class NMEA0183AutopilotOutput:
    """Sends steering commands over Serial as NMEA 0183 sentences."""

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 4800) -> None:
        self.port = port
        self.baudrate = baudrate
        self.ser: Optional[serial.Serial] = None
        self._last_heading_deg: Optional[float] = None

    def connect(self) -> bool:
        """Establish serial connection."""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            logger.info(f"NMEA 0183 serial output connected: {self.port} @ {self.baudrate} bps")
            return True
        except Exception as e:
            logger.error(f"Failed to connect NMEA 0183 serial: {e}")
            return False

    def disconnect(self) -> None:
        """Close serial connection."""
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None

    def _calculate_checksum(self, sentence: str) -> str:
        """Calculate NMEA checksum."""
        checksum = 0
        for char in sentence[1:]:  # Skip leading $
            checksum ^= ord(char)
        return f"{checksum:02X}"

    def send_steering(self, desired_heading_deg: float, xte_nm: float = 0.0) -> bool:
        """Send $GPAPB (Autopilot Sentence 'B') via Serial.

        Args:
            desired_heading_deg: Desired heading in degrees
            xte_nm: Cross-track error in nautical miles

        Returns:
            True if sent, False if failed.
        """
        if not self.ser or not self.ser.is_open:
            return False

        try:
            # $GPAPB,A,A,x.x,a,N,A,A,x.x,a,c--c,x.x,a,x.x,a*hh
            # Simplified APB for heading hold
            status_a = "A"  # Data valid
            cycle_a = "A"   # Cycle lock
            xte = f"{abs(xte_nm):.3f}"
            steer_dir = "L" if xte_nm > 0 else "R"
            units = "N"     # NM
            arrival = "V"   # Not arrived
            bearing_origin_to_dest = f"{desired_heading_deg:.1f}"
            mag_true = "T"
            dest_wp_id = "AADS"
            bearing_pos_to_dest = f"{desired_heading_deg:.1f}"
            
            sentence = f"$GPAPB,{status_a},{cycle_a},{xte},{steer_dir},{units},{arrival},{arrival},{bearing_origin_to_dest},{mag_true},{dest_wp_id},{bearing_pos_to_dest},{mag_true},{desired_heading_deg:.1f},{mag_true}"
            checksum = self._calculate_checksum(sentence)
            full_sentence = f"{sentence}*{checksum}\r\n"
            
            self.ser.write(full_sentence.encode("ascii"))
            self._last_heading_deg = desired_heading_deg
            logger.debug(f"Sent NMEA 0183 APB: {full_sentence.strip()}")
            return True
        except Exception as e:
            logger.warning(f"Failed to send NMEA 0183 sentence: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            "connected": self.ser is not None and self.ser.is_open,
            "port": self.port,
            "baudrate": self.baudrate,
            "last_heading_deg": self._last_heading_deg,
        }

# Singleton instance
nmea0183_autopilot = NMEA0183AutopilotOutput(
    port=getattr(settings, "NMEA0183_OUTPUT_PORT", "/dev/ttyUSB0"),
    baudrate=getattr(settings, "NMEA0183_OUTPUT_BAUD", 4800)
)
