"""Tests for NMEA2000 GPS module."""

import struct
from datetime import datetime
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_can_message():
    """Create a mock CAN message for testing."""
    def _create_message(pgn: int, data: bytes) -> Mock:
        """Create mock CAN message with given PGN and data."""
        msg = Mock()
        # NMEA2000 CAN ID format: PGN is in bits 8-25
        msg.arbitration_id = (pgn << 8) | 0x00
        msg.data = data
        return msg
    return _create_message


def test_pgn_129025_parsing(mock_can_message):
    """Test parsing of PGN 129025 (Position, Rapid Update).
    
    Verifies that latitude and longitude are correctly extracted from
    CAN bus message data and converted from 1e-7 degrees to decimal degrees.
    """
    # Import with mocked python-can
    with patch.dict('sys.modules', {'can': Mock()}):
        from app.modules.nmea2000_gps import NMEA2000GPS
        
        # Create GPS instance
        gps = NMEA2000GPS()
        
        # Create test data: 78.2232°N, 15.6267°E (Longyearbyen, Svalbard)
        lat_raw = int(78.2232 * 1e7)  # Convert to 1e-7 degrees
        lon_raw = int(15.6267 * 1e7)
        
        # Pack into bytes (little-endian signed 32-bit integers)
        data = struct.pack('<ii', lat_raw, lon_raw)
        
        # Create mock CAN message for PGN 129025
        msg = mock_can_message(129025, data)
        
        # Parse the message
        gps._handle_pgn_129025(msg)
        
        # Verify parsed position
        assert gps.position.latitude is not None
        assert gps.position.longitude is not None
        
        # Check values with tolerance for floating point precision
        assert abs(gps.position.latitude - 78.2232) < 0.0001
        assert abs(gps.position.longitude - 15.6267) < 0.0001
        
        # Verify timestamp was updated
        assert isinstance(gps.position.timestamp, datetime)
        
        # Verify position is valid
        assert gps.position.is_valid()


def test_pgn_129025_invalid_data(mock_can_message):
    """Test handling of invalid PGN 129025 data (0x7FFFFFFF marker)."""
    with patch.dict('sys.modules', {'can': Mock()}):
        from app.modules.nmea2000_gps import NMEA2000GPS
        
        gps = NMEA2000GPS()
        
        # Use invalid data marker (0x7FFFFFFF)
        invalid_marker = 0x7FFFFFFF
        data = struct.pack('<ii', invalid_marker, invalid_marker)
        
        msg = mock_can_message(129025, data)
        gps._handle_pgn_129025(msg)
        
        # Position should remain None when invalid data received
        assert gps.position.latitude is None
        assert gps.position.longitude is None
        assert not gps.position.is_valid()
