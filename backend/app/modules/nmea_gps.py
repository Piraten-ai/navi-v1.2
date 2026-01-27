"""
NMEA GPS Module
===============
Reads and parses NMEA sentences from GPS serial port.
Provides real-time position, speed, heading, and time data.
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import serial
import pynmea2
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class NMEAData:
    """Container for parsed NMEA GPS data."""

    def __init__(self):
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.speed: Optional[float] = None  # Speed in knots
        self.heading: Optional[float] = None  # True heading in degrees
        self.altitude: Optional[float] = None  # Altitude in meters
        self.timestamp: Optional[str] = None
        self.satellites: Optional[int] = None
        self.quality: Optional[str] = None
        self.raw: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "speed": self.speed,
            "heading": self.heading,
            "altitude": self.altitude,
            "timestamp": self.timestamp,
            "satellites": self.satellites,
            "quality": self.quality,
            "raw": self.raw,
        }

    def is_valid(self) -> bool:
        """Check if we have valid position data."""
        return self.latitude is not None and self.longitude is not None


class NMEAGPSModule:
    """NMEA GPS module for reading and parsing GPS data."""

    def __init__(self):
        self.running = False
        self.serial_port: Optional[serial.Serial] = None
        self.current_data = NMEAData()
        self._read_task: Optional[asyncio.Task] = None

        # Mock data state for testing
        self._mock_latitude = 78.2232  # Svalbard
        self._mock_longitude = 15.6267
        self._mock_heading = 45.0
        self._mock_speed = 5.5

    def get_status(self) -> Dict[str, Any]:
        """Get module status."""
        return {
            "module": "nmea_gps",
            "enabled": settings.NMEA_ENABLED,
            "running": self.running,
            "mock_mode": settings.NMEA_MOCK_DATA,
            "serial_port": settings.NMEA_SERIAL_PORT if not settings.NMEA_MOCK_DATA else None,
            "baud_rate": settings.NMEA_BAUD_RATE,
            "has_fix": self.current_data.is_valid(),
            "last_update": self.current_data.timestamp,
        }

    def get_data(self) -> Dict[str, Any]:
        """Get current GPS data."""
        return self.current_data.to_dict()

    async def start(self) -> None:
        """Start reading NMEA data."""
        if self.running:
            logger.warning("NMEA GPS module already running")
            return

        if not settings.NMEA_ENABLED:
            logger.info("NMEA GPS module disabled in configuration")
            return

        self.running = True
        logger.info(
            "Starting NMEA GPS module",
            extra={
                "mock_mode": settings.NMEA_MOCK_DATA,
                "serial_port": settings.NMEA_SERIAL_PORT,
                "baud_rate": settings.NMEA_BAUD_RATE,
            },
        )

        if settings.NMEA_MOCK_DATA:
            self._read_task = asyncio.create_task(self._mock_read_loop())
        else:
            self._read_task = asyncio.create_task(self._serial_read_loop())

    async def stop(self) -> None:
        """Stop reading NMEA data."""
        if not self.running:
            return

        logger.info("Stopping NMEA GPS module")
        self.running = False

        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
            self._read_task = None

        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            logger.info("Serial port closed")

    async def _serial_read_loop(self) -> None:
        """Read NMEA sentences from serial port."""
        try:
            # Open serial port
            self.serial_port = serial.Serial(
                port=settings.NMEA_SERIAL_PORT,
                baudrate=settings.NMEA_BAUD_RATE,
                timeout=settings.NMEA_TIMEOUT,
            )
            logger.info(f"Opened serial port {settings.NMEA_SERIAL_PORT} " f"at {settings.NMEA_BAUD_RATE} baud")

            while self.running:
                try:
                    # Read line from serial port
                    if self.serial_port.in_waiting:
                        line = self.serial_port.readline().decode("ascii", errors="ignore").strip()
                        if line:
                            self._parse_nmea_sentence(line)
                    else:
                        # Small delay to prevent CPU spinning
                        await asyncio.sleep(0.01)

                except serial.SerialException as e:
                    logger.error(f"Serial port error: {e}")
                    await asyncio.sleep(1)  # Wait before retry
                except Exception as e:
                    logger.error(f"Error reading NMEA data: {e}", exc_info=True)
                    await asyncio.sleep(1)

        except serial.SerialException as e:
            logger.error(f"Failed to open serial port {settings.NMEA_SERIAL_PORT}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"NMEA serial read loop error: {e}", exc_info=True)
        finally:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

    async def _mock_read_loop(self) -> None:
        """Generate mock NMEA data for testing."""
        logger.info("Starting mock NMEA data generator")

        while self.running:
            try:
                # Simulate GPS movement
                self._mock_latitude += random.uniform(-0.001, 0.001)
                self._mock_longitude += random.uniform(-0.001, 0.001)
                self._mock_heading = (self._mock_heading + random.uniform(-2, 2)) % 360
                self._mock_speed = max(0, self._mock_speed + random.uniform(-0.5, 0.5))

                # Update current data
                self.current_data.latitude = self._mock_latitude
                self.current_data.longitude = self._mock_longitude
                self.current_data.speed = self._mock_speed
                self.current_data.heading = self._mock_heading
                self.current_data.altitude = 5.0
                self.current_data.timestamp = datetime.now(timezone.utc).isoformat()
                self.current_data.satellites = random.randint(8, 12)
                self.current_data.quality = "good"
                # Generate mock NMEA sentence (without checksum for simplicity)
                self.current_data.raw = (
                    f"$GPRMC,{datetime.now(timezone.utc).strftime('%H%M%S')},A,"
                    f"{abs(self._mock_latitude):.4f},{'N' if self._mock_latitude >= 0 else 'S'},"
                    f"{abs(self._mock_longitude):.4f},{'E' if self._mock_longitude >= 0 else 'W'},"
                    f"{self._mock_speed:.1f},{self._mock_heading:.1f},"
                    f"{datetime.now(timezone.utc).strftime('%d%m%y')},,,"
                )

                logger.debug(
                    "Generated mock NMEA data",
                    extra={
                        "lat": self._mock_latitude,
                        "lon": self._mock_longitude,
                        "speed": self._mock_speed,
                        "heading": self._mock_heading,
                    },
                )

                # Wait before next update
                await asyncio.sleep(settings.NMEA_UPDATE_INTERVAL)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in mock NMEA generator: {e}", exc_info=True)
                await asyncio.sleep(1)

    def _parse_nmea_sentence(self, sentence: str) -> None:
        """Parse a single NMEA sentence and update current data."""
        try:
            self.current_data.raw = sentence

            # Parse the sentence
            msg = pynmea2.parse(sentence)

            # Update data based on sentence type
            if isinstance(msg, pynmea2.types.talker.GGA):
                # GPS Fix Data
                if msg.latitude is not None and msg.longitude is not None:
                    self.current_data.latitude = msg.latitude
                    self.current_data.longitude = msg.longitude
                    self.current_data.altitude = msg.altitude if msg.altitude is not None else None
                    # Parse satellite count safely
                    try:
                        if hasattr(msg, "num_sats") and msg.num_sats is not None:
                            self.current_data.satellites = int(msg.num_sats)
                    except (ValueError, AttributeError):
                        self.current_data.satellites = None

                    # Quality indicator
                    if hasattr(msg, "gps_qual"):
                        quality_map = {0: "invalid", 1: "gps_fix", 2: "dgps_fix"}
                        self.current_data.quality = quality_map.get(msg.gps_qual, "unknown")

                    self.current_data.timestamp = datetime.now(timezone.utc).isoformat()

                    logger.debug(
                        "Parsed GGA sentence",
                        extra={
                            "lat": self.current_data.latitude,
                            "lon": self.current_data.longitude,
                            "satellites": self.current_data.satellites,
                        },
                    )

            elif isinstance(msg, pynmea2.types.talker.RMC):
                # Recommended Minimum Navigation Information
                if msg.latitude is not None and msg.longitude is not None:
                    self.current_data.latitude = msg.latitude
                    self.current_data.longitude = msg.longitude

                if hasattr(msg, "spd_over_grnd") and msg.spd_over_grnd is not None:
                    self.current_data.speed = float(msg.spd_over_grnd)

                if hasattr(msg, "true_course") and msg.true_course is not None:
                    self.current_data.heading = float(msg.true_course)

                self.current_data.timestamp = datetime.now(timezone.utc).isoformat()

                logger.debug(
                    "Parsed RMC sentence",
                    extra={
                        "lat": self.current_data.latitude,
                        "lon": self.current_data.longitude,
                        "speed": self.current_data.speed,
                        "heading": self.current_data.heading,
                    },
                )

            elif isinstance(msg, pynmea2.types.talker.VTG):
                # Track Made Good and Ground Speed
                if hasattr(msg, "true_track") and msg.true_track is not None:
                    self.current_data.heading = float(msg.true_track)

                if hasattr(msg, "spd_over_grnd_kts") and msg.spd_over_grnd_kts is not None:
                    self.current_data.speed = float(msg.spd_over_grnd_kts)

                logger.debug(
                    "Parsed VTG sentence",
                    extra={
                        "speed": self.current_data.speed,
                        "heading": self.current_data.heading,
                    },
                )

            elif isinstance(msg, pynmea2.types.talker.HDT):
                # Heading True
                if hasattr(msg, "heading") and msg.heading is not None:
                    self.current_data.heading = float(msg.heading)

                logger.debug("Parsed HDT sentence", extra={"heading": self.current_data.heading})

        except pynmea2.ParseError as e:
            logger.warning(f"Failed to parse NMEA sentence: {e}")
        except Exception as e:
            logger.error(f"Error parsing NMEA sentence: {e}", exc_info=True)


# Global instance
nmea_gps = NMEAGPSModule()
