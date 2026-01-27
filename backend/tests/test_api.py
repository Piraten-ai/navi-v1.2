"""
API endpoint tests for AADS backend.

Tests all FastAPI endpoints:
- Health checks
- Vision detection endpoints
- NAVTEX message endpoints
- Audio anomaly endpoints
- Sensor reading endpoints
- Alert endpoints
- Statistics endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json

from app.main import app
from app.core.models import VisionDetection, Alert, NAVTEXMessage, AudioAnomaly


# ============================================================================
# Health Check Tests
# ============================================================================

@pytest.mark.api
class TestHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check_endpoint(self, client):
        """Test basic health check."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] in ["healthy", "ok"]

    def test_health_check_response_format(self, client):
        """Test health check response format."""
        response = client.get("/health")
        data = response.json()

        # Should include basic health info
        assert isinstance(data, dict)


# ============================================================================
# Vision Detection Endpoints
# ============================================================================

@pytest.mark.api
class TestVisionDetectionEndpoints:
    """Tests for vision detection CRUD endpoints."""

    def test_create_detection(self, client):
        """Test creating a vision detection."""
        detection_data = {
            "threat_type": "ice",
            "confidence": 0.92,
            "distance_meters": 500.0,
            "bearing_degrees": 45.0,
            "notes": "Large iceberg detected"
        }

        response = client.post("/api/v1/detections", json=detection_data)

        assert response.status_code == 201
        data = response.json()

        assert data["threat_type"] == "ice"
        assert data["confidence"] == 0.92
        assert "id" in data

    def test_create_detection_invalid_data(self, client):
        """Test creating detection with invalid data."""
        invalid_data = {
            "threat_type": "invalid_type",
            "confidence": 1.5  # Invalid: > 1.0
        }

        response = client.post("/api/v1/detections", json=invalid_data)

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_list_detections(self, client, test_db_session):
        """Test listing all detections."""
        # Create sample detections
        for i in range(5):
            detection = VisionDetection(
                threat_type="ice",
                confidence=0.7 + i*0.05
            )
            test_db_session.add(detection)
        test_db_session.commit()

        response = client.get("/api/v1/detections")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 5

    def test_get_detection_by_id(self, client, sample_vision_detection):
        """Test getting a specific detection by ID."""
        detection_id = sample_vision_detection.id

        response = client.get(f"/api/v1/detections/{detection_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == detection_id
        assert data["threat_type"] == sample_vision_detection.threat_type

    def test_get_detection_not_found(self, client):
        """Test getting non-existent detection."""
        response = client.get("/api/v1/detections/99999")

        assert response.status_code == 404

    def test_update_detection(self, client, sample_vision_detection):
        """Test updating a detection."""
        detection_id = sample_vision_detection.id
        update_data = {
            "notes": "Updated notes"
        }

        response = client.patch(f"/api/v1/detections/{detection_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()

        assert data["notes"] == "Updated notes"

    def test_delete_detection(self, client, sample_vision_detection):
        """Test deleting a detection."""
        detection_id = sample_vision_detection.id

        response = client.delete(f"/api/v1/detections/{detection_id}")

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/v1/detections/{detection_id}")
        assert get_response.status_code == 404


# ============================================================================
# Alert Endpoints
# ============================================================================

@pytest.mark.api
class TestAlertEndpoints:
    """Tests for alert CRUD endpoints."""

    def test_create_alert(self, client):
        """Test creating an alert."""
        alert_data = {
            "severity": "warning",
            "category": "vision",
            "title": "Ice Detected",
            "message": "Iceberg detected ahead",
            "source": "vakten"
        }

        response = client.post("/api/v1/alerts", json=alert_data)

        assert response.status_code == 201
        data = response.json()

        assert data["severity"] == "warning"
        assert data["resolved"] == False

    def test_list_alerts(self, client, test_db_session):
        """Test listing alerts."""
        # Create sample alerts
        for i in range(3):
            alert = Alert(
                severity="info",
                category="test",
                title=f"Alert {i}",
                message=f"Message {i}"
            )
            test_db_session.add(alert)
        test_db_session.commit()

        response = client.get("/api/v1/alerts")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 3

    def test_filter_alerts_by_severity(self, client, test_db_session):
        """Test filtering alerts by severity."""
        # Create alerts with different severities
        Alert(severity="info", category="test", title="Info", message="Test")
        Alert(severity="warning", category="test", title="Warning", message="Test")
        Alert(severity="critical", category="test", title="Critical", message="Test")

        for alert in [
            Alert(severity="info", category="test", title="Info", message="Test"),
            Alert(severity="warning", category="test", title="Warning", message="Test"),
            Alert(severity="critical", category="test", title="Critical", message="Test")
        ]:
            test_db_session.add(alert)
        test_db_session.commit()

        response = client.get("/api/v1/alerts?severity=critical")

        assert response.status_code == 200
        data = response.json()

        assert all(alert["severity"] == "critical" for alert in data)

    def test_resolve_alert(self, client, sample_alert):
        """Test resolving an alert."""
        alert_id = sample_alert.id

        response = client.post(f"/api/v1/alerts/{alert_id}/resolve")

        assert response.status_code == 200
        data = response.json()

        assert data["resolved"] == True
        assert data["resolved_at"] is not None


# ============================================================================
# NAVTEX Message Endpoints
# ============================================================================

@pytest.mark.api
class TestNAVTEXEndpoints:
    """Tests for NAVTEX message endpoints."""

    def test_create_navtex_message(self, client):
        """Test creating a NAVTEX message."""
        message_data = {
            "message_type": "weather",
            "content": "GALE WARNING: Wind NE 30-40 knots",
            "source_station": "SVALBARD"
        }

        response = client.post("/api/v1/navtex", json=message_data)

        assert response.status_code == 201
        data = response.json()

        assert data["message_type"] == "weather"
        assert "GALE WARNING" in data["content"]

    def test_list_navtex_messages(self, client, test_db_session):
        """Test listing NAVTEX messages."""
        for i in range(3):
            msg = NAVTEXMessage(
                message_type="ice",
                content=f"Ice report {i}"
            )
            test_db_session.add(msg)
        test_db_session.commit()

        response = client.get("/api/v1/navtex")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 3


# ============================================================================
# Audio Anomaly Endpoints
# ============================================================================

@pytest.mark.api
class TestAudioAnomalyEndpoints:
    """Tests for audio anomaly endpoints."""

    def test_create_audio_anomaly(self, client):
        """Test creating an audio anomaly record."""
        anomaly_data = {
            "anomaly_type": "unusual_vibration",
            "confidence": 0.87,
            "severity": "medium",
            "detected_pattern": "irregular_knocking"
        }

        response = client.post("/api/v1/audio-anomalies", json=anomaly_data)

        assert response.status_code == 201
        data = response.json()

        assert data["anomaly_type"] == "unusual_vibration"
        assert data["severity"] == "medium"


# ============================================================================
# Statistics Endpoints
# ============================================================================

@pytest.mark.api
class TestStatisticsEndpoints:
    """Tests for statistics endpoints."""

    def test_get_detection_statistics(self, client, test_db_session):
        """Test getting detection statistics."""
        # Create sample detections
        for threat_type in ["ice", "ice", "ship", "whale"]:
            detection = VisionDetection(
                threat_type=threat_type,
                confidence=0.85
            )
            test_db_session.add(detection)
        test_db_session.commit()

        response = client.get("/api/v1/statistics/detections")

        assert response.status_code == 200
        data = response.json()

        assert "total" in data
        assert data["total"] == 4

    def test_get_alert_statistics(self, client, test_db_session):
        """Test getting alert statistics."""
        # Create sample alerts
        for severity in ["info", "warning", "warning", "critical"]:
            alert = Alert(
                severity=severity,
                category="test",
                title="Test",
                message="Test"
            )
            test_db_session.add(alert)
        test_db_session.commit()

        response = client.get("/api/v1/statistics/alerts")

        assert response.status_code == 200
        data = response.json()

        assert "total" in data


# ============================================================================
# Pagination Tests
# ============================================================================

@pytest.mark.api
class TestPagination:
    """Tests for pagination functionality."""

    def test_pagination_limit(self, client, test_db_session):
        """Test pagination with limit parameter."""
        # Create 20 detections
        for i in range(20):
            detection = VisionDetection(
                threat_type="ice",
                confidence=0.8
            )
            test_db_session.add(detection)
        test_db_session.commit()

        response = client.get("/api/v1/detections?limit=10")

        assert response.status_code == 200
        data = response.json()

        assert len(data) <= 10

    def test_pagination_offset(self, client, test_db_session):
        """Test pagination with offset parameter."""
        # Create 20 detections
        for i in range(20):
            detection = VisionDetection(
                threat_type="ice",
                confidence=0.8
            )
            test_db_session.add(detection)
        test_db_session.commit()

        # Get first page
        page1 = client.get("/api/v1/detections?limit=10&offset=0")
        page1_ids = [d["id"] for d in page1.json()]

        # Get second page
        page2 = client.get("/api/v1/detections?limit=10&offset=10")
        page2_ids = [d["id"] for d in page2.json()]

        # Pages should not overlap
        assert set(page1_ids).isdisjoint(set(page2_ids))


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.api
class TestErrorHandling:
    """Tests for API error handling."""

    def test_validation_error_response(self, client):
        """Test validation error response format."""
        invalid_data = {
            "threat_type": "ice",
            "confidence": 2.0  # Invalid: > 1.0
        }

        response = client.post("/api/v1/detections", json=invalid_data)

        assert response.status_code in [400, 422]
        data = response.json()

        assert "detail" in data or "error" in data

    def test_not_found_error_response(self, client):
        """Test 404 error response."""
        response = client.get("/api/v1/detections/99999")

        assert response.status_code == 404
        data = response.json()

        assert "detail" in data or "error" in data


# ============================================================================
# Integration Workflow Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
class TestWorkflows:
    """Tests for complete workflows."""

    def test_detection_alert_workflow(self, client):
        """Test complete detection to alert workflow."""
        # 1. Create a detection
        detection_data = {
            "threat_type": "ice",
            "confidence": 0.95,
            "distance_meters": 200.0
        }

        detection_response = client.post("/api/v1/detections", json=detection_data)
        assert detection_response.status_code == 201
        detection = detection_response.json()

        # 2. Create an alert for the detection
        alert_data = {
            "severity": "critical",
            "category": "vision",
            "title": "Ice Hazard",
            "message": f"Ice detected at {detection['distance_meters']}m",
            "source": "vakten"
        }

        alert_response = client.post("/api/v1/alerts", json=alert_data)
        assert alert_response.status_code == 201
        alert = alert_response.json()

        # 3. Resolve the alert
        resolve_response = client.post(f"/api/v1/alerts/{alert['id']}/resolve")
        assert resolve_response.status_code == 200

        # 4. Verify workflow completion
        final_alert = resolve_response.json()
        assert final_alert["resolved"] == True
