"""
Test cases for Signal K module
"""

import pytest
import asyncio
from datetime import datetime, timezone
from app.modules.signalk_client import SignalKModule, SignalKData


class TestSignalKData:
    """Test SignalKData container class."""
    
    def test_initialization(self):
        """Test SignalKData initialization."""
        data = SignalKData()
        
        assert data.latitude is None
        assert data.longitude is None
        assert data.speed_over_ground is None
        assert data.water_depth is None
        assert data.engine_rpm is None
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        data = SignalKData()
        data.latitude = 78.2232
        data.longitude = 15.6267
        data.speed_over_ground = 5.5
        data.water_depth = 42.5
        data.engine_rpm = 1800
        data.timestamp = datetime.now(timezone.utc).isoformat()
        data.source = "test"
        
        result = data.to_dict()
        
        assert result["navigation"]["latitude"] == 78.2232
        assert result["navigation"]["longitude"] == 15.6267
        assert result["navigation"]["speed_over_ground"] == 5.5
        assert result["environment"]["water_depth"] == 42.5
        assert result["propulsion"]["engine_rpm"] == 1800
        assert result["timestamp"] is not None
        assert result["source"] == "test"
    
    def test_is_valid(self):
        """Test validity check."""
        data = SignalKData()
        
        # No position data - not valid
        assert not data.is_valid()
        
        # Only latitude - not valid
        data.latitude = 78.2232
        assert not data.is_valid()
        
        # Both latitude and longitude - valid
        data.longitude = 15.6267
        assert data.is_valid()


class TestSignalKModule:
    """Test SignalKModule class."""
    
    def test_initialization(self):
        """Test module initialization."""
        module = SignalKModule()
        
        assert not module.running
        assert module.ws is None
        assert module.current_data is not None
        assert module._read_task is None
    
    def test_get_status(self):
        """Test status retrieval."""
        module = SignalKModule()
        status = module.get_status()
        
        assert status["module"] == "signalk"
        assert "enabled" in status
        assert "running" in status
        assert "mock_mode" in status
        assert status["running"] is False
    
    def test_get_data(self):
        """Test data retrieval."""
        module = SignalKModule()
        data = module.get_data()
        
        assert "navigation" in data
        assert "environment" in data
        assert "propulsion" in data
        assert "latitude" in data["navigation"]
        assert "water_depth" in data["environment"]
        assert "engine_rpm" in data["propulsion"]
    
    @pytest.mark.asyncio
    async def test_start_stop_mock_mode(self):
        """Test starting and stopping in mock mode."""
        module = SignalKModule()
        
        # Override settings for test
        from app.core.config import settings
        original_enabled = settings.SIGNALK_ENABLED
        original_mock = settings.SIGNALK_MOCK_DATA
        
        try:
            settings.SIGNALK_ENABLED = True
            settings.SIGNALK_MOCK_DATA = True
            
            # Start module
            await module.start()
            assert module.running
            
            # Wait a bit for data generation
            await asyncio.sleep(0.5)
            
            # Check that data has been generated
            data = module.get_data()
            assert data["navigation"]["latitude"] is not None
            assert data["navigation"]["longitude"] is not None
            
            # Stop module
            await module.stop()
            assert not module.running
            
        finally:
            # Restore settings
            settings.SIGNALK_ENABLED = original_enabled
            settings.SIGNALK_MOCK_DATA = original_mock
    
    @pytest.mark.asyncio
    async def test_mock_data_generation(self):
        """Test that mock data generates realistic values."""
        module = SignalKModule()
        
        from app.core.config import settings
        original_enabled = settings.SIGNALK_ENABLED
        original_mock = settings.SIGNALK_MOCK_DATA
        
        try:
            settings.SIGNALK_ENABLED = True
            settings.SIGNALK_MOCK_DATA = True
            
            await module.start()
            
            # Wait for data generation
            await asyncio.sleep(1.5)
            
            data = module.get_data()
            nav = data["navigation"]
            env = data["environment"]
            prop = data["propulsion"]
            
            # Check navigation data
            assert nav["latitude"] is not None
            assert nav["longitude"] is not None
            assert 70 < nav["latitude"] < 80  # Arctic region
            assert 10 < nav["longitude"] < 20
            assert nav["speed_over_ground"] >= 0
            assert 0 <= nav["heading"] < 360
            
            # Check environment data
            assert env["water_depth"] > 0
            assert env["water_temperature"] is not None
            assert env["wind_speed"] >= 0
            assert 0 <= env["wind_direction"] < 360
            
            # Check propulsion data
            assert prop["engine_rpm"] > 0
            assert prop["engine_temperature"] > 0
            assert 0 <= prop["fuel_level"] <= 100
            
            await module.stop()
            
        finally:
            settings.SIGNALK_ENABLED = original_enabled
            settings.SIGNALK_MOCK_DATA = original_mock
    
    @pytest.mark.asyncio
    async def test_disabled_module(self):
        """Test that disabled module doesn't start."""
        module = SignalKModule()
        
        from app.core.config import settings
        original_enabled = settings.SIGNALK_ENABLED
        
        try:
            settings.SIGNALK_ENABLED = False
            
            await module.start()
            assert not module.running
            
        finally:
            settings.SIGNALK_ENABLED = original_enabled


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
