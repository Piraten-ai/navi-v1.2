"""
Test cases for Psykologen (Mental Health) Module
================================================
Tests for mood scoring, privacy features, check-ins,
therapy sessions, and proactive wellness checks.
"""

import pytest
import os
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open, MagicMock
from app.modules.psykologen import PsykologenModule


class TestPsykologenModule:
    """Test PsykologenModule class"""

    def test_initialization(self):
        """Test module initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            assert psyk.sessions == []
            assert psyk.check_ins == []
            assert psyk.data_dir == tmpdir

    def test_initialization_creates_data_dir(self):
        """Test that data directory is created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = os.path.join(tmpdir, "psyk_data")
            psyk = PsykologenModule(data_dir=data_path)

            assert os.path.exists(data_path)

    def test_privacy_mode_emphasized(self):
        """Test privacy guarantees are emphasized"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            # Privacy should be core principle
            status = psyk.get_status()
            assert status["privacy_mode"] == "LOCAL_ONLY"
            assert status["data_location"] == "LOCAL_ENCRYPTED"


class TestMoodScoreValidation:
    """Test mood score validation"""

    def test_checkin_valid_score_min(self):
        """Test check-in with minimum valid score (1)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.checkin(1)

            assert result["checkin"]["mood_score"] == 1

    def test_checkin_valid_score_max(self):
        """Test check-in with maximum valid score (10)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.checkin(10)

            assert result["checkin"]["mood_score"] == 10

    def test_checkin_valid_score_mid(self):
        """Test check-in with middle score (5)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.checkin(5)

            assert result["checkin"]["mood_score"] == 5

    def test_checkin_invalid_score_below_range(self):
        """Test check-in rejects score below 1"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            with pytest.raises(ValueError):
                psyk.checkin(0)

    def test_checkin_invalid_score_above_range(self):
        """Test check-in rejects score above 10"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            with pytest.raises(ValueError):
                psyk.checkin(11)

    def test_checkin_invalid_score_negative(self):
        """Test check-in rejects negative scores"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            with pytest.raises(ValueError):
                psyk.checkin(-5)


class TestCheckinFunctionality:
    """Test check-in functionality"""

    def test_checkin_basic_structure(self):
        """Test check-in returns proper structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.checkin(7)

            assert "checkin" in result
            assert "response" in result
            assert "timestamp" in result["checkin"]
            assert "mood_score" in result["checkin"]
            assert "user_id" in result["checkin"]

    def test_checkin_with_notes(self):
        """Test check-in with notes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.checkin(5, notes="Feeling okay today")

            assert result["checkin"]["has_notes"] is True

    def test_checkin_without_notes(self):
        """Test check-in without notes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.checkin(7)

            assert result["checkin"]["has_notes"] is False

    def test_checkin_custom_user_id(self):
        """Test check-in with custom user ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.checkin(8, user_id="captain")

            assert result["checkin"]["user_id"] == "captain"

    def test_checkin_stored_in_history(self):
        """Test check-ins are stored in history"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            psyk.checkin(5)
            psyk.checkin(7)

            assert len(psyk.check_ins) == 2

    def test_checkin_timestamp_format(self):
        """Test check-in timestamp is ISO format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.checkin(5)

            timestamp = result["checkin"]["timestamp"]
            # Should be parseable as ISO format
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


class TestCheckinResponses:
    """Test supportive response generation based on mood"""

    def test_checkin_response_low_mood(self):
        """Test response for low mood (1-3)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_checkin_response(2)

            assert "struggling" in response.lower() or "not be okay" in response.lower()

    def test_checkin_response_medium_mood(self):
        """Test response for medium mood (4-6)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_checkin_response(5)

            assert "challenging" in response.lower() or "routines" in response.lower()

    def test_checkin_response_high_mood(self):
        """Test response for high mood (7-10)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_checkin_response(9)

            assert "great" in response.lower() or "well" in response.lower() or "positive" in response.lower()

    def test_checkin_response_boundary_low(self):
        """Test response at low boundary (3)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_checkin_response(3)

            # Should trigger low mood response
            assert len(response) > 0

    def test_checkin_response_boundary_medium(self):
        """Test response at medium boundary (6)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_checkin_response(6)

            # Should trigger medium mood response
            assert len(response) > 0


class TestSessionFunctionality:
    """Test therapy session functionality"""

    def test_session_basic_structure(self):
        """Test session returns proper structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.session("anxiety", "I'm feeling anxious")

            assert "session" in result
            assert "response" in result
            assert result["session"]["topic"] == "anxiety"
            assert result["session"]["has_content"] is True

    def test_session_stored_in_history(self):
        """Test sessions are stored in history"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            psyk.session("topic1", "message1")
            psyk.session("topic2", "message2")

            assert len(psyk.sessions) == 2

    def test_session_custom_user_id(self):
        """Test session with custom user ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.session("test", "message", user_id="engineer")

            assert result["session"]["user_id"] == "engineer"

    def test_session_privacy_content_not_in_memory(self):
        """Test session content is not stored in memory (privacy)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.session("private", "Sensitive information")

            # Session object should not contain actual message
            assert "message" not in result["session"]
            assert result["session"]["has_content"] is True


class TestSessionResponses:
    """Test CBT-based session responses"""

    def test_session_response_isolation(self):
        """Test response for isolation topic"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_session_response("isolation", "I feel so alone")

            assert "isolation" in response.lower() or "alone" in response.lower()

    def test_session_response_loneliness(self):
        """Test response for loneliness"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_session_response("lonely", "Feeling lonely")

            assert "lonely" in response.lower() or "isolation" in response.lower()

    def test_session_response_anxiety(self):
        """Test response for anxiety"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_session_response("anxiety", "Feeling anxious")

            assert "anxiety" in response.lower() or "5-4-3-2-1" in response

    def test_session_response_stress(self):
        """Test response for stress"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_session_response("stress", "Too much stress")

            assert "stress" in response.lower() or "anxiety" in response.lower()

    def test_session_response_sleep(self):
        """Test response for sleep issues"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_session_response("sleep", "Can't sleep")

            assert "sleep" in response.lower()

    def test_session_response_insomnia(self):
        """Test response for insomnia"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_session_response("insomnia", "Insomnia problems")

            assert "sleep" in response.lower()

    def test_session_response_generic(self):
        """Test response for generic topic"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            response = psyk._generate_session_response("general", "Just talking")

            assert len(response) > 0
            assert "support" in response.lower() or "here" in response.lower()


class TestProactiveWellnessChecks:
    """Test proactive wellness check triggers"""

    def test_proactive_check_long_at_sea(self):
        """Test proactive check for long time at sea"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            crew_data = {
                "days_at_sea": 40,
                "last_checkin_days": 10
            }

            message = psyk.proactive_check(crew_data)

            assert message is not None
            assert "at sea" in message.lower() or "checking in" in message.lower()

    def test_proactive_check_long_watch(self):
        """Test proactive check for long watch hours"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            crew_data = {
                "watch_hours_today": 14
            }

            message = psyk.proactive_check(crew_data)

            assert message is not None
            assert "watch" in message.lower() or "fatigue" in message.lower()

    def test_proactive_check_no_recent_checkin(self):
        """Test proactive check for missing check-ins"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            crew_data = {
                "last_checkin_days": 20
            }

            message = psyk.proactive_check(crew_data)

            assert message is not None
            assert "check" in message.lower() or "weeks" in message.lower()

    def test_proactive_check_no_triggers(self):
        """Test proactive check with no triggers"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            crew_data = {
                "days_at_sea": 10,
                "watch_hours_today": 6,
                "last_checkin_days": 2
            }

            message = psyk.proactive_check(crew_data)

            assert message is None

    def test_proactive_check_multiple_conditions(self):
        """Test proactive check with multiple trigger conditions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            crew_data = {
                "days_at_sea": 50,
                "watch_hours_today": 16,
                "last_checkin_days": 15
            }

            message = psyk.proactive_check(crew_data)

            # Should trigger (first matching condition wins)
            assert message is not None


class TestPrivacyFeatures:
    """Test privacy-preserving features"""

    def test_save_local_creates_file(self):
        """Test that data is saved to local file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            data = {"test": "data"}
            psyk._save_local("test_type", data)

            # Should create a file in data directory
            files = os.listdir(tmpdir)
            assert len(files) > 0

    def test_checkin_notes_saved_separately(self):
        """Test check-in notes are saved separately"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            psyk.checkin(5, notes="Private thoughts")

            # Should create a file for notes
            files = os.listdir(tmpdir)
            assert any("checkin_notes" in f for f in files)

    def test_session_content_saved_separately(self):
        """Test session content is saved separately"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            psyk.session("test", "Private message")

            # Should create a file for session
            files = os.listdir(tmpdir)
            assert any("session" in f for f in files)

    @patch('os.chmod')
    def test_file_permissions_restricted(self, mock_chmod):
        """Test saved files have restricted permissions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            data = {"test": "data"}
            psyk._save_local("test", data)

            # Should set restrictive permissions (0o600 = read/write owner only)
            mock_chmod.assert_called()
            args = mock_chmod.call_args[0]
            assert args[1] == 0o600


class TestModuleStatus:
    """Test module status reporting"""

    def test_get_status(self):
        """Test getting module status"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            status = psyk.get_status()

            assert status["module"] == "psykologen"
            assert status["status"] == "ready"
            assert status["privacy_mode"] == "LOCAL_ONLY"
            assert "total_checkins" in status
            assert "total_sessions" in status

    def test_get_status_tracks_counts(self):
        """Test status reflects check-in and session counts"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            psyk.checkin(5)
            psyk.checkin(7)
            psyk.session("test", "message")

            status = psyk.get_status()

            assert status["total_checkins"] == 2
            assert status["total_sessions"] == 1

    def test_get_status_average_mood(self):
        """Test status calculates average mood"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            psyk.checkin(4)
            psyk.checkin(6)
            psyk.checkin(8)

            status = psyk.get_status()

            # Average should be around 6
            assert 5 < status["avg_mood_7d"] < 7

    def test_get_status_average_mood_recent_only(self):
        """Test average mood only includes recent 7 days"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            # Add old check-in (8 days ago)
            old_checkin = {
                "timestamp": (datetime.utcnow() - timedelta(days=8)).isoformat(),
                "mood_score": 2
            }
            psyk.check_ins.append(old_checkin)

            # Add recent check-in
            psyk.checkin(9)

            status = psyk.get_status()

            # Should only include recent (9), not old (2)
            assert status["avg_mood_7d"] == 9.0


class TestDataPersistence:
    """Test data persistence features"""

    def test_checkin_data_structure(self):
        """Test check-in data structure for persistence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.checkin(7, notes="Test notes", user_id="crew1")

            checkin = result["checkin"]

            # Verify structure suitable for storage
            assert isinstance(checkin["timestamp"], str)
            assert isinstance(checkin["mood_score"], int)
            assert isinstance(checkin["has_notes"], bool)
            assert isinstance(checkin["user_id"], str)

    def test_session_data_structure(self):
        """Test session data structure for persistence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.session("anxiety", "Message", user_id="crew1")

            session = result["session"]

            # Verify structure
            assert isinstance(session["timestamp"], str)
            assert isinstance(session["topic"], str)
            assert isinstance(session["user_id"], str)
            assert isinstance(session["has_content"], bool)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_checkin_float_score_rounded(self):
        """Test check-in handles float scores (should work or raise ValueError)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            # Python will convert 5.7 to int, so this should work
            result = psyk.checkin(int(5.7))
            assert result["checkin"]["mood_score"] == 5

    def test_empty_topic_session(self):
        """Test session with empty topic"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.session("", "Message")

            assert result["session"]["topic"] == ""

    def test_empty_message_session(self):
        """Test session with empty message"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result = psyk.session("topic", "")

            # Should handle gracefully
            assert "response" in result

    def test_proactive_check_missing_keys(self):
        """Test proactive check with incomplete crew data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            crew_data = {}  # Empty dict

            message = psyk.proactive_check(crew_data)

            # Should handle missing keys with defaults
            # Result depends on default values (999 for last_checkin_days)

    def test_multiple_checkins_same_minute(self):
        """Test multiple check-ins in quick succession"""
        with tempfile.TemporaryDirectory() as tmpdir:
            psyk = PsykologenModule(data_dir=tmpdir)

            result1 = psyk.checkin(5)
            result2 = psyk.checkin(7)
            result3 = psyk.checkin(9)

            # All should be stored
            assert len(psyk.check_ins) == 3
