"""NMEA2000 GPS module for reading GPS data via CAN bus.

This module implements NMEA2000 protocol support for reading GPS position data
from a CAN bus interface. It supports the following PGNs:
- PGN 129025: Position, Rapid Update (latitude/longitude)
- PGN 129029: GNSS Position Data (full GNSS info with quality indicators)

Requirements:
- python-can library for CAN bus communication
- SocketCAN interface (Linux) or virtual CAN for testing
"""

from __future__ import annotations

import asyncio
import logging
import struct
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

try:
    import can
    CAN_AVAILABLE = True
except ImportError:
    CAN_AVAILABLE = False
    logging.warning("python-can not installed, NMEA2000 GPS will be unavailable")

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class NMEA2000Position:
    """NMEA2000 GPS position data."""
    
    latitude: Optional[float] = None  # Degrees, positive = North
    longitude: Optional[float] = None  # Degrees, positive = East
    altitude: Optional[float] = None  # Meters above sea level
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # PGN 129029 additional fields
    gnss_method: Optional[str] = None  # "GPS", "GLONASS", "GPS+GLONASS", etc.
    gnss_integrity: Optional[str] = None  # "No integrity checking", "Safe", "Caution"
    number_of_svs: Optional[int] = None  # Number of satellites
    hdop: Optional[float] = None  # Horizontal dilution of precision
    pdop: Optional[float] = None  # Position dilution of precision
    geoidal_separation: Optional[float] = None  # Meters
    reference_stations: Optional[int] = None  # Number of reference stations
    
    def is_valid(self) -> bool:
        """Check if position has minimum valid data."""
        return (
            self.latitude is not None 
            and self.longitude is not None
            and -90 <= self.latitude <= 90
            and -180 <= self.longitude <= 180
        )


class NMEA2000GPS:
    """NMEA2000 GPS data reader using CAN bus."""
    
    # PGN definitions
    PGN_POSITION_RAPID = 129025
    PGN_GNSS_POSITION = 129029
    
    def __init__(self):
        """Initialize NMEA2000 GPS reader."""
        self.bus: Optional[can.Bus] = None
        self.position = NMEA2000Position()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        if not CAN_AVAILABLE:
            logger.error("python-can library not available, NMEA2000 GPS disabled")
    
    async def start(self) -> None:
        """Start reading NMEA2000 GPS data from CAN bus."""
        if not settings.NMEA2000_ENABLED:
            logger.info("NMEA2000 GPS disabled in config")
            return
        
        if not CAN_AVAILABLE:
            logger.error("Cannot start NMEA2000 GPS: python-can not installed")
            return
        
        try:
            # Initialize CAN bus interface
            self.bus = can.Bus(
                interface='socketcan',
                channel=settings.NMEA2000_INTERFACE,
                receive_own_messages=False
            )
            logger.info(f"NMEA2000 GPS started on {settings.NMEA2000_INTERFACE}")
            
            self._running = True
            self._task = asyncio.create_task(self._read_loop())
            
        except Exception as e:
            logger.error(f"Failed to start NMEA2000 GPS: {e}")
            self.bus = None
    
    async def stop(self) -> None:
        """Stop reading NMEA2000 GPS data."""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        if self.bus:
            self.bus.shutdown()
            self.bus = None
        
        logger.info("NMEA2000 GPS stopped")
    
    async def _read_loop(self) -> None:
        """Main loop for reading CAN messages."""
        if not self.bus:
            return
        
        logger.info("NMEA2000 GPS read loop started")
        
        while self._running:
            try:
                # Non-blocking read with timeout
                msg = self.bus.recv(timeout=settings.NMEA2000_TIMEOUT)
                
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue
                
                # Extract PGN from CAN ID (29-bit extended format)
                # For NMEA2000: PGN is in bits 8-25 of the CAN ID
                pgn = (msg.arbitration_id >> 8) & 0x1FFFF
                
                # Handle supported PGNs
                if pgn == self.PGN_POSITION_RAPID and settings.NMEA2000_GPS_PGN_129025_ENABLED:
                    self._handle_pgn_129025(msg)
                elif pgn == self.PGN_GNSS_POSITION and settings.NMEA2000_GPS_PGN_129029_ENABLED:
                    self._handle_pgn_129029(msg)
                elif settings.NMEA2000_LOG_UNKNOWN_PGNS:
                    logger.debug(f"Unknown PGN {pgn}: {msg.data.hex()}")
                
                # Yield to event loop
                await asyncio.sleep(0)
                
            except can.CanError as e:
                logger.error(f"CAN bus error: {e}")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error reading NMEA2000 data: {e}")
                await asyncio.sleep(1)
    
    def _handle_pgn_129025(self, msg: can.Message) -> None:
        """Handle PGN 129025 - Position, Rapid Update.
        
        Format (8 bytes):
        - Latitude: int32 (1e-7 degrees)
        - Longitude: int32 (1e-7 degrees)
        """
        if len(msg.data) < 8:
            logger.warning(f"PGN 129025: Invalid data length {len(msg.data)}")
            return
        
        try:
            # Parse latitude (bytes 0-3) and longitude (bytes 4-7)
            lat_raw = struct.unpack('<i', msg.data[0:4])[0]
            lon_raw = struct.unpack('<i', msg.data[4:8])[0]
            
            # Convert from 1e-7 degrees to degrees
            # Check for invalid data (0x7FFFFFFF)
            if lat_raw != 0x7FFFFFFF:
                self.position.latitude = lat_raw * 1e-7
            
            if lon_raw != 0x7FFFFFFF:
                self.position.longitude = lon_raw * 1e-7
            
            self.position.timestamp = datetime.utcnow()
            
            logger.debug(
                f"PGN 129025: lat={self.position.latitude:.6f}, "
                f"lon={self.position.longitude:.6f}"
            )
            
        except Exception as e:
            logger.error(f"Error parsing PGN 129025: {e}")
    
    def _handle_pgn_129029(self, msg: can.Message) -> None:
        """Handle PGN 129029 - GNSS Position Data.
        
        Format (variable length, typically 51 bytes):
        - SID: uint8
        - Date: uint16 (days since 1970-01-01)
        - Time: uint32 (seconds since midnight * 0.0001)
        - Latitude: int64 (1e-16 degrees)
        - Longitude: int64 (1e-16 degrees)
        - Altitude: int64 (1e-6 meters)
        - GNSS type: enumeration
        - Method: enumeration
        - Integrity: enumeration
        - Number of SVs: uint8
        - HDOP: uint16 (0.01)
        - PDOP: uint16 (0.01)
        - Geoidal separation: int32 (0.01 meters)
        - Reference stations: uint8
        - ... (additional fields)
        """
        if len(msg.data) < 43:
            logger.warning(f"PGN 129029: Invalid data length {len(msg.data)}")
            return
        
        try:
            # Parse key fields (simplified - full spec has more)
            offset = 0
            
            # Skip SID (1 byte)
            offset += 1
            
            # Skip Date and Time (6 bytes total)
            offset += 6
            
            # Parse latitude (8 bytes) and longitude (8 bytes)
            lat_raw = struct.unpack('<q', msg.data[offset:offset+8])[0]
            offset += 8
            lon_raw = struct.unpack('<q', msg.data[offset:offset+8])[0]
            offset += 8
            
            # Parse altitude (8 bytes)
            alt_raw = struct.unpack('<q', msg.data[offset:offset+8])[0]
            offset += 8
            
            # Convert from 1e-16 degrees to degrees
            if lat_raw != 0x7FFFFFFFFFFFFFFF:
                self.position.latitude = lat_raw * 1e-16
            
            if lon_raw != 0x7FFFFFFFFFFFFFFF:
                self.position.longitude = lon_raw * 1e-16
            
            # Convert from 1e-6 meters to meters
            if alt_raw != 0x7FFFFFFFFFFFFFFF:
                self.position.altitude = alt_raw * 1e-6
            
            # Parse GNSS type, method, integrity (3 bytes)
            if len(msg.data) >= offset + 3:
                gnss_type = msg.data[offset]
                method = msg.data[offset + 1]
                integrity = msg.data[offset + 2]
                offset += 3
                
                # Map enumerations to strings (simplified)
                gnss_types = {0: "GPS", 1: "GLONASS", 2: "GPS+GLONASS", 3: "GPS+SBAS/WAAS"}
                self.position.gnss_method = gnss_types.get(gnss_type, f"Unknown({gnss_type})")
                
                integrity_map = {0: "No integrity", 1: "Safe", 2: "Caution"}
                self.position.gnss_integrity = integrity_map.get(integrity, f"Unknown({integrity})")
            
            # Parse number of satellites (1 byte)
            if len(msg.data) >= offset + 1:
                self.position.number_of_svs = msg.data[offset]
                offset += 1
            
            # Parse HDOP and PDOP (2 bytes each)
            if len(msg.data) >= offset + 4:
                hdop_raw = struct.unpack('<H', msg.data[offset:offset+2])[0]
                pdop_raw = struct.unpack('<H', msg.data[offset+2:offset+4])[0]
                
                if hdop_raw != 0xFFFF:
                    self.position.hdop = hdop_raw * 0.01
                if pdop_raw != 0xFFFF:
                    self.position.pdop = pdop_raw * 0.01
                offset += 4
            
            self.position.timestamp = datetime.utcnow()
            
            logger.debug(
                f"PGN 129029: lat={self.position.latitude:.6f}, "
                f"lon={self.position.longitude:.6f}, "
                f"alt={self.position.altitude:.1f}m, "
                f"sats={self.position.number_of_svs}, "
                f"hdop={self.position.hdop:.2f}"
            )
            
        except Exception as e:
            logger.error(f"Error parsing PGN 129029: {e}")
    
    def get_position(self) -> Optional[NMEA2000Position]:
        """Get current GPS position.
        
        Returns:
            NMEA2000Position if valid, None otherwise
        """
        if self.position.is_valid():
            return self.position
        return None


# Module instance (not auto-started)
_nmea2000_gps: Optional[NMEA2000GPS] = None


def get_nmea2000_gps() -> Optional[NMEA2000GPS]:
    """Get the NMEA2000 GPS module instance."""
    global _nmea2000_gps
    if _nmea2000_gps is None and CAN_AVAILABLE:
        _nmea2000_gps = NMEA2000GPS()
    return _nmea2000_gps
