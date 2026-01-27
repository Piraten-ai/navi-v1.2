"""
Vakten (The Guard) - Vision AI Module
Real-time vision processing for maritime threat detection
"""

import asyncio
from typing import List, Dict, Optional, TYPE_CHECKING
from datetime import datetime
import logging

# cv2 and numpy are imported lazily when needed to avoid import errors
# when these heavy ML dependencies are not installed (e.g., during unit tests)
if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)


class Detection:
    """Detection result from vision system"""

    def __init__(
        self,
        class_name: str,
        confidence: float,
        bbox: List[int],
        distance_m: Optional[float] = None,
        threat_score: float = 0.0,
    ):
        self.class_name = class_name
        self.confidence = confidence
        self.bbox = bbox  # [x1, y1, x2, y2]
        self.distance_m = distance_m
        self.threat_score = threat_score
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict:
        return {
            "class": self.class_name,
            "confidence": self.confidence,
            "bbox": self.bbox,
            "distance_m": self.distance_m,
            "threat_score": self.threat_score,
            "timestamp": self.timestamp.isoformat(),
        }


class VaktenModule:
    """Vision AI module for threat detection"""

    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode
        self.model = None
        self.camera = None
        self.running = False
        self.detections: List[Detection] = []

        # Detection classes for Arctic maritime environment
        self.classes = ["ice_floe", "ship", "person", "obstacle", "buoy", "whale", "seal", "debris"]

        logger.info(f"Vakten initialized (mock_mode={mock_mode})")

    async def initialize(self):
        """Initialize vision system"""
        try:
            if not self.mock_mode:
                # Try to load YOLO model
                try:
                    from ultralytics import YOLO

                    self.model = YOLO("yolov8n.pt")  # Nano model for speed
                    logger.info("YOLOv8 model loaded")
                except Exception as e:
                    logger.warning(f"Failed to load YOLO model: {e}, using mock mode")
                    self.mock_mode = True

                # Try to open camera
                try:
                    import cv2
                    self.camera = cv2.VideoCapture(0)  # /dev/video0
                    if not self.camera.isOpened():
                        raise Exception("Camera not available")
                    logger.info("Camera opened successfully")
                except Exception as e:
                    logger.warning(f"Failed to open camera: {e}, using mock mode")
                    self.mock_mode = True

            if self.mock_mode:
                logger.info("Running in MOCK MODE - generating synthetic detections")

        except Exception as e:
            logger.error(f"Failed to initialize Vakten: {e}")
            raise

    async def detect_threats(self, frame: Optional["np.ndarray"] = None) -> List[Detection]:
        """Run detection on a frame"""
        if self.mock_mode:
            return self._mock_detect()

        if frame is None and self.camera is not None:
            ret, frame = self.camera.read()
            if not ret:
                logger.error("Failed to read frame from camera")
                return []

        if frame is None:
            return []

        try:
            # Run YOLO detection
            results = self.model(frame, verbose=False)

            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()

                    # Map YOLO classes to our maritime classes
                    class_name = self._map_class(cls)

                    # Estimate distance (placeholder - would use depth estimation)
                    distance = self._estimate_distance(bbox)

                    # Calculate threat score
                    threat_score = self._calculate_threat_score(class_name, conf, distance)

                    detection = Detection(
                        class_name=class_name,
                        confidence=conf,
                        bbox=[int(x) for x in bbox],
                        distance_m=distance,
                        threat_score=threat_score,
                    )
                    detections.append(detection)

            self.detections = detections
            return detections

        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []

    def _mock_detect(self) -> List[Detection]:
        """Generate mock detections for testing"""
        import random

        mock_detections = []

        # Randomly generate 0-3 detections
        num_detections = random.randint(0, 3)

        for _ in range(num_detections):
            class_name = random.choice(self.classes)
            confidence = random.uniform(0.6, 0.95)
            x1, y1 = random.randint(0, 640), random.randint(0, 480)
            x2, y2 = x1 + random.randint(50, 200), y1 + random.randint(50, 200)
            distance = random.uniform(10, 500)
            threat_score = random.uniform(0.0, 1.0) if class_name in ["ice_floe", "ship"] else 0.0

            detection = Detection(
                class_name=class_name,
                confidence=confidence,
                bbox=[x1, y1, x2, y2],
                distance_m=distance,
                threat_score=threat_score,
            )
            mock_detections.append(detection)

        self.detections = mock_detections
        return mock_detections

    def _map_class(self, yolo_class: int) -> str:
        """Map YOLO class ID to maritime class"""
        # Mapping COCO classes to maritime classes
        yolo_to_maritime = {
            0: "person",  # person
            1: "obstacle",  # bicycle -> obstacle
            2: "obstacle",  # car -> obstacle
            8: "ship",  # boat -> ship
            # Add more mappings as needed
        }
        return yolo_to_maritime.get(yolo_class, "obstacle")

    def _estimate_distance(self, bbox: List[int]) -> float:
        """Estimate distance based on bounding box size (placeholder)"""
        # Simple heuristic: larger boxes are closer
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        area = width * height

        # Inverse relationship (larger area = closer)
        # This is a placeholder - real implementation would use depth estimation
        if area > 50000:
            return 10.0
        elif area >= 20000:
            return 50.0
        elif area >= 5000:
            return 100.0
        else:
            return 200.0

    def _calculate_threat_score(self, class_name: str, confidence: float, distance: Optional[float]) -> float:
        """Calculate threat score based on detection properties"""
        threat_weights = {
            "ice_floe": 0.8,
            "ship": 0.6,
            "person": 0.9,  # High threat if person in water
            "obstacle": 0.5,
            "debris": 0.3,
            "whale": 0.2,
            "seal": 0.1,
            "buoy": 0.0,
        }

        base_threat = threat_weights.get(class_name, 0.0)

        # Increase threat if close
        if distance is not None and distance < 50:
            distance_factor = 2.0
        elif distance is not None and distance < 100:
            distance_factor = 1.5
        else:
            distance_factor = 1.0

        threat_score = min(base_threat * confidence * distance_factor, 1.0)
        return threat_score

    async def detect_shadow_ship(self, ais_data: List[Dict]) -> Optional[Detection]:
        """Detect shadow ships (visual detection but no AIS signal)"""
        # Find ship detections
        ship_detections = [d for d in self.detections if d.class_name == "ship"]

        if not ship_detections:
            return None

        # Check if any ship detection lacks corresponding AIS data
        for detection in ship_detections:
            # In real implementation, would cross-reference with AIS data
            # For now, return high-threat detection if no AIS data provided
            if not ais_data:
                detection.threat_score = 1.0
                logger.warning(f"SHADOW SHIP detected: {detection.to_dict()}")
                return detection

        return None

    async def start(self):
        """Start continuous detection loop"""
        self.running = True
        logger.info("Vakten detection loop started")

        while self.running:
            await self.detect_threats()
            await asyncio.sleep(0.1)  # 10 FPS

    async def stop(self):
        """Stop detection loop"""
        self.running = False
        if self.camera:
            self.camera.release()
        logger.info("Vakten stopped")

    def get_status(self) -> Dict:
        """Get module status"""
        return {
            "module": "vakten",
            "status": "running" if self.running else "stopped",
            "mock_mode": self.mock_mode,
            "camera_available": self.camera is not None if not self.mock_mode else False,
            "model_loaded": self.model is not None if not self.mock_mode else False,
            "latest_detections": len(self.detections),
            "max_threat_score": max([d.threat_score for d in self.detections], default=0.0),
        }

    def get_detections(self) -> List[Dict]:
        """Get latest detections as dicts"""
        return [d.to_dict() for d in self.detections]


# Global instance
vakten = VaktenModule(mock_mode=False)  # Production: use real camera/YOLO
