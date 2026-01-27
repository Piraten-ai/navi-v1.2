import asyncio

import pytest
from app.core.config import settings

from app.modules.autopilot_controller import AutopilotController


def test_autopilot_rudder_with_leeway_bias():
    ctrl = AutopilotController()

    # Provider: heading 0 deg, stw 3 kn, wind true 30 deg at 20 kn equivalent
    def provider():
        return {
            "navigation": {
                "heading": 0.0,
                "speed_through_water": 3.0,
            },
            "environment": {
                "wind_direction": 30.0,
                "wind_speed": 20.0 / 1.94384,  # m/s
            },
        }

    ctrl.configure(signalk_provider=provider)
    ctrl.enable(desired_heading_deg=0.0)

    asyncio.run(ctrl._step_once())
    rud = ctrl.state.last_rudder_deg
    # Wind from starboard (AWA ~ +30) → positive leeway → steer starboard a bit
    assert rud > 0.0


def test_autopilot_clamping():
    ctrl = AutopilotController()

    # Provider: large error that should cause clamp
    def provider():
        return {
            "navigation": {
                "heading": 0.0,
                "speed_through_water": 0.5,
            },
            "environment": {
                "wind_direction": 90.0,
                "wind_speed": 30.0 / 1.94384,
            },
        }

    ctrl.configure(signalk_provider=provider)
    ctrl.enable(desired_heading_deg=45.0)  # 45 deg error + leeway
    asyncio.run(ctrl._step_once())
    rud = ctrl.state.last_rudder_deg
    assert abs(rud) <=  settings.AUTOPILOT_MAX_RUDDER_DEG
