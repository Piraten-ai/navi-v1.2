"""Quick working tests for actual AADS models"""

import pytest
from datetime import datetime
import json

from app.core.models import VisionDetection, NAVTEXMessage, AudioAnomaly, SensorReading, Alert


@pytest.mark.unit
class TestModelsQuick:
    """Quick tests that match actual model structure."""

    def test_vision_detection_basic(self, test_db_session):
        """Test VisionDetection with actual fields."""
        detection = VisionDetection(
            threat_type="ICE",  # Actual enum value
            confidence=0.92,
            distance_meters=500.0
        )
        test_db_session.add(detection)
        test_db_session.commit()
        test_db_session.refresh(detection)

        assert detection.id is not None
        assert detection.timestamp is not None  # Field is 'timestamp' not 'created_at'
        assert str(detection.threat_type) == "ThreatType.ICE"

    def test_navtex_message_basic(self, test_db_session):
        """Test NAVTEXMessage with actual fields."""
        message = NAVTEXMessage(
            category="A",  # Actual field is 'category' not 'message_type'
            body="GALE WARNING: Wind NE 30-40 knots",  # Field is 'body' not 'content'
            station_id="SVALBARD"
        )
        test_db_session.add(message)
        test_db_session.commit()
        test_db_session.refresh(message)

        assert message.id is not None
        assert message.timestamp is not None
        assert "GALE WARNING" in message.body

    def test_audio_anomaly_basic(self, test_db_session):
        """Test AudioAnomaly with actual fields."""
        anomaly = AudioAnomaly(
            confidence=0.87,
            description="unusual_vibration",  # Field is 'description' not 'anomaly_type'
            severity="medium"
        )
        test_db_session.add(anomaly)
        test_db_session.commit()
        test_db_session.refresh(anomaly)

        assert anomaly.id is not None
        assert anomaly.timestamp is not None
        assert anomaly.severity == "medium"

    def test_sensor_reading_basic(self, test_db_session):
        """Test SensorReading with actual fields."""
        reading = SensorReading(
            sensor_type="GPS",  # Actual enum value
            latitude=78.2232,
            longitude=15.6267
        )
        test_db_session.add(reading)
        test_db_session.commit()
        test_db_session.refresh(reading)

        assert reading.id is not None
        assert reading.timestamp is not None
        assert reading.latitude == 78.2232

    def test_alert_basic(self, test_db_session):
        """Test Alert with actual fields."""
        alert = Alert(
            severity="warning",
            category="vision",
            title="Ice Detected",
            message="Large iceberg detected"
            # Note: 'source' field doesn't exist in actual model
        )
        test_db_session.add(alert)
        test_db_session.commit()
        test_db_session.refresh(alert)

        assert alert.id is not None
        assert alert.timestamp is not None
        assert alert.resolved == False
