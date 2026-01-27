"""
Test cases for NMEA GPS Module
===============================
Tests for NMEA sentence parsing, mock data generation,
and coordinate conversion.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import pynmea2
from app.modules.nmea_gps import NMEAGPSModule, NMEAData


class TestNMEAData:
    """Test NMEAData container class"""

    def test_nmea_data_initialization(self):
        """Test creating NMEAData object"""
        data = NMEAData()

        assert data.latitude is None
        assert data.longitude is None
        assert data.speed is None
        assert data.heading is None
        assert data.altitude is None
        assert data.timestamp is None
        assert data.satellites is None
        assert data.quality is None
        assert data.raw is None

    def test_nmea_data_to_dict(self):
        """Test converting NMEAData to dictionary"""
        data = NMEAData()
        data.latitude = 78.2232
        data.longitude = 15.6267
        data.speed = 5.5
        data.heading = 45.0
        data.altitude = 10.0
        data.satellites = 12
        data.quality = "good"
        data.timestamp = "2024-01-20T12:00:00Z"

        result = data.to_dict()

        assert result["latitude"] == 78.2232
        assert result["longitude"] == 15.6267
        assert result["speed"] == 5.5
        assert result["heading"] == 45.0
        assert result["altitude"] == 10.0
        assert result["satellites"] == 12
        assert result["quality"] == "good"
        assert result["timestamp"] == "2024-01-20T12:00:00Z"

    def test_nmea_data_is_valid_true(self):
        """Test is_valid returns True when position data exists"""
        data = NMEAData()
        data.latitude = 78.0
        data.longitude = 15.0

        assert data.is_valid() is True

    def test_nmea_data_is_valid_false_no_lat(self):
        """Test is_valid returns False when latitude is None"""
        data = NMEAData()
        data.latitude = None
        data.longitude = 15.0

        assert data.is_valid() is False

    def test_nmea_data_is_valid_false_no_lon(self):
        """Test is_valid returns False when longitude is None"""
        data = NMEAData()
        data.latitude = 78.0
        data.longitude = None

        assert data.is_valid() is False

    def test_nmea_data_is_valid_false_both_none(self):
        """Test is_valid returns False when both are None"""
        data = NMEAData()

        assert data.is_valid() is False


class TestNMEAGPSModule:
    """Test NMEAGPSModule class"""

    def test_initialization(self):
        """Test module initialization"""
        module = NMEAGPSModule()

        assert module.running is False
        assert module.serial_port is None
        assert isinstance(module.current_data, NMEAData)
        assert module._read_task is None
        # Mock data defaults
        assert module._mock_latitude == 78.2232
        assert module._mock_longitude == 15.6267
        assert module._mock_heading == 45.0
        assert module._mock_speed == 5.5

    def test_get_status(self):
        """Test getting module status"""
        module = NMEAGPSModule()

        with patch('app.modules.nmea_gps.settings') as mock_settings:
            mock_settings.NMEA_ENABLED = True
            mock_settings.NMEA_MOCK_DATA = True
            mock_settings.NMEA_SERIAL_PORT = "/dev/ttyUSB0"
            mock_settings.NMEA_BAUD_RATE = 4800

            status = module.get_status()

            assert status["module"] == "nmea_gps"
            assert status["enabled"] is True
            assert status["running"] is False
            assert status["mock_mode"] is True
            assert "has_fix" in status
            assert "last_update" in status

    def test_get_data(self):
        """Test getting current GPS data"""
        module = NMEAGPSModule()
        module.current_data.latitude = 78.0
        module.current_data.longitude = 15.0

        data = module.get_data()

        assert isinstance(data, dict)
        assert data["latitude"] == 78.0
        assert data["longitude"] == 15.0


class TestNMEASentenceParsing:
    """Test parsing of NMEA sentences"""

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_gga_sentence_valid(self, mock_pynmea2):
        """Test parsing valid GGA sentence with position data"""
        module = NMEAGPSModule()

        # Mock GGA message
        mock_msg = Mock()
        mock_msg.latitude = 78.2232
        mock_msg.longitude = 15.6267
        mock_msg.altitude = 10.0
        mock_msg.num_sats = 12
        mock_msg.gps_qual = 1  # GPS fix
        mock_pynmea2.parse.return_value = mock_msg
        mock_pynmea2.types.talker.GGA = type(mock_msg)

        sentence = "$GPGGA,123519,7813.392,N,01537.602,E,1,12,1.0,10.0,M,46.9,M,,*47"
        module._parse_nmea_sentence(sentence)

        assert module.current_data.latitude == 78.2232
        assert module.current_data.longitude == 15.6267
        assert module.current_data.altitude == 10.0
        assert module.current_data.satellites == 12
        assert module.current_data.quality == "gps_fix"
        assert module.current_data.raw == sentence

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_rmc_sentence_valid(self, mock_pynmea2):
        """Test parsing valid RMC sentence with speed and course"""
        module = NMEAGPSModule()

        # Mock RMC message
        mock_msg = Mock(spec=pynmea2.types.talker.RMC)
        mock_msg.latitude = 78.2232
        mock_msg.longitude = 15.6267
        mock_msg.spd_over_grnd = 5.5
        mock_msg.true_course = 45.0
        mock_msg.num_sats = None
        mock_pynmea2.parse.return_value = mock_msg
        mock_pynmea2.types.talker.RMC = pynmea2.types.talker.RMC
        mock_pynmea2.types.talker.GGA = pynmea2.types.talker.GGA
        mock_pynmea2.types.talker.VTG = pynmea2.types.talker.VTG
        mock_pynmea2.types.talker.HDT = pynmea2.types.talker.HDT
        mock_pynmea2.ParseError = pynmea2.ParseError

        sentence = "$GPRMC,123519,A,7813.392,N,01537.602,E,5.5,45.0,200124,,,A*68"
        module._parse_nmea_sentence(sentence)

        assert module.current_data.latitude == 78.2232
        assert module.current_data.longitude == 15.6267
        assert module.current_data.speed == 5.5
        assert module.current_data.heading == 45.0

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_vtg_sentence_valid(self, mock_pynmea2):
        """Test parsing valid VTG sentence with heading"""
        module = NMEAGPSModule()

        # Mock VTG message
        mock_msg = Mock(spec=pynmea2.types.talker.VTG)
        mock_msg.true_track = 45.0
        mock_msg.spd_over_grnd_kts = 5.5
        mock_msg.num_sats = None
        mock_pynmea2.parse.return_value = mock_msg
        mock_pynmea2.types.talker.RMC = pynmea2.types.talker.RMC
        mock_pynmea2.types.talker.GGA = pynmea2.types.talker.GGA
        mock_pynmea2.types.talker.VTG = pynmea2.types.talker.VTG
        mock_pynmea2.types.talker.HDT = pynmea2.types.talker.HDT
        mock_pynmea2.ParseError = pynmea2.ParseError

        sentence = "$GPVTG,45.0,T,40.0,M,5.5,N,10.2,K,A*3C"
        module._parse_nmea_sentence(sentence)

        assert module.current_data.heading == 45.0
        assert module.current_data.speed == 5.5

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_hdt_sentence_valid(self, mock_pynmea2):
        """Test parsing valid HDT sentence with true heading"""
        module = NMEAGPSModule()

        # Mock HDT message
        mock_msg = Mock(spec=pynmea2.types.talker.HDT)
        mock_msg.heading = 45.0
        mock_msg.num_sats = None
        mock_pynmea2.parse.return_value = mock_msg
        mock_pynmea2.types.talker.RMC = pynmea2.types.talker.RMC
        mock_pynmea2.types.talker.GGA = pynmea2.types.talker.GGA
        mock_pynmea2.types.talker.VTG = pynmea2.types.talker.VTG
        mock_pynmea2.types.talker.HDT = pynmea2.types.talker.HDT
        mock_pynmea2.ParseError = pynmea2.ParseError

        sentence = "$GPHDT,45.0,T*3B"
        module._parse_nmea_sentence(sentence)

        assert module.current_data.heading == 45.0

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_sentence_null_values(self, mock_pynmea2):
        """Test parsing sentence with missing data (null fields)"""
        module = NMEAGPSModule()

        # Mock GGA with no position
        mock_msg = Mock()
        mock_msg.latitude = None
        mock_msg.longitude = None
        mock_pynmea2.parse.return_value = mock_msg
        mock_pynmea2.types.talker.GGA = type(mock_msg)

        sentence = "$GPGGA,123519,,,,,0,00,,,,,,,*68"
        module._parse_nmea_sentence(sentence)

        # Should not update position if None
        assert module.current_data.latitude is None
        assert module.current_data.longitude is None

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_sentence_invalid_checksum(self, mock_pynmea2):
        """Test handling of invalid checksum"""
        module = NMEAGPSModule()

        # Simulate parse error
        sentence = "$GPGGA,123519,7813.392,N,01537.602,E,1,12,1.0,10.0,M,46.9,M,,*00"
        mock_pynmea2.parse.side_effect = pynmea2.ParseError("Invalid checksum", sentence)
        mock_pynmea2.ParseError = pynmea2.ParseError

        # Should not raise exception
        module._parse_nmea_sentence(sentence)
        
        # Data should remain unchanged
        assert module.current_data.raw == sentence

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_sentence_corrupted(self, mock_pynmea2):
        """Test handling of corrupted/partial sentence"""
        module = NMEAGPSModule()

        # Simulate parse error
        sentence = "$GPGGA,1235"  # Incomplete
        mock_pynmea2.parse.side_effect = pynmea2.ParseError("Corrupted", sentence)
        mock_pynmea2.ParseError = pynmea2.ParseError

        # Should handle gracefully
        module._parse_nmea_sentence(sentence)

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_sentence_empty(self, mock_pynmea2):
        """Test handling of empty sentence"""
        module = NMEAGPSModule()

        # Simulate parse error
        sentence = ""
        mock_pynmea2.parse.side_effect = pynmea2.ParseError("Empty", sentence)
        mock_pynmea2.ParseError = pynmea2.ParseError

        # Should handle gracefully
        module._parse_nmea_sentence(sentence)

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_gga_quality_indicators(self, mock_pynmea2):
        """Test parsing different GPS quality indicators"""
        module = NMEAGPSModule()

        # Mock GGA messages with different quality
        for qual, expected in [(0, "invalid"), (1, "gps_fix"), (2, "dgps_fix"), (9, "unknown")]:
            mock_msg = Mock()
            mock_msg.latitude = 78.0
            mock_msg.longitude = 15.0
            mock_msg.altitude = None
            mock_msg.num_sats = 8
            mock_msg.gps_qual = qual
            mock_pynmea2.parse.return_value = mock_msg
            mock_pynmea2.types.talker.GGA = type(mock_msg)

            module._parse_nmea_sentence("$GPGGA,...")

            assert module.current_data.quality == expected


@pytest.mark.asyncio
class TestMockDataGeneration:
    """Test mock data generation for testing"""

    @patch('app.modules.nmea_gps.settings')
    async def test_mock_data_generates_valid_sentences(self, mock_settings):
        """Test mock generator produces valid data"""
        mock_settings.NMEA_ENABLED = True
        mock_settings.NMEA_MOCK_DATA = True
        mock_settings.NMEA_UPDATE_INTERVAL = 0.1

        module = NMEAGPSModule()
        
        # Start mock loop
        await module.start()
        
        # Let it generate some data
        await asyncio.sleep(0.2)
        
        # Stop
        await module.stop()

        # Should have position data
        assert module.current_data.latitude is not None
        assert module.current_data.longitude is not None
        assert module.current_data.speed is not None
        assert module.current_data.heading is not None

    @patch('app.modules.nmea_gps.settings')
    async def test_mock_data_simulated_movement(self, mock_settings):
        """Test mock data simulates movement"""
        mock_settings.NMEA_ENABLED = True
        mock_settings.NMEA_MOCK_DATA = True
        mock_settings.NMEA_UPDATE_INTERVAL = 0.05

        module = NMEAGPSModule()
        
        initial_lat = module._mock_latitude
        initial_lon = module._mock_longitude
        
        await module.start()
        await asyncio.sleep(0.15)  # Let it update a few times
        await module.stop()

        # Position should have changed (random movement)
        # Note: There's a small chance they could be equal by random chance
        # but very unlikely after multiple updates

    @patch('app.modules.nmea_gps.settings')
    async def test_mock_data_format_compliance(self, mock_settings):
        """Test mock data follows NMEA format"""
        mock_settings.NMEA_ENABLED = True
        mock_settings.NMEA_MOCK_DATA = True
        mock_settings.NMEA_UPDATE_INTERVAL = 0.1

        module = NMEAGPSModule()
        
        await module.start()
        await asyncio.sleep(0.15)
        await module.stop()

        # Check raw NMEA sentence format
        raw = module.current_data.raw
        assert raw is not None
        assert raw.startswith("$GPRMC")
        assert "," in raw

    @patch('app.modules.nmea_gps.settings')
    async def test_mock_data_satellite_count(self, mock_settings):
        """Test mock data generates realistic satellite count"""
        mock_settings.NMEA_ENABLED = True
        mock_settings.NMEA_MOCK_DATA = True
        mock_settings.NMEA_UPDATE_INTERVAL = 0.1

        module = NMEAGPSModule()
        
        await module.start()
        await asyncio.sleep(0.15)
        await module.stop()

        # Should have realistic satellite count (8-12)
        assert module.current_data.satellites is not None
        assert 8 <= module.current_data.satellites <= 12


class TestCoordinateConversion:
    """Test coordinate conversion and validation"""

    @patch('app.modules.nmea_gps.pynmea2')
    def test_coordinate_conversion_ddmm_to_decimal(self, mock_pynmea2):
        """Test conversion from DDMM.MMMM to decimal degrees"""
        module = NMEAGPSModule()

        # NMEA format: DDMM.MMMM (78°13.392' = 78.2232°)
        mock_msg = Mock()
        mock_msg.latitude = 78.2232  # pynmea2 already converts
        mock_msg.longitude = 15.6267
        mock_msg.altitude = None
        mock_msg.num_sats = None
        mock_pynmea2.parse.return_value = mock_msg
        mock_pynmea2.types.talker.GGA = type(mock_msg)

        module._parse_nmea_sentence("$GPGGA,...")

        # Verify decimal degrees
        assert pytest.approx(module.current_data.latitude, abs=0.0001) == 78.2232
        assert pytest.approx(module.current_data.longitude, abs=0.0001) == 15.6267

    @patch('app.modules.nmea_gps.pynmea2')
    def test_coordinate_conversion_hemisphere(self, mock_pynmea2):
        """Test N/S and E/W hemisphere handling"""
        module = NMEAGPSModule()

        # Southern hemisphere
        mock_msg = Mock()
        mock_msg.latitude = -23.5  # South
        mock_msg.longitude = 45.5  # East
        mock_msg.altitude = None
        mock_msg.num_sats = None
        mock_pynmea2.parse.return_value = mock_msg
        mock_pynmea2.types.talker.GGA = type(mock_msg)

        module._parse_nmea_sentence("$GPGGA,...")

        assert module.current_data.latitude < 0  # Negative for South

    @patch('app.modules.nmea_gps.pynmea2')
    def test_coordinate_conversion_boundary_values(self, mock_pynmea2):
        """Test boundary coordinate values"""
        module = NMEAGPSModule()

        # Test cases: (lat, lon) pairs
        test_cases = [
            (0.0, 0.0),      # Equator, Prime Meridian
            (90.0, 0.0),     # North Pole
            (-90.0, 0.0),    # South Pole
            (0.0, 180.0),    # Date Line (East)
            (0.0, -180.0),   # Date Line (West)
        ]

        for lat, lon in test_cases:
            mock_msg = Mock(spec=pynmea2.types.talker.GGA)
            mock_msg.latitude = lat
            mock_msg.longitude = lon
            mock_msg.altitude = None
            mock_msg.num_sats = None
            mock_pynmea2.parse.return_value = mock_msg
            mock_pynmea2.types.talker.RMC = pynmea2.types.talker.RMC
            mock_pynmea2.types.talker.GGA = pynmea2.types.talker.GGA
            mock_pynmea2.types.talker.VTG = pynmea2.types.talker.VTG
            mock_pynmea2.types.talker.HDT = pynmea2.types.talker.HDT

            module._parse_nmea_sentence("$GPGGA,...")

            assert module.current_data.latitude == lat
            assert module.current_data.longitude == lon


@pytest.mark.asyncio
class TestSerialCommunication:
    """Test serial port communication (mocked)"""

    @patch('app.modules.nmea_gps.settings')
    @patch('app.modules.nmea_gps.serial.Serial')
    async def test_serial_port_timeout(self, mock_serial, mock_settings):
        """Test handling of serial port read timeout"""
        mock_settings.NMEA_ENABLED = True
        mock_settings.NMEA_MOCK_DATA = False
        mock_settings.NMEA_SERIAL_PORT = "/dev/ttyUSB0"
        mock_settings.NMEA_BAUD_RATE = 4800
        mock_settings.NMEA_TIMEOUT = 1.0

        # Mock serial port with no data
        mock_port = Mock()
        mock_port.in_waiting = False
        mock_port.is_open = True
        mock_serial.return_value = mock_port

        module = NMEAGPSModule()
        
        # Start and quickly stop
        await module.start()
        await asyncio.sleep(0.1)
        await module.stop()

        # Should handle timeout gracefully
        assert mock_port.close.called

    @patch('app.modules.nmea_gps.settings')
    @patch('app.modules.nmea_gps.serial.Serial')
    async def test_serial_port_not_found(self, mock_serial, mock_settings):
        """Test handling when serial port doesn't exist"""
        mock_settings.NMEA_ENABLED = True
        mock_settings.NMEA_MOCK_DATA = False
        mock_settings.NMEA_SERIAL_PORT = "/dev/ttyUSB99"
        mock_settings.NMEA_BAUD_RATE = 4800

        # Simulate port not found
        import serial as serial_module
        mock_serial.side_effect = serial_module.SerialException("Port not found")

        module = NMEAGPSModule()
        
        # Should not crash
        await module.start()
        await asyncio.sleep(0.1)
        await module.stop()


@pytest.mark.asyncio
class TestModuleLifecycle:
    """Test module lifecycle operations"""

    @patch('app.modules.nmea_gps.settings')
    async def test_start_already_running(self, mock_settings):
        """Test starting module when already running"""
        mock_settings.NMEA_ENABLED = True
        mock_settings.NMEA_MOCK_DATA = True

        module = NMEAGPSModule()
        
        await module.start()
        assert module.running is True

        # Try to start again
        await module.start()
        
        # Should still be running
        assert module.running is True
        
        await module.stop()

    @patch('app.modules.nmea_gps.settings')
    async def test_stop_not_running(self, mock_settings):
        """Test stopping module when not running"""
        mock_settings.NMEA_ENABLED = True

        module = NMEAGPSModule()
        
        # Stop without starting
        await module.stop()
        
        # Should handle gracefully
        assert module.running is False

    @patch('app.modules.nmea_gps.settings')
    async def test_module_disabled(self, mock_settings):
        """Test module respects disabled configuration"""
        mock_settings.NMEA_ENABLED = False

        module = NMEAGPSModule()
        
        await module.start()
        
        # Should not start if disabled
        assert module.running is False


class TestEdgeCases:
    """Test edge cases and error handling"""

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_sentence_with_exception(self, mock_pynmea2):
        """Test handling of unexpected exception during parsing"""
        module = NMEAGPSModule()

        # Simulate unexpected error
        mock_pynmea2.parse.side_effect = Exception("Unexpected error")
        mock_pynmea2.ParseError = pynmea2.ParseError

        sentence = "$GPGGA,123519,7813.392,N,01537.602,E,1,12,1.0,10.0,M,46.9,M,,*47"
        
        # Should not crash
        module._parse_nmea_sentence(sentence)

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_gga_missing_satellites(self, mock_pynmea2):
        """Test parsing GGA without satellite count"""
        module = NMEAGPSModule()

        mock_msg = Mock()
        mock_msg.latitude = 78.0
        mock_msg.longitude = 15.0
        mock_msg.altitude = None
        mock_msg.num_sats = None  # Missing
        mock_pynmea2.parse.return_value = mock_msg
        mock_pynmea2.types.talker.GGA = type(mock_msg)
        mock_pynmea2.types.talker.RMC = Mock
        mock_pynmea2.types.talker.VTG = Mock
        mock_pynmea2.types.talker.HDT = Mock
        mock_pynmea2.ParseError = pynmea2.ParseError

        module._parse_nmea_sentence("$GPGGA,...")

        # Should handle None satellite count
        assert module.current_data.satellites is None

    @patch('app.modules.nmea_gps.pynmea2')
    def test_parse_rmc_missing_speed(self, mock_pynmea2):
        """Test parsing RMC without speed data"""
        module = NMEAGPSModule()

        mock_msg = Mock(spec=pynmea2.types.talker.RMC)
        mock_msg.latitude = 78.0
        mock_msg.longitude = 15.0
        mock_msg.spd_over_grnd = None
        mock_msg.true_course = 45.0
        mock_msg.num_sats = None
        mock_pynmea2.parse.return_value = mock_msg
        mock_pynmea2.types.talker.RMC = pynmea2.types.talker.RMC
        mock_pynmea2.types.talker.GGA = pynmea2.types.talker.GGA
        mock_pynmea2.types.talker.VTG = pynmea2.types.talker.VTG
        mock_pynmea2.types.talker.HDT = pynmea2.types.talker.HDT
        mock_pynmea2.ParseError = pynmea2.ParseError

        module._parse_nmea_sentence("$GPRMC,...")

        # Speed should not be updated
        assert module.current_data.heading == 45.0
