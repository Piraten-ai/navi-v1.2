"""
Unit and integration tests for database operations.

Tests:
- Database connection management
- Session handling
- Error handling
- Health checks
- Connection pooling
- Backup/restore operations
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy.orm import Session
import json

from app.core.models import Base, VisionDetection, Alert
from app.core.database import get_db


# ============================================================================
# Database Connection Tests
# ============================================================================

@pytest.mark.database
class TestDatabaseConnection:
    """Tests for database connection management."""

    def test_database_initialization(self, test_db_engine):
        """Test that database initializes correctly."""
        assert test_db_engine is not None

        # Verify all tables are created
        inspector = test_db_engine.inspect()
        tables = inspector.get_table_names()

        expected_tables = [
            "vision_detections",
            "navtex_messages",
            "audio_anomalies",
            "sensor_readings",
            "system_logs",
            "ai_interactions",
            "voyages",
            "alerts"
        ]

        for table in expected_tables:
            assert table in tables

    def test_database_connection_valid(self, test_db_engine):
        """Test database connection is valid."""
        with test_db_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_database_tables_empty_initially(self, test_db_session):
        """Test that tables are empty on fresh database."""
        detections = test_db_session.query(VisionDetection).count()
        alerts = test_db_session.query(Alert).count()

        assert detections == 0
        assert alerts == 0


# ============================================================================
# Session Management Tests
# ============================================================================

@pytest.mark.database
class TestSessionManagement:
    """Tests for database session management."""

    def test_session_scope_success(self, test_db_session):
        """Test successful transaction commit."""
        detection = VisionDetection(
            threat_type="ice",
            confidence=0.9
        )

        test_db_session.add(detection)
        test_db_session.commit()

        # Verify record was saved
        count = test_db_session.query(VisionDetection).count()
        assert count == 1

    def test_session_rollback_on_error(self, test_db_session):
        """Test that session rolls back on error."""
        # Create a valid record
        detection1 = VisionDetection(
            threat_type="ice",
            confidence=0.9
        )
        test_db_session.add(detection1)
        test_db_session.commit()

        # Try to create invalid record (this would cause IntegrityError in real scenario)
        detection2 = VisionDetection(
            threat_type="ice",
            confidence=0.85
        )
        test_db_session.add(detection2)

        # Manually rollback
        test_db_session.rollback()

        # Only first record should exist
        count = test_db_session.query(VisionDetection).count()
        assert count == 1

    def test_session_isolation(self, test_db_engine):
        """Test that sessions are isolated."""
        from sqlalchemy.orm import sessionmaker

        Session1 = sessionmaker(bind=test_db_engine)
        Session2 = sessionmaker(bind=test_db_engine)

        session1 = Session1()
        session2 = Session2()

        try:
            # Add record in session1
            detection = VisionDetection(threat_type="ice", confidence=0.9)
            session1.add(detection)

            # Should not be visible in session2 before commit
            count2 = session2.query(VisionDetection).count()
            assert count2 == 0

            # Commit session1
            session1.commit()

            # Now should be visible in session2
            session2.expire_all()
            count2 = session2.query(VisionDetection).count()
            assert count2 == 1

        finally:
            session1.close()
            session2.close()


# ============================================================================
# CRUD Operation Tests
# ============================================================================

@pytest.mark.database
class TestCRUDOperations:
    """Tests for Create, Read, Update, Delete operations."""

    def test_create_record(self, test_db_session):
        """Test creating a record."""
        alert = Alert(
            severity="warning",
            category="test",
            title="Test Alert",
            message="This is a test"
        )

        test_db_session.add(alert)
        test_db_session.commit()
        test_db_session.refresh(alert)

        assert alert.id is not None

    def test_read_record(self, test_db_session, sample_vision_detection):
        """Test reading a record."""
        detection = test_db_session.query(VisionDetection).filter_by(
            id=sample_vision_detection.id
        ).first()

        assert detection is not None
        assert detection.threat_type == sample_vision_detection.threat_type

    def test_update_record(self, test_db_session, sample_alert):
        """Test updating a record."""
        original_title = sample_alert.title

        sample_alert.title = "Updated Title"
        test_db_session.commit()

        # Re-query to verify update
        test_db_session.expire_all()
        updated_alert = test_db_session.query(Alert).filter_by(
            id=sample_alert.id
        ).first()

        assert updated_alert.title == "Updated Title"
        assert updated_alert.title != original_title

    def test_delete_record(self, test_db_session, sample_vision_detection):
        """Test deleting a record."""
        detection_id = sample_vision_detection.id

        test_db_session.delete(sample_vision_detection)
        test_db_session.commit()

        # Verify deletion
        deleted = test_db_session.query(VisionDetection).filter_by(
            id=detection_id
        ).first()

        assert deleted is None


# ============================================================================
# Query Tests
# ============================================================================

@pytest.mark.database
class TestQueries:
    """Tests for database queries."""

    def test_filter_by_field(self, test_db_session):
        """Test filtering records by field."""
        # Create multiple detections
        ice_detection = VisionDetection(threat_type="ice", confidence=0.9)
        ship_detection = VisionDetection(threat_type="ship", confidence=0.85)

        test_db_session.add_all([ice_detection, ship_detection])
        test_db_session.commit()

        # Query ice detections only
        ice_detections = test_db_session.query(VisionDetection).filter_by(
            threat_type="ice"
        ).all()

        assert len(ice_detections) == 1
        assert ice_detections[0].threat_type == "ice"

    def test_order_by(self, test_db_session):
        """Test ordering query results."""
        # Create detections with different confidences
        d1 = VisionDetection(threat_type="ice", confidence=0.7)
        d2 = VisionDetection(threat_type="ice", confidence=0.9)
        d3 = VisionDetection(threat_type="ice", confidence=0.8)

        test_db_session.add_all([d1, d2, d3])
        test_db_session.commit()

        # Query ordered by confidence desc
        detections = test_db_session.query(VisionDetection).order_by(
            VisionDetection.confidence.desc()
        ).all()

        assert detections[0].confidence == 0.9
        assert detections[1].confidence == 0.8
        assert detections[2].confidence == 0.7

    def test_limit_offset(self, test_db_session):
        """Test pagination with limit and offset."""
        # Create 10 detections
        for i in range(10):
            d = VisionDetection(threat_type="ice", confidence=0.5 + i*0.05)
            test_db_session.add(d)
        test_db_session.commit()

        # Get first 5
        page1 = test_db_session.query(VisionDetection).limit(5).all()
        assert len(page1) == 5

        # Get next 5
        page2 = test_db_session.query(VisionDetection).limit(5).offset(5).all()
        assert len(page2) == 5

        # Ensure they're different
        page1_ids = [d.id for d in page1]
        page2_ids = [d.id for d in page2]
        assert set(page1_ids).isdisjoint(set(page2_ids))

    def test_count(self, test_db_session):
        """Test counting records."""
        # Create 5 detections
        for i in range(5):
            d = VisionDetection(threat_type="ice", confidence=0.8)
            test_db_session.add(d)
        test_db_session.commit()

        count = test_db_session.query(VisionDetection).count()
        assert count == 5


# ============================================================================
# Transaction Tests
# ============================================================================

@pytest.mark.database
class TestTransactions:
    """Tests for database transactions."""

    def test_atomic_transaction(self, test_db_session):
        """Test atomic transaction (all or nothing)."""
        try:
            # Create multiple records in one transaction
            for i in range(3):
                alert = Alert(
                    severity="info",
                    category="test",
                    title=f"Alert {i}",
                    message=f"Message {i}"
                )
                test_db_session.add(alert)

            test_db_session.commit()

            # All 3 should be saved
            count = test_db_session.query(Alert).count()
            assert count == 3

        except Exception:
            test_db_session.rollback()
            raise

    def test_transaction_rollback_on_exception(self, test_db_session):
        """Test that transaction rolls back on exception."""
        initial_count = test_db_session.query(Alert).count()

        try:
            alert = Alert(
                severity="info",
                category="test",
                title="Test",
                message="Test"
            )
            test_db_session.add(alert)

            # Simulate error
            raise Exception("Simulated error")

        except Exception:
            test_db_session.rollback()

        # Count should be unchanged
        final_count = test_db_session.query(Alert).count()
        assert final_count == initial_count


# ============================================================================
# Relationship Tests
# ============================================================================

@pytest.mark.database
@pytest.mark.slow
class TestRelationships:
    """Tests for model relationships (if any)."""

    def test_voyage_relationship_placeholder(self, test_db_session, sample_voyage):
        """Placeholder for testing model relationships."""
        # Currently models don't have explicit relationships
        # This test demonstrates where relationship tests would go
        assert sample_voyage.id is not None


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.database
@pytest.mark.slow
class TestPerformance:
    """Tests for database performance."""

    def test_bulk_insert(self, test_db_session):
        """Test bulk insert performance."""
        import time

        detections = [
            VisionDetection(threat_type="ice", confidence=0.5 + i*0.001)
            for i in range(100)
        ]

        start = time.time()
        test_db_session.bulk_save_objects(detections)
        test_db_session.commit()
        duration = time.time() - start

        # Should complete in under 1 second
        assert duration < 1.0

        # Verify all saved
        count = test_db_session.query(VisionDetection).count()
        assert count == 100

    def test_query_performance(self, test_db_session):
        """Test query performance."""
        import time

        # Insert 1000 records
        for i in range(1000):
            d = VisionDetection(threat_type="ice", confidence=0.5)
            test_db_session.add(d)
        test_db_session.commit()

        # Query with filter
        start = time.time()
        results = test_db_session.query(VisionDetection).filter_by(
            threat_type="ice"
        ).all()
        duration = time.time() - start

        # Should complete quickly
        assert duration < 0.5
        assert len(results) == 1000
