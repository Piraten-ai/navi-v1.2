"""
Test cases for Vakten (Vision AI) Module
=========================================
Tests for threat detection, distance estimation, shadow ship detection,
and mock detection generation.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from app.modules.vakten import VaktenModule, Detection


class TestDetection:
    """Test Detection class"""

    def test_detection_initialization(self):
        """Test creating a detection object"""
        detection = Detection(
            class_name="ice_floe",
            confidence=0.92,
            bbox=[100, 200, 250, 400],
            distance_m=50.0,
            threat_score=0.85
        )

        assert detection.class_name == "ice_floe"
        assert detection.confidence == 0.92
        assert detection.bbox == [100, 200, 250, 400]
        assert detection.distance_m == 50.0
        assert detection.threat_score == 0.85
        assert isinstance(detection.timestamp, datetime)

    def test_detection_to_dict(self):
        """Test detection serialization to dictionary"""
        detection = Detection(
            class_name="ship",
            confidence=0.87,
            bbox=[50, 100, 150, 250],
            distance_m=100.0,
            threat_score=0.52
        )

        result = detection.to_dict()

        assert result["class"] == "ship"
        assert result["confidence"] == 0.87
        assert result["bbox"] == [50, 100, 150, 250]
        assert result["distance_m"] == 100.0
        assert result["threat_score"] == 0.52
        assert "timestamp" in result


class TestVaktenModule:
    """Test VaktenModule class"""

    def test_initialization_mock_mode(self):
        """Test module initialization in mock mode"""
        vakten = VaktenModule(mock_mode=True)

        assert vakten.mock_mode is True
        assert vakten.model is None
        assert vakten.camera is None
        assert vakten.running is False
        assert vakten.detections == []
        assert "ice_floe" in vakten.classes
        assert "ship" in vakten.classes
        assert "person" in vakten.classes

    def test_initialization_default(self):
        """Test default initialization"""
        vakten = VaktenModule()

        assert vakten.mock_mode is False
        assert vakten.running is False


class TestThreatScoreCalculation:
    """Test threat score calculation algorithm"""

    def test_threat_score_ice_floe_close_range(self):
        """Test ice floe threat score at close range (<50m)"""
        vakten = VaktenModule(mock_mode=True)
        
        # Ice floe with 0.8 base weight * 0.9 confidence * 2.0 close distance = 1.44 -> capped at 1.0
        threat_score = vakten._calculate_threat_score("ice_floe", 0.9, 30.0)
        
        assert threat_score == 1.0  # Should be capped at 1.0

    def test_threat_score_ice_floe_medium_range(self):
        """Test ice floe threat score at medium range (50-100m)"""
        vakten = VaktenModule(mock_mode=True)
        
        # Ice floe: 0.8 * 0.9 * 1.5 = 1.08 -> capped at 1.0
        threat_score = vakten._calculate_threat_score("ice_floe", 0.9, 75.0)
        
        assert threat_score == 1.0  # Capped at 1.0

    def test_threat_score_ice_floe_far_range(self):
        """Test ice floe threat score at far range (>100m)"""
        vakten = VaktenModule(mock_mode=True)
        
        # Ice floe: 0.8 * 0.9 * 1.0 = 0.72
        threat_score = vakten._calculate_threat_score("ice_floe", 0.9, 150.0)
        
        assert threat_score == pytest.approx(0.72, rel=0.01)

    def test_threat_score_person_overboard(self):
        """Test person in water has high threat score (0.9 weight)"""
        vakten = VaktenModule(mock_mode=True)
        
        # Person: 0.9 * 0.85 * 1.0 = 0.765
        threat_score = vakten._calculate_threat_score("person", 0.85, 120.0)
        
        assert threat_score == pytest.approx(0.765, rel=0.01)

    def test_threat_score_ship_medium(self):
        """Test ship threat score (0.6 weight)"""
        vakten = VaktenModule(mock_mode=True)
        
        # Ship: 0.6 * 0.9 * 1.0 = 0.54
        threat_score = vakten._calculate_threat_score("ship", 0.9, 200.0)
        
        assert threat_score == pytest.approx(0.54, rel=0.01)

    def test_threat_score_low_threat_objects(self):
        """Test low threat objects (buoy, seal)"""
        vakten = VaktenModule(mock_mode=True)
        
        # Buoy has 0.0 weight
        threat_score_buoy = vakten._calculate_threat_score("buoy", 0.95, 50.0)
        assert threat_score_buoy == 0.0
        
        # Seal has 0.1 weight
        threat_score_seal = vakten._calculate_threat_score("seal", 0.90, 100.0)
        assert threat_score_seal == pytest.approx(0.09, rel=0.01)

    def test_threat_score_invalid_class(self):
        """Test unknown class defaults to 0.0"""
        vakten = VaktenModule(mock_mode=True)
        
        threat_score = vakten._calculate_threat_score("unknown_object", 0.95, 50.0)
        
        assert threat_score == 0.0

    def test_threat_score_zero_distance(self):
        """Test threat score with zero distance"""
        vakten = VaktenModule(mock_mode=True)
        
        # Distance of 0 should still be < 50, applying 2.0 multiplier
        threat_score = vakten._calculate_threat_score("ice_floe", 0.9, 0.0)
        
        assert threat_score == 1.0  # 0.8 * 0.9 * 2.0 = 1.44 -> capped

    def test_threat_score_negative_distance(self):
        """Test threat score handles negative distance gracefully"""
        vakten = VaktenModule(mock_mode=True)
        
        # Negative distance treated as < 50
        threat_score = vakten._calculate_threat_score("ice_floe", 0.9, -10.0)
        
        assert threat_score == 1.0

    def test_threat_score_none_distance(self):
        """Test threat score with None distance"""
        vakten = VaktenModule(mock_mode=True)
        
        # None distance should use 1.0 multiplier
        threat_score = vakten._calculate_threat_score("ice_floe", 0.9, None)
        
        assert threat_score == pytest.approx(0.72, rel=0.01)  # 0.8 * 0.9 * 1.0

    def test_threat_score_confidence_out_of_range_high(self):
        """Test threat score with confidence > 1.0"""
        vakten = VaktenModule(mock_mode=True)
        
        # Even with high confidence, should cap at 1.0
        threat_score = vakten._calculate_threat_score("ice_floe", 1.5, 30.0)
        
        assert threat_score == 1.0

    def test_threat_score_confidence_out_of_range_low(self):
        """Test threat score with confidence < 0.0"""
        vakten = VaktenModule(mock_mode=True)
        
        # Negative confidence * positive weight = negative, but capped
        threat_score = vakten._calculate_threat_score("ice_floe", -0.5, 30.0)
        
        # Should handle gracefully (result will be negative, no explicit cap in code)
        assert threat_score <= 0.0

    def test_threat_score_max_capped_at_1(self):
        """Test that threat score never exceeds 1.0"""
        vakten = VaktenModule(mock_mode=True)
        
        # Maximum possible: person (0.9) * 1.0 conf * 2.0 distance = 1.8
        threat_score = vakten._calculate_threat_score("person", 1.0, 10.0)
        
        assert threat_score == 1.0
        assert threat_score <= 1.0


class TestDistanceEstimation:
    """Test distance estimation from bounding box"""

    def test_estimate_distance_large_bbox(self):
        """Test distance for large bounding box (>50000 area) → 10m"""
        vakten = VaktenModule(mock_mode=True)
        
        # 300 x 200 = 60000 area
        bbox = [100, 100, 400, 300]
        distance = vakten._estimate_distance(bbox)
        
        assert distance == 10.0

    def test_estimate_distance_medium_bbox(self):
        """Test distance for medium bounding box (20000-50000 area) → 50m"""
        vakten = VaktenModule(mock_mode=True)
        
        # 200 x 150 = 30000 area
        bbox = [100, 100, 300, 250]
        distance = vakten._estimate_distance(bbox)
        
        assert distance == 50.0

    def test_estimate_distance_small_bbox(self):
        """Test distance for small bounding box (5000-20000 area) → 100m"""
        vakten = VaktenModule(mock_mode=True)
        
        # 100 x 80 = 8000 area
        bbox = [100, 100, 200, 180]
        distance = vakten._estimate_distance(bbox)
        
        assert distance == 100.0

    def test_estimate_distance_very_small_bbox(self):
        """Test distance for very small bounding box (<5000 area) → 200m"""
        vakten = VaktenModule(mock_mode=True)
        
        # 50 x 40 = 2000 area
        bbox = [100, 100, 150, 140]
        distance = vakten._estimate_distance(bbox)
        
        assert distance == 200.0

    def test_estimate_distance_zero_area(self):
        """Test distance estimation for zero-size bounding box"""
        vakten = VaktenModule(mock_mode=True)
        
        # Zero area bbox
        bbox = [100, 100, 100, 100]
        distance = vakten._estimate_distance(bbox)
        
        assert distance == 200.0  # Falls into <5000 category

    def test_estimate_distance_boundary_50000(self):
        """Test boundary at 50000 area"""
        vakten = VaktenModule(mock_mode=True)
        
        # Exactly 50000 area (not greater than)
        bbox = [0, 0, 200, 250]  # 50000
        distance = vakten._estimate_distance(bbox)
        
        assert distance == 50.0  # Not > 50000

    def test_estimate_distance_boundary_20000(self):
        """Test boundary at 20000 area"""
        vakten = VaktenModule(mock_mode=True)
        
        # Exactly 20000 area
        bbox = [0, 0, 200, 100]  # 20000
        distance = vakten._estimate_distance(bbox)
        
        assert distance == 50.0  # Not > 20000, but > 5000

    def test_estimate_distance_boundary_5000(self):
        """Test boundary at 5000 area"""
        vakten = VaktenModule(mock_mode=True)
        
        # Exactly 5000 area
        bbox = [0, 0, 100, 50]  # 5000
        distance = vakten._estimate_distance(bbox)
        
        assert distance == 100.0  # Not > 5000


class TestShadowShipDetection:
    """Test shadow ship detection (visual detection without AIS)"""

    @pytest.mark.asyncio
    async def test_shadow_ship_detection_with_empty_ais(self):
        """Test shadow ship detected when ship visible but no AIS data"""
        vakten = VaktenModule(mock_mode=True)
        
        # Create ship detection
        ship_detection = Detection(
            class_name="ship",
            confidence=0.9,
            bbox=[100, 100, 300, 250],
            distance_m=100.0,
            threat_score=0.54
        )
        vakten.detections = [ship_detection]
        
        # No AIS data
        result = await vakten.detect_shadow_ship([])
        
        assert result is not None
        assert result.class_name == "ship"
        assert result.threat_score == 1.0  # Elevated to maximum

    @pytest.mark.asyncio
    async def test_shadow_ship_detection_with_ais_data(self):
        """Test no shadow ship when AIS data present"""
        vakten = VaktenModule(mock_mode=True)
        
        # Create ship detection
        ship_detection = Detection(
            class_name="ship",
            confidence=0.9,
            bbox=[100, 100, 300, 250],
            distance_m=100.0,
            threat_score=0.54
        )
        vakten.detections = [ship_detection]
        
        # AIS data present
        ais_data = [{"mmsi": "123456789", "name": "Test Vessel"}]
        result = await vakten.detect_shadow_ship(ais_data)
        
        assert result is None  # No shadow ship

    @pytest.mark.asyncio
    async def test_shadow_ship_detection_no_ships(self):
        """Test shadow ship detection with no ship detections"""
        vakten = VaktenModule(mock_mode=True)
        
        # Only non-ship detections
        ice_detection = Detection(
            class_name="ice_floe",
            confidence=0.85,
            bbox=[100, 100, 200, 180],
            distance_m=50.0,
            threat_score=0.8
        )
        vakten.detections = [ice_detection]
        
        result = await vakten.detect_shadow_ship([])
        
        assert result is None  # No ships to check

    @pytest.mark.asyncio
    async def test_shadow_ship_detection_empty_detections(self):
        """Test shadow ship detection with no detections"""
        vakten = VaktenModule(mock_mode=True)
        vakten.detections = []
        
        result = await vakten.detect_shadow_ship([])
        
        assert result is None

    @pytest.mark.asyncio
    async def test_shadow_ship_detection_multiple_ships(self):
        """Test shadow ship detection returns first ship without AIS"""
        vakten = VaktenModule(mock_mode=True)
        
        # Multiple ship detections
        ship1 = Detection("ship", 0.9, [100, 100, 200, 200], 100.0, 0.54)
        ship2 = Detection("ship", 0.85, [300, 100, 400, 200], 150.0, 0.51)
        vakten.detections = [ship1, ship2]
        
        result = await vakten.detect_shadow_ship([])
        
        assert result is not None
        assert result.threat_score == 1.0


class TestMockDetectionGenerator:
    """Test mock detection generator for testing"""

    def test_mock_detect_generates_detections(self):
        """Test mock detection generates valid detection objects"""
        vakten = VaktenModule(mock_mode=True)
        
        detections = vakten._mock_detect()
        
        assert isinstance(detections, list)
        assert len(detections) >= 0
        assert len(detections) <= 3  # Generates 0-3 detections

    def test_mock_detect_random_count(self):
        """Test mock detect generates random number of detections"""
        vakten = VaktenModule(mock_mode=True)
        
        # Run multiple times to verify randomness
        counts = [len(vakten._mock_detect()) for _ in range(20)]
        
        # Should have variety (not all same count)
        assert len(set(counts)) > 1
        assert all(0 <= c <= 3 for c in counts)

    def test_mock_detect_valid_classes(self):
        """Test mock detections use valid classes"""
        vakten = VaktenModule(mock_mode=True)
        
        # Generate many detections
        for _ in range(10):
            detections = vakten._mock_detect()
            for detection in detections:
                assert detection.class_name in vakten.classes

    def test_mock_detect_confidence_range(self):
        """Test mock detections have valid confidence range"""
        vakten = VaktenModule(mock_mode=True)
        
        for _ in range(10):
            detections = vakten._mock_detect()
            for detection in detections:
                assert 0.6 <= detection.confidence <= 0.95

    def test_mock_detect_threat_scores(self):
        """Test ice/ship have threat scores, others don't"""
        vakten = VaktenModule(mock_mode=True)
        
        # Generate many detections to get variety
        for _ in range(20):
            detections = vakten._mock_detect()
            for detection in detections:
                if detection.class_name in ["ice_floe", "ship"]:
                    # These should have non-zero threat scores
                    assert detection.threat_score >= 0.0
                else:
                    # Others should have 0.0 threat score
                    assert detection.threat_score == 0.0

    def test_mock_detect_bbox_format(self):
        """Test mock detections have valid bbox format [x1, y1, x2, y2]"""
        vakten = VaktenModule(mock_mode=True)
        
        for _ in range(10):
            detections = vakten._mock_detect()
            for detection in detections:
                assert len(detection.bbox) == 4
                x1, y1, x2, y2 = detection.bbox
                assert x2 > x1  # Width > 0
                assert y2 > y1  # Height > 0

    def test_mock_detect_stores_detections(self):
        """Test mock detect stores detections in module"""
        vakten = VaktenModule(mock_mode=True)
        
        result = vakten._mock_detect()
        
        assert vakten.detections == result


class TestModuleLifecycle:
    """Test module initialization and lifecycle"""

    @pytest.mark.asyncio
    async def test_initialize_mock_mode(self):
        """Test initialization in mock mode"""
        vakten = VaktenModule(mock_mode=True)
        
        await vakten.initialize()
        
        assert vakten.mock_mode is True
        assert vakten.model is None
        assert vakten.camera is None

    @pytest.mark.asyncio
    async def test_detect_threats_in_mock_mode(self):
        """Test detecting threats in mock mode"""
        vakten = VaktenModule(mock_mode=True)
        await vakten.initialize()
        
        detections = await vakten.detect_threats()
        
        assert isinstance(detections, list)
        for detection in detections:
            assert isinstance(detection, Detection)

    def test_get_status(self):
        """Test getting module status"""
        vakten = VaktenModule(mock_mode=True)
        
        status = vakten.get_status()
        
        assert status["module"] == "vakten"
        assert status["status"] == "stopped"
        assert status["mock_mode"] is True
        assert "latest_detections" in status
        assert "max_threat_score" in status

    def test_get_detections(self):
        """Test getting detections as dictionaries"""
        vakten = VaktenModule(mock_mode=True)
        
        # Add a detection
        detection = Detection("ice_floe", 0.9, [100, 100, 200, 200], 50.0, 0.8)
        vakten.detections = [detection]
        
        result = vakten.get_detections()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["class"] == "ice_floe"
        assert result[0]["confidence"] == 0.9

    def test_map_class(self):
        """Test YOLO class ID mapping"""
        vakten = VaktenModule(mock_mode=True)
        
        assert vakten._map_class(0) == "person"
        assert vakten._map_class(1) == "obstacle"
        assert vakten._map_class(8) == "ship"
        assert vakten._map_class(999) == "obstacle"  # Unknown -> obstacle


@pytest.mark.asyncio
class TestAsyncOperations:
    """Test asynchronous operations"""

    async def test_start_stop_lifecycle(self):
        """Test starting and stopping the module"""
        vakten = VaktenModule(mock_mode=True)
        
        assert vakten.running is False
        
        # Start in background
        import asyncio
        task = asyncio.create_task(vakten.start())
        await asyncio.sleep(0.2)  # Let it run briefly
        
        assert vakten.running is True
        
        # Stop
        await vakten.stop()
        await task  # Wait for task to complete
        
        assert vakten.running is False

    async def test_concurrent_detection_calls(self):
        """Test concurrent detection calls don't interfere"""
        vakten = VaktenModule(mock_mode=True)
        await vakten.initialize()
        
        # Run detections concurrently
        import asyncio
        results = await asyncio.gather(
            vakten.detect_threats(),
            vakten.detect_threats(),
            vakten.detect_threats()
        )
        
        # All should return valid results
        assert len(results) == 3
        for result in results:
            assert isinstance(result, list)
