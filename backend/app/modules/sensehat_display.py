"""SenseHAT Display Module - Navi's Face on LED Matrix

Animates expressions and talking visuals on the 8x8 LED matrix while Navi speaks.
Includes sensors (temp, humidity, pressure) and joystick input.

Features:
- 8x8 RGB LED matrix display
- Animated face with eyes and mouth
- Real-time expression changes during speech
- Sensor data streaming (temperature, humidity, pressure)
- Joystick input for manual control
"""

import asyncio
import threading
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# Optional SenseHAT dependency with graceful fallback
try:
    from sense_hat import SenseHat
    SENSEHAT_AVAILABLE = True
except ImportError:
    SENSEHAT_AVAILABLE = False
    logger.warning("sense-hat not available – LED display disabled")


class FaceExpression(Enum):
    """Navi facial expressions"""
    NEUTRAL = "neutral"      # Relaxed, waiting
    HAPPY = "happy"          # Enthusiastic response
    THINKING = "thinking"    # Processing query
    CONFUSED = "confused"    # Uncertain response
    ALERT = "alert"          # Warning/important
    TALKING = "talking"      # Active speech
    CONCERNED = "concerned"  # Problem detected
    EXCITED = "excited"      # Positive discovery


# Color palette - RGB tuples for 8x8 display
COLORS = {
    "off": (0, 0, 0),
    "white": (255, 255, 255),
    "blue": (0, 100, 255),      # Navi blue
    "green": (0, 255, 100),
    "red": (255, 50, 50),
    "yellow": (255, 255, 0),
    "purple": (200, 0, 255),
    "cyan": (0, 255, 255),
}

# 8x8 LED face patterns
FACE_PATTERNS = {
    "neutral": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],  # Eyes
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 2, 2, 0, 0, 0],  # Mouth
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "happy": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],  # Eyes
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 2, 2, 0, 0, 0],  # Smile
        [0, 0, 2, 0, 0, 2, 0, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "talking": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],  # Eyes
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],  # Open mouth
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 0, 2, 3, 3, 2, 0, 0],
    ],
    "thinking": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],  # Looking up
        [0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],  # Neutral mouth
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "alert": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],  # Wide eyes
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],  # O mouth
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0, 0, 2, 0, 0, 2, 0, 0],
        [0, 0, 0, 2, 2, 0, 0, 0],
    ],
    "confused": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 2, 0, 0, 1, 0, 0],  # Mismatched eyes
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 2, 0, 0, 0],  # Confused mouth
        [0, 0, 0, 2, 0, 2, 0, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
}


@dataclass
class SensorReading:
    """Current sensor values from SenseHAT"""
    temperature_c: float
    humidity_percent: float
    pressure_mb: float
    timestamp: str


class SenseHATDisplay:
    """LED Matrix display controller for Navi face animations"""

    def __init__(self):
        self.available = SENSEHAT_AVAILABLE
        self.hat: Optional[SenseHat] = None
        self.current_expression = FaceExpression.NEUTRAL
        self.animation_task: Optional[asyncio.Task] = None
        self.is_animating = False
        self._lock = asyncio.Lock()
        self._broadcast: Optional[Callable[[Dict[str, Any]], None]] = None
        self._sensor_update_interval = 2.0  # seconds

        if self.available:
            try:
                self.hat = SenseHat()
                logger.info("✓ SenseHAT initialized")
            except Exception as e:
                logger.error(f"Failed to initialize SenseHAT: {e}")
                self.available = False

    def configure(self, broadcast: Optional[Callable[[Dict[str, Any]], None]] = None):
        """Configure broadcast callback for sensor data"""
        self._broadcast = broadcast

    async def set_expression(self, expression: FaceExpression) -> None:
        """Set facial expression"""
        async with self._lock:
            self.current_expression = expression
            await self._render_face(expression)
            logger.info(f"Expression: {expression.value}")

    async def _render_face(self, expression: FaceExpression) -> None:
        """Render face pattern on LED matrix"""
        if not self.available or not self.hat:
            return

        pattern = FACE_PATTERNS.get(expression.value, FACE_PATTERNS["neutral"])
        pixels = []

        for row in pattern:
            for cell in row:
                if cell == 0:
                    pixels.extend(COLORS["off"])
                elif cell == 1:
                    # Eyes - bright blue
                    pixels.extend(COLORS["blue"])
                elif cell == 2:
                    # Mouth - yellow/gold
                    pixels.extend(COLORS["yellow"])
                elif cell == 3:
                    # Tongue/inside - red
                    pixels.extend(COLORS["red"])

        try:
            self.hat.set_pixels(pixels)
        except Exception as e:
            logger.error(f"Failed to set LED pixels: {e}")

    async def animate_talking(self, duration_seconds: float = 3.0) -> None:
        """Animate talking mouth while speaking"""
        if not self.available:
            return

        self.is_animating = True
        start_time = asyncio.get_event_loop().time()

        try:
            while asyncio.get_event_loop().time() - start_time < duration_seconds:
                # Alternate between talking and slightly open
                await self.set_expression(FaceExpression.TALKING)
                await asyncio.sleep(0.2)

                await self.set_expression(FaceExpression.NEUTRAL)
                await asyncio.sleep(0.15)
        finally:
            self.is_animating = False
            await self.set_expression(self.current_expression)

    async def pulse_alert(self, duration_seconds: float = 2.0, color: str = "red") -> None:
        """Pulse the entire display for alerts"""
        if not self.available or not self.hat:
            return

        start_time = asyncio.get_event_loop().time()
        rgb = COLORS.get(color, COLORS["red"])

        try:
            while asyncio.get_event_loop().time() - start_time < duration_seconds:
                # Pulse on
                pixels = rgb * 64  # 8x8 = 64 pixels
                self.hat.set_pixels(pixels)
                await asyncio.sleep(0.3)

                # Pulse off
                pixels = COLORS["off"] * 64
                self.hat.set_pixels(pixels)
                await asyncio.sleep(0.2)
        finally:
            await self.set_expression(self.current_expression)

    async def sensor_loop(self) -> None:
        """Continuously read and broadcast sensor data"""
        if not self.available or not self.hat:
            return

        while True:
            try:
                reading = SensorReading(
                    temperature_c=self.hat.temp,
                    humidity_percent=self.hat.humidity,
                    pressure_mb=self.hat.pressure,
                    timestamp=datetime.utcnow().isoformat(),
                )

                if self._broadcast:
                    self._broadcast({
                        "type": "sensehat_sensors",
                        "temperature_c": reading.temperature_c,
                        "humidity_percent": reading.humidity_percent,
                        "pressure_mb": reading.pressure_mb,
                        "timestamp": reading.timestamp,
                    })

                await asyncio.sleep(self._sensor_update_interval)
            except Exception as e:
                logger.error(f"Sensor loop error: {e}")
                await asyncio.sleep(1)

    async def joystick_input_handler(self) -> None:
        """Handle joystick input from SenseHAT"""
        if not self.available or not self.hat:
            return

        while True:
            try:
                for event in self.hat.stick.get_events():
                    action = event.action
                    direction = event.direction

                    if self._broadcast:
                        self._broadcast({
                            "type": "sensehat_joystick",
                            "direction": direction,
                            "action": action,
                            "timestamp": datetime.utcnow().isoformat(),
                        })

                    logger.info(f"Joystick: {direction} ({action})")

                await asyncio.sleep(0.1)
            except Exception as e:
                logger.debug(f"Joystick error: {e}")
                await asyncio.sleep(0.5)

    def get_status(self) -> Dict[str, Any]:
        """Get current display status"""
        status = {
            "available": self.available,
            "current_expression": self.current_expression.value,
            "is_animating": self.is_animating,
        }

        if self.available and self.hat:
            try:
                status.update({
                    "temperature_c": self.hat.temp,
                    "humidity_percent": self.hat.humidity,
                    "pressure_mb": self.hat.pressure,
                })
            except Exception as e:
                logger.debug(f"Failed to read sensors: {e}")

        return status


# Singleton instance
sensehat_display = SenseHATDisplay()
