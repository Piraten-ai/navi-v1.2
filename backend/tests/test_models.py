"""
Unit tests for SQLAlchemy database models.

Tests all 8 AADS database models:
- VisionDetection
- NAVTEXMessage
- AudioAnomaly
- SensorReading
- SystemLog
- AIInteraction
- Voyage
- Alert
"""

import pytest
from datetime import datetime, timedelta
import json
from sqlalchemy.exc import IntegrityError

from app.core.models import (
    VisionDetection,
    NAVTEXMessage,
    AudioAnomaly,
    SensorReading,
    SystemLog,
    AIInteraction,
    Voyage,
    Alert
)


# ============================================================================
# VisionDetection Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestVisionDetection:
    """Tests for VisionDetection model."""

    def test_create_vision_detection(self, test_db_session):
        """Test creating a VisionDetection record."""
        detection = VisionDetection(
            threat_type="ice",
            confidence=0.92,
            distance_meters=500.0,
            bearing_degrees=45.0,
            bbox=json.dumps({"x": 100, "y": 200, "width": 150, "height": 200}),
            image_path="/data/images/ice_001.jpg"
        )

        test_db_session.add(detection)
        test_db_session.commit()
        test_db_session.refresh(detection)

        assert detection.id is not None
        assert detection.threat_type == "ice"
        assert detection.confidence == 0.92
        assert detection.distance_meters == 500.0
        assert detection.created_at is not None

    def test_vision_detection_defaults(self, test_db_session):
        """Test VisionDetection default values."""
        detection = VisionDetection(
            threat_type="ship",
            confidence=0.75
        )

        test_db_session.add(detection)
        test_db_session.commit()
        test_db_session.refresh(detection)

        assert detection.distance_meters is None
        assert detection.bearing_degrees is None
        assert detection.bbox is None
        assert detection.created_at is not None

    def test_vision_detection_all_threat_types(self, test_db_session):
        """Test all valid threat types."""
        threat_types = ["ice", "ship", "whale", "debris", "unknown"]

        for threat_type in threat_types:
            detection = VisionDetection(
                threat_type=threat_type,
                confidence=0.8
            )
            test_db_session.add(detection)

        test_db_session.commit()

        detections = test_db_session.query(VisionDetection).all()
        assert len(detections) == 5
        retrieved_types = [d.threat_type for d in detections]
        assert set(retrieved_types) == set(threat_types)

    def test_vision_detection_json_bbox(self, test_db_session):
        """Test storing and retrieving JSON bbox data."""
        bbox_data = {"x": 150, "y": 250, "width": 200, "height": 300}

        detection = VisionDetection(
            threat_type="ice",
            confidence=0.88,
            bbox=json.dumps(bbox_data)
        )

        test_db_session.add(detection)
        test_db_session.commit()
        test_db_session.refresh(detection)

        retrieved_bbox = json.loads(detection.bbox)
        assert retrieved_bbox == bbox_data


# ============================================================================
# NAVTEXMessage Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestNAVTEXMessage:
    """Tests for NAVTEXMessage model."""

    def test_create_navtex_message(self, test_db_session):
        """Test creating a NAVTEXMessage record."""
        message = NAVTEXMessage(
            message_type="weather",
            content="GALE WARNING: Wind NE 30-40 knots",
            source_station="SVALBARD",
            transmission_frequency="518kHz",
            valid_from=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(hours=24)
        )

        test_db_session.add(message)
        test_db_session.commit()
        test_db_session.refresh(message)

        assert message.id is not None
        assert message.message_type == "weather"
        assert "GALE WARNING" in message.content
        assert message.received_at is not None

    def test_navtex_message_types(self, test_db_session):
        """Test all valid NAVTEX message types."""
        message_types = ["weather", "ice", "nav_warning", "sar", "other"]

        for msg_type in message_types:
            message = NAVTEXMessage(
                message_type=msg_type,
                content=f"Test {msg_type} message"
            )
            test_db_session.add(message)

        test_db_session.commit()

        messages = test_db_session.query(NAVTEXMessage).all()
        assert len(messages) == 5

    def test_navtex_validity_period(self, test_db_session):
        """Test NAVTEX message validity period."""
        now = datetime.utcnow()
        valid_from = now
        valid_until = now + timedelta(hours=48)

        message = NAVTEXMessage(
            message_type="ice",
            content="Ice concentration 7/10",
            valid_from=valid_from,
            valid_until=valid_until
        )

        test_db_session.add(message)
        test_db_session.commit()
        test_db_session.refresh(message)

        assert message.valid_from == valid_from
        assert message.valid_until == valid_until


# ============================================================================
# AudioAnomaly Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestAudioAnomaly:
    """Tests for AudioAnomaly model."""

    def test_create_audio_anomaly(self, test_db_session):
        """Test creating an AudioAnomaly record."""
        anomaly = AudioAnomaly(
            anomaly_type="unusual_vibration",
            confidence=0.87,
            audio_file_path="/data/audio/anomaly_001.wav",
            frequency_range="500-1000Hz",
            detected_pattern="irregular_knocking",
            severity="medium"
        )

        test_db_session.add(anomaly)
        test_db_session.commit()
        test_db_session.refresh(anomaly)

        assert anomaly.id is not None
        assert anomaly.anomaly_type == "unusual_vibration"
        assert anomaly.severity == "medium"
        assert anomaly.detected_at is not None

    def test_audio_anomaly_severities(self, test_db_session):
        """Test all severity levels."""
        severities = ["low", "medium", "high", "critical"]

        for severity in severities:
            anomaly = AudioAnomaly(
                anomaly_type="test",
                confidence=0.9,
                severity=severity
            )
            test_db_session.add(anomaly)

        test_db_session.commit()

        anomalies = test_db_session.query(AudioAnomaly).all()
        assert len(anomalies) == 4


# ============================================================================
# SensorReading Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestSensorReading:
    """Tests for SensorReading model."""

    def test_create_gps_reading(self, test_db_session):
        """Test creating a GPS sensor reading."""
        reading = SensorReading(
            sensor_type="gps",
            latitude=78.2232,
            longitude=15.6267,
            speed_knots=8.2
        )

        test_db_session.add(reading)
        test_db_session.commit()
        test_db_session.refresh(reading)

        assert reading.id is not None
        assert reading.sensor_type == "gps"
        assert reading.latitude == 78.2232
        assert reading.timestamp is not None

    def test_create_imu_reading(self, test_db_session):
        """Test creating an IMU sensor reading."""
        reading = SensorReading(
            sensor_type="imu",
            roll_degrees=2.1,
            pitch_degrees=1.5,
            yaw_degrees=0.8
        )

        test_db_session.add(reading)
        test_db_session.commit()
        test_db_session.refresh(reading)

        assert reading.sensor_type == "imu"
        assert reading.roll_degrees == 2.1

    def test_sensor_types(self, test_db_session):
        """Test all sensor types."""
        sensor_types = ["gps", "imu", "weather", "radar", "other"]

        for sensor_type in sensor_types:
            reading = SensorReading(sensor_type=sensor_type)
            test_db_session.add(reading)

        test_db_session.commit()

        readings = test_db_session.query(SensorReading).all()
        assert len(readings) == 5


# ============================================================================
# SystemLog Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestSystemLog:
    """Tests for SystemLog model."""

    def test_create_system_log(self, test_db_session):
        """Test creating a SystemLog entry."""
        log = SystemLog(
            level="INFO",
            module="vakten",
            message="Detection system initialized",
            details=json.dumps({"version": "1.0.0"})
        )

        test_db_session.add(log)
        test_db_session.commit()
        test_db_session.refresh(log)

        assert log.id is not None
        assert log.level == "INFO"
        assert log.module == "vakten"
        assert log.timestamp is not None

    def test_log_levels(self, test_db_session):
        """Test all log levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            log = SystemLog(
                level=level,
                module="test",
                message=f"Test {level} message"
            )
            test_db_session.add(log)

        test_db_session.commit()

        logs = test_db_session.query(SystemLog).all()
        assert len(logs) == 5


# ============================================================================
# AIInteraction Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestAIInteraction:
    """Tests for AIInteraction model."""

    def test_create_ai_interaction(self, test_db_session):
        """Test creating an AI interaction."""
        interaction = AIInteraction(
            provider="ollama",
            model="llama2",
            prompt="What's the weather like?",
            response="Based on latest NAVTEX...",
            tokens_used=150,
            response_time_ms=1250.5
        )

        test_db_session.add(interaction)
        test_db_session.commit()
        test_db_session.refresh(interaction)

        assert interaction.id is not None
        assert interaction.provider == "ollama"
        assert interaction.tokens_used == 150
        assert interaction.created_at is not None

    def test_ai_providers(self, test_db_session):
        """Test all AI providers."""
        providers = ["ollama", "gemini", "claude"]

        for provider in providers:
            interaction = AIInteraction(
                provider=provider,
                model="test-model",
                prompt="Test",
                response="Response"
            )
            test_db_session.add(interaction)

        test_db_session.commit()

        interactions = test_db_session.query(AIInteraction).all()
        assert len(interactions) == 3


# ============================================================================
# Voyage Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestVoyage:
    """Tests for Voyage model."""

    def test_create_voyage(self, test_db_session):
        """Test creating a Voyage record."""
        voyage = Voyage(
            name="Arctic Expedition 2024",
            start_port="Tromsø",
            end_port="Longyearbyen",
            departure_time=datetime.utcnow(),
            status="in_progress"
        )

        test_db_session.add(voyage)
        test_db_session.commit()
        test_db_session.refresh(voyage)

        assert voyage.id is not None
        assert voyage.name == "Arctic Expedition 2024"
        assert voyage.status == "in_progress"
        assert voyage.created_at is not None

    def test_voyage_statuses(self, test_db_session):
        """Test all voyage statuses."""
        statuses = ["planned", "in_progress", "completed", "cancelled"]

        for status in statuses:
            voyage = Voyage(
                name=f"Voyage {status}",
                status=status
            )
            test_db_session.add(voyage)

        test_db_session.commit()

        voyages = test_db_session.query(Voyage).all()
        assert len(voyages) == 4


# ============================================================================
# Alert Model Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.database
class TestAlert:
    """Tests for Alert model."""

    def test_create_alert(self, test_db_session):
        """Test creating an Alert."""
        alert = Alert(
            severity="warning",
            category="vision",
            title="Ice Detected",
            message="Large iceberg detected ahead",
            source="vakten"
        )

        test_db_session.add(alert)
        test_db_session.commit()
        test_db_session.refresh(alert)

        assert alert.id is not None
        assert alert.severity == "warning"
        assert alert.resolved == False
        assert alert.created_at is not None

    def test_alert_severities(self, test_db_session):
        """Test all alert severities."""
        severities = ["info", "warning", "critical"]

        for severity in severities:
            alert = Alert(
                severity=severity,
                category="test",
                title=f"Test {severity}",
                message="Test message"
            )
            test_db_session.add(alert)

        test_db_session.commit()

        alerts = test_db_session.query(Alert).all()
        assert len(alerts) == 3

    def test_alert_resolution(self, test_db_session):
        """Test alert resolution."""
        alert = Alert(
            severity="warning",
            category="test",
            title="Test",
            message="Test alert"
        )

        test_db_session.add(alert)
        test_db_session.commit()

        assert alert.resolved == False
        assert alert.resolved_at is None

        # Resolve the alert
        alert.resolved = True
        alert.resolved_at = datetime.utcnow()
        test_db_session.commit()

        assert alert.resolved == True
        assert alert.resolved_at is not None
