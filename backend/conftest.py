"""
Pytest configuration and shared fixtures for AADS backend tests.

This file provides:
- Test database setup/teardown
- Mock fixtures for external services
- Sample data fixtures
- Helper functions
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import Generator
import json
from unittest.mock import MagicMock

from app.main import app
from app.core.models import Base, VisionDetection, NAVTEXMessage, AudioAnomaly, SensorReading, SystemLog, AIInteraction, Voyage, Alert

# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def test_db_engine():
    """Create an in-memory SQLite database engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    SessionLocal = sessionmaker(bind=test_db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(test_db_session):
    """Create a FastAPI test client with test database."""
    # Mock the database dependency
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    # Override the dependency if it exists in the app
    # Note: get_db should be imported from the appropriate location
    # For now, we'll just create the test client
    with TestClient(app) as test_client:
        yield test_client


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_vision_detection(test_db_session):
    """Create a sample VisionDetection record."""
    detection = VisionDetection(
        threat_type="ice",
        confidence=0.92,
        distance_meters=500.0,
        bearing_degrees=45.0,
        bbox=json.dumps({"x": 100, "y": 200, "width": 150, "height": 200}),
        image_path="/data/images/detection_001.jpg",
        notes="Large iceberg detected ahead"
    )
    test_db_session.add(detection)
    test_db_session.commit()
    test_db_session.refresh(detection)
    return detection


@pytest.fixture
def sample_navtex_message(test_db_session):
    """Create a sample NAVTEXMessage record."""
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
    return message


@pytest.fixture
def sample_audio_anomaly(test_db_session):
    """Create a sample AudioAnomaly record."""
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
    return anomaly


@pytest.fixture
def sample_sensor_reading(test_db_session):
    """Create a sample SensorReading record."""
    reading = SensorReading(
        sensor_type="gps",
        latitude=78.2232,
        longitude=15.6267,
        heading=45.5,
        speed_knots=8.2,
        roll_degrees=2.1,
        pitch_degrees=1.5,
        yaw_degrees=0.8,
        temperature_celsius=-5.2,
        pressure_hpa=1013.25,
        humidity_percent=75.0,
        raw_data=json.dumps({"satellites": 12, "hdop": 0.9})
    )
    test_db_session.add(reading)
    test_db_session.commit()
    test_db_session.refresh(reading)
    return reading


@pytest.fixture
def sample_voyage(test_db_session):
    """Create a sample Voyage record."""
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
    return voyage


@pytest.fixture
def sample_alert(test_db_session):
    """Create a sample Alert record."""
    alert = Alert(
        severity="warning",
        category="vision",
        title="Ice Detected",
        message="Large iceberg detected 500m ahead at bearing 45°",
        source="vakten"
    )
    test_db_session.add(alert)
    test_db_session.commit()
    test_db_session.refresh(alert)
    return alert


# ============================================================================
# MOCK FIXTURES FOR EXTERNAL SERVICES
# ============================================================================

@pytest.fixture
def mock_ollama_response():
    """Mock Ollama API response."""
    return {
        "model": "llama2",
        "created_at": "2024-01-01T00:00:00Z",
        "response": "This is a test response from Ollama",
        "done": True
    }


@pytest.fixture
def mock_gemini_response():
    """Mock Google Gemini API response."""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "This is a test response from Gemini"}
                    ]
                }
            }
        ]
    }


@pytest.fixture
def mock_claude_response():
    """Mock Anthropic Claude API response."""
    return {
        "content": [
            {
                "type": "text",
                "text": "This is a test response from Claude"
            }
        ],
        "model": "claude-3-sonnet-20240229",
        "role": "assistant"
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_test_detection(session: Session, **kwargs) -> VisionDetection:
    """Helper to create a test VisionDetection with custom fields."""
    defaults = {
        "threat_type": "ice",
        "confidence": 0.85,
        "distance_meters": 300.0,
        "bearing_degrees": 0.0
    }
    defaults.update(kwargs)

    detection = VisionDetection(**defaults)
    session.add(detection)
    session.commit()
    session.refresh(detection)
    return detection


def create_test_alert(session: Session, **kwargs) -> Alert:
    """Helper to create a test Alert with custom fields."""
    defaults = {
        "severity": "info",
        "category": "system",
        "title": "Test Alert",
        "message": "This is a test alert",
        "source": "test"
    }
    defaults.update(kwargs)

    alert = Alert(**defaults)
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert


# Export helper functions
__all__ = [
    "test_db_engine",
    "test_db_session",
    "client",
    "sample_vision_detection",
    "sample_navtex_message",
    "sample_audio_anomaly",
    "sample_sensor_reading",
    "sample_voyage",
    "sample_alert",
    "mock_ollama_response",
    "mock_gemini_response",
    "mock_claude_response",
    "create_test_detection",
    "create_test_alert"
]
