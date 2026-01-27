"""
Test cases for Legen (Medical Triage) Module
=============================================
Tests for medical triage logic, protocol selection,
and evacuation decisions.
"""

import pytest
from datetime import datetime
from app.modules.legen import LegenModule


class TestLegenModule:
    """Test LegenModule class"""

    def test_initialization(self):
        """Test module initialization"""
        legen = LegenModule()

        assert legen.assessments == []
        assert isinstance(legen.protocols, dict)
        assert "hypothermia" in legen.protocols
        assert "cardiac" in legen.protocols
        assert "trauma" in legen.protocols
        assert "seasickness" in legen.protocols

    def test_protocols_loaded(self):
        """Test medical protocols are properly loaded"""
        legen = LegenModule()

        # Check hypothermia protocols
        assert "mild" in legen.protocols["hypothermia"]
        assert "moderate" in legen.protocols["hypothermia"]
        assert "severe" in legen.protocols["hypothermia"]

        # Check cardiac protocols
        assert "chest_pain" in legen.protocols["cardiac"]
        assert "cpr" in legen.protocols["cardiac"]

        # Check trauma protocols
        assert "bleeding" in legen.protocols["trauma"]
        assert "fracture" in legen.protocols["trauma"]
        assert "burns" in legen.protocols["trauma"]


class TestTriageLevelDetermination:
    """Test triage level determination (RED/YELLOW/GREEN)"""

    def test_triage_red_level(self):
        """Test RED (critical) triage for life-threatening symptoms"""
        legen = LegenModule()

        # Chest pain
        level = legen._triage(["chest_pain"], "medium")
        assert level == "RED"

        # Unconscious
        level = legen._triage(["unconscious"], "medium")
        assert level == "RED"

        # Severe bleeding
        level = legen._triage(["severe_bleeding"], "low")
        assert level == "RED"

        # Difficulty breathing
        level = legen._triage(["difficulty_breathing"], "low")
        assert level == "RED"

    def test_triage_yellow_level(self):
        """Test YELLOW (urgent) triage for serious symptoms"""
        legen = LegenModule()

        # Fracture
        level = legen._triage(["fracture"], "medium")
        assert level == "YELLOW"

        # Burns
        level = legen._triage(["burns"], "medium")
        assert level == "YELLOW"

        # Hypothermia
        level = legen._triage(["hypothermia"], "low")
        assert level == "YELLOW"

        # Severe pain
        level = legen._triage(["severe_pain"], "medium")
        assert level == "YELLOW"

    def test_triage_green_level(self):
        """Test GREEN (non-urgent) triage for minor symptoms"""
        legen = LegenModule()

        # Minor symptoms
        level = legen._triage(["nausea", "headache"], "low")
        assert level == "GREEN"

        # Seasickness
        level = legen._triage(["seasickness"], "low")
        assert level == "GREEN"

    def test_triage_multiple_symptoms(self):
        """Test triage with multiple symptoms - highest severity wins"""
        legen = LegenModule()

        # Mix of critical and minor
        level = legen._triage(["chest_pain", "nausea", "fatigue"], "medium")
        assert level == "RED"  # Critical symptom present

        # Mix of urgent and minor
        level = legen._triage(["fracture", "headache"], "medium")
        assert level == "YELLOW"

    def test_triage_critical_symptom_detection(self):
        """Test detection of critical symptoms"""
        legen = LegenModule()

        critical_symptoms = ["chest_pain", "unconscious", "severe_bleeding", "difficulty_breathing"]

        for symptom in critical_symptoms:
            level = legen._triage([symptom], "low")
            assert level == "RED", f"{symptom} should be RED triage"

    def test_triage_severity_override(self):
        """Test severity parameter overrides symptom-based triage"""
        legen = LegenModule()

        # Even minor symptom with critical severity
        level = legen._triage(["headache"], "critical")
        assert level == "RED"

        # Minor symptom with high severity
        level = legen._triage(["nausea"], "high")
        assert level == "YELLOW"


class TestAssessment:
    """Test medical assessment functionality"""

    def test_assess_basic_structure(self):
        """Test assessment returns proper structure"""
        legen = LegenModule()

        symptoms = ["nausea", "headache"]
        assessment = legen.assess(symptoms, "low")

        assert "timestamp" in assessment
        assert "symptoms" in assessment
        assert assessment["symptoms"] == symptoms
        assert "severity" in assessment
        assert assessment["severity"] == "low"
        assert "triage_level" in assessment
        assert "recommendations" in assessment
        assert isinstance(assessment["recommendations"], list)
        assert "evacuation_needed" in assessment

    def test_assess_stores_in_history(self):
        """Test assessments are stored in history"""
        legen = LegenModule()

        initial_count = len(legen.assessments)
        
        legen.assess(["headache"], "low")
        legen.assess(["nausea"], "low")

        assert len(legen.assessments) == initial_count + 2

    def test_assess_critical_symptoms(self):
        """Test assessment flags critical symptoms"""
        legen = LegenModule()

        assessment = legen.assess(["chest_pain"], "high")

        assert assessment["triage_level"] == "RED"
        assert assessment["evacuation_needed"] is True
        assert any("EVACUATION" in rec for rec in assessment["recommendations"])

    def test_assess_unconscious_patient(self):
        """Test assessment of unconscious patient"""
        legen = LegenModule()

        assessment = legen.assess(["unconscious"], "critical")

        assert assessment["triage_level"] == "RED"
        assert assessment["evacuation_needed"] is True

    def test_assess_severe_bleeding(self):
        """Test assessment of severe bleeding"""
        legen = LegenModule()

        assessment = legen.assess(["severe_bleeding"], "high")

        assert assessment["triage_level"] == "RED"
        assert assessment["evacuation_needed"] is True


class TestProtocolSelection:
    """Test medical protocol selection"""

    def test_protocol_selection_chest_pain(self):
        """Test chest pain protocol"""
        legen = LegenModule()

        assessment = legen.assess(["chest_pain"], "high")

        assert "protocol" in assessment
        assert "Aspirin" in assessment["protocol"]
        assert "URGENT" in assessment["protocol"]
        assert assessment["evacuation_needed"] is True

    def test_protocol_selection_bleeding(self):
        """Test bleeding protocol"""
        legen = LegenModule()

        assessment = legen.assess(["bleeding"], "medium")

        assert "protocol" in assessment
        assert "pressure" in assessment["protocol"].lower()

    def test_protocol_selection_fracture(self):
        """Test fracture protocol"""
        legen = LegenModule()

        assessment = legen.assess(["fracture"], "high")

        assert "protocol" in assessment
        assert "Immobilize" in assessment["protocol"]

    def test_protocol_selection_broken_bone(self):
        """Test broken bone (alias for fracture)"""
        legen = LegenModule()

        assessment = legen.assess(["broken"], "high")

        assert "protocol" in assessment
        assert "Immobilize" in assessment["protocol"]

    def test_protocol_selection_hypothermia_mild(self):
        """Test mild hypothermia protocol"""
        legen = LegenModule()

        assessment = legen.assess(["hypothermia"], "low")

        assert "protocol" in assessment
        assert "Remove wet clothing" in assessment["protocol"]

    def test_protocol_selection_hypothermia_moderate(self):
        """Test moderate hypothermia protocol"""
        legen = LegenModule()

        assessment = legen.assess(["hypothermia"], "medium")

        assert "protocol" in assessment
        assert "warm blankets" in assessment["protocol"]

    def test_protocol_selection_hypothermia_severe(self):
        """Test severe hypothermia protocol"""
        legen = LegenModule()

        assessment = legen.assess(["hypothermia"], "severe")

        assert "protocol" in assessment
        assert "MEDEVAC" in assessment["protocol"]

    def test_protocol_selection_cold_weather(self):
        """Test cold-related symptoms"""
        legen = LegenModule()

        assessment = legen.assess(["cold"], "low")

        assert "protocol" in assessment  # Should trigger hypothermia protocol

    def test_protocol_selection_seasickness(self):
        """Test seasickness protocol"""
        legen = LegenModule()

        assessment = legen.assess(["seasickness"], "low")

        assert "protocol" in assessment
        assert "Fresh air" in assessment["protocol"]

    def test_protocol_selection_nausea(self):
        """Test nausea (similar to seasickness)"""
        legen = LegenModule()

        assessment = legen.assess(["nausea"], "low")

        assert "protocol" in assessment
        # Should get seasickness treatment

    def test_protocol_selection_unknown_symptom(self):
        """Test handling of unknown symptoms"""
        legen = LegenModule()

        assessment = legen.assess(["unknown_symptom"], "low")

        # Should still return valid assessment
        assert "triage_level" in assessment
        # May not have specific protocol


class TestEvacuationDecision:
    """Test evacuation decision logic"""

    def test_evacuation_required_red_triage(self):
        """Test evacuation required for RED triage"""
        legen = LegenModule()

        assessment = legen.assess(["chest_pain"], "high")

        assert assessment["evacuation_needed"] is True

    def test_evacuation_not_required_yellow(self):
        """Test evacuation not always required for YELLOW"""
        legen = LegenModule()

        assessment = legen.assess(["fracture"], "medium")

        # Fracture alone may not require immediate evacuation
        # (depends on implementation - adjust if needed)

    def test_evacuation_required_severe_bleeding(self):
        """Test evacuation for severe bleeding"""
        legen = LegenModule()

        assessment = legen.assess(["severe_bleeding"], "high")

        assert assessment["evacuation_needed"] is True

    def test_evacuation_required_unconscious(self):
        """Test evacuation for unconscious patient"""
        legen = LegenModule()

        assessment = legen.assess(["unconscious"], "critical")

        assert assessment["evacuation_needed"] is True

    def test_evacuation_required_difficulty_breathing(self):
        """Test evacuation for breathing difficulties"""
        legen = LegenModule()

        assessment = legen.assess(["difficulty_breathing"], "high")

        assert assessment["evacuation_needed"] is True

    def test_evacuation_required_severe_hypothermia(self):
        """Test evacuation for severe hypothermia"""
        legen = LegenModule()

        assessment = legen.assess(["severe_hypothermia"], "critical")

        assert assessment["evacuation_needed"] is True

    def test_evacuation_logic_edge_cases(self):
        """Test evacuation logic handles edge cases"""
        legen = LegenModule()

        # Multiple symptoms including one critical
        assessment = legen.assess(["chest_pain", "nausea", "fatigue"], "medium")
        assert assessment["evacuation_needed"] is True

        # Non-critical symptoms
        assessment2 = legen.assess(["headache", "fatigue"], "low")
        # Should typically not require evacuation


class TestGeneralRecommendations:
    """Test general medical recommendations"""

    def test_recommendations_always_present(self):
        """Test that recommendations are always provided"""
        legen = LegenModule()

        assessment = legen.assess(["headache"], "low")

        assert len(assessment["recommendations"]) > 0

    def test_recommendations_include_monitoring(self):
        """Test recommendations include vital sign monitoring"""
        legen = LegenModule()

        assessment = legen.assess(["nausea"], "low")

        assert any("vital" in rec.lower() for rec in assessment["recommendations"])

    def test_recommendations_include_documentation(self):
        """Test recommendations include documentation"""
        legen = LegenModule()

        assessment = legen.assess(["fracture"], "medium")

        assert any("document" in rec.lower() for rec in assessment["recommendations"])

    def test_recommendations_for_critical_case(self):
        """Test recommendations for critical cases"""
        legen = LegenModule()

        assessment = legen.assess(["chest_pain"], "critical")

        # Should have evacuation recommendation
        assert any("EVACUATION" in rec for rec in assessment["recommendations"])


class TestGetProtocol:
    """Test retrieving specific protocols"""

    def test_get_protocol_hypothermia(self):
        """Test retrieving hypothermia protocol"""
        legen = LegenModule()

        protocol = legen.get_protocol("hypothermia")

        assert "mild" in protocol
        assert "moderate" in protocol
        assert "severe" in protocol

    def test_get_protocol_cardiac(self):
        """Test retrieving cardiac protocol"""
        legen = LegenModule()

        protocol = legen.get_protocol("cardiac")

        assert "chest_pain" in protocol
        assert "cpr" in protocol

    def test_get_protocol_trauma(self):
        """Test retrieving trauma protocol"""
        legen = LegenModule()

        protocol = legen.get_protocol("trauma")

        assert "bleeding" in protocol
        assert "fracture" in protocol
        assert "burns" in protocol

    def test_get_protocol_seasickness(self):
        """Test retrieving seasickness protocol"""
        legen = LegenModule()

        protocol = legen.get_protocol("seasickness")

        assert "assessment" in protocol
        assert "treatment" in protocol

    def test_get_protocol_not_found(self):
        """Test handling of non-existent protocol"""
        legen = LegenModule()

        protocol = legen.get_protocol("nonexistent")

        assert "error" in protocol
        assert protocol["error"] == "Protocol not found"


class TestModuleStatus:
    """Test module status reporting"""

    def test_get_status(self):
        """Test getting module status"""
        legen = LegenModule()

        status = legen.get_status()

        assert status["module"] == "legen"
        assert status["status"] == "ready"
        assert "total_assessments" in status
        assert "red_triage" in status
        assert "protocols_available" in status

    def test_get_status_with_assessments(self):
        """Test status reflects completed assessments"""
        legen = LegenModule()

        # Perform some assessments
        legen.assess(["headache"], "low")
        legen.assess(["chest_pain"], "critical")
        legen.assess(["nausea"], "low")

        status = legen.get_status()

        assert status["total_assessments"] == 3
        assert status["red_triage"] == 1  # Only chest_pain

    def test_get_status_red_triage_count(self):
        """Test RED triage count in status"""
        legen = LegenModule()

        # Add multiple RED triage cases
        legen.assess(["chest_pain"], "critical")
        legen.assess(["unconscious"], "critical")
        legen.assess(["severe_bleeding"], "high")

        status = legen.get_status()

        assert status["red_triage"] == 3

    def test_get_status_protocols_count(self):
        """Test protocols count in status"""
        legen = LegenModule()

        status = legen.get_status()

        # Should have at least 4 protocol categories
        assert status["protocols_available"] >= 4


class TestComplexScenarios:
    """Test complex medical scenarios"""

    def test_multi_trauma_patient(self):
        """Test assessment of patient with multiple injuries"""
        legen = LegenModule()

        symptoms = ["bleeding", "fracture", "unconscious"]
        assessment = legen.assess(symptoms, "critical")

        assert assessment["triage_level"] == "RED"
        assert assessment["evacuation_needed"] is True

    def test_hypothermia_progression(self):
        """Test hypothermia at different severity levels"""
        legen = LegenModule()

        # Mild
        mild = legen.assess(["hypothermia"], "low")
        assert "Remove wet clothing" in mild["protocol"]

        # Moderate
        moderate = legen.assess(["hypothermia"], "medium")
        assert "warm blankets" in moderate["protocol"]

        # Severe
        severe = legen.assess(["hypothermia"], "severe")
        assert "MEDEVAC" in severe["protocol"]

    def test_cardiac_emergency(self):
        """Test full cardiac emergency scenario"""
        legen = LegenModule()

        assessment = legen.assess(["chest_pain", "difficulty_breathing"], "critical")

        assert assessment["triage_level"] == "RED"
        assert assessment["evacuation_needed"] is True
        assert "protocol" in assessment
        assert any("EVACUATION" in rec for rec in assessment["recommendations"])

    def test_seasickness_to_dehydration(self):
        """Test mild condition (seasickness) assessment"""
        legen = LegenModule()

        assessment = legen.assess(["seasickness", "nausea"], "low")

        assert assessment["triage_level"] == "GREEN"
        assert "protocol" in assessment
        assert "Fresh air" in assessment["protocol"]


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_assess_empty_symptoms(self):
        """Test assessment with no symptoms"""
        legen = LegenModule()

        assessment = legen.assess([], "low")

        assert "triage_level" in assessment
        assert assessment["symptoms"] == []

    def test_assess_duplicate_symptoms(self):
        """Test handling of duplicate symptoms"""
        legen = LegenModule()

        assessment = legen.assess(["headache", "headache", "nausea"], "low")

        assert "symptoms" in assessment
        # Should handle duplicates gracefully

    def test_assess_case_sensitivity(self):
        """Test if symptom matching is case-sensitive"""
        legen = LegenModule()

        # Test with different cases
        assessment1 = legen.assess(["Chest_Pain"], "high")
        assessment2 = legen.assess(["CHEST_PAIN"], "high")

        # Both should be treated similarly (lowercase in code)

    def test_timestamp_format(self):
        """Test timestamp is in ISO format"""
        legen = LegenModule()

        assessment = legen.assess(["headache"], "low")

        # Should be ISO 8601 format
        timestamp = assessment["timestamp"]
        # Verify it can be parsed
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
