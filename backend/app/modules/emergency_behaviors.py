"""Emergency Behaviors Module

Implements failsafe autopilot responses for collision, loss-of-steering, and engine failure.
Config-gated; overrides normal autopilot when triggered.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmergencyMode(Enum):
    NORMAL = "normal"
    COLLISION_AVOIDANCE = "collision_avoidance"
    LOSS_OF_STEERING = "loss_of_steering"
    ENGINE_FAILURE = "engine_failure"


@dataclass
class EmergencyState:
    mode: EmergencyMode = EmergencyMode.NORMAL
    last_trigger_ts: float = 0.0
    trigger_reason: str = ""
    override_rudder_deg: Optional[float] = None
    recovery_time_remaining: float = 0.0


class EmergencyBehaviors:
    def __init__(self) -> None:
        self.state = EmergencyState()
        self.collision_distance_threshold_nm = 0.3  # Config: trigger at 0.3 NM (300 m)
        self.loss_of_steering_timeout_sec = 5.0  # No rudder movement for N seconds
        self.engine_failure_recovery_rudder = 5.0  # Slight starboard bias on engine failure
        self.recovery_duration_sec = 30.0  # Time to recover from emergency

    def check_collision_imminent(self, cpa_nm: float, time_to_cpa_sec: float) -> bool:
        """Detect imminent collision from AIS/Signal K CPA data."""
        return cpa_nm < self.collision_distance_threshold_nm and time_to_cpa_sec < 120

    def trigger_collision_avoidance(self, threat_bearing_deg: float) -> float:
        """Hard-over rudder away from threat."""
        # Steer away from threat bearing
        rudder = 30.0 if threat_bearing_deg > 180 else -30.0  # Arbitrary: hard-over starboard or port
        self.state.mode = EmergencyMode.COLLISION_AVOIDANCE
        self.state.override_rudder_deg = rudder
        self.state.trigger_reason = f"Collision avoidance: threat at {threat_bearing_deg:.1f}°"
        logger.warning(self.state.trigger_reason)
        return rudder

    def trigger_loss_of_steering(self) -> float:
        """Respond to detected steering loss."""
        rudder = 0.0  # Center rudder (may be stuck anyway)
        self.state.mode = EmergencyMode.LOSS_OF_STEERING
        self.state.override_rudder_deg = rudder
        self.state.trigger_reason = "Loss of steering detected; centering rudder and alerting"
        logger.error(self.state.trigger_reason)
        return rudder

    def trigger_engine_failure(self) -> float:
        """Respond to engine failure (loss of propulsion)."""
        # Try to maintain course with slight rudder and reduced thrust
        rudder = self.engine_failure_recovery_rudder
        self.state.mode = EmergencyMode.ENGINE_FAILURE
        self.state.override_rudder_deg = rudder
        self.state.trigger_reason = "Engine failure detected; setting minimal rudder, may need sail/drift recovery"
        logger.error(self.state.trigger_reason)
        return rudder

    def recover_to_normal(self) -> None:
        """Return to normal autopilot operation."""
        self.state.mode = EmergencyMode.NORMAL
        self.state.override_rudder_deg = None
        self.state.trigger_reason = ""
        logger.info("Emergency behavior resolved; returning to normal autopilot")

    def get_status(self) -> Dict[str, Any]:
        return {
            "mode": self.state.mode.value,
            "override_rudder_deg": self.state.override_rudder_deg,
            "trigger_reason": self.state.trigger_reason,
            "recovery_time_remaining": self.state.recovery_time_remaining,
            "collision_threshold_nm": self.collision_distance_threshold_nm,
            "loss_of_steering_timeout_sec": self.loss_of_steering_timeout_sec,
        }


# Singleton instance
emergency = EmergencyBehaviors()
