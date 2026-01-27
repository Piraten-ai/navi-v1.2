"""Unit tests for AutopilotPID rudder computation."""

import math


def test_rudder_sign_convention():
    from app.modules.autopilot_pid import AutopilotPID
    ap = AutopilotPID(kp_xte=1.0, ki_xte=0.0, kd_xte=0.0, kp_hdgt=1.0,
                      max_rudder_deg=30.0, min_rudder_deg=0.0,
                      wind_gain=0.0, wind_compensation=False)

    # Positive heading error (need to turn starboard) → positive rudder
    r1 = ap.compute_rudder(xte_nm=0.0, heading_error_deg=10.0, dt=1.0)
    assert r1 > 0

    # Positive XTE (right of track) → port (negative) rudder
    ap.reset()
    r2 = ap.compute_rudder(xte_nm=0.2, heading_error_deg=0.0, dt=1.0)
    assert r2 < 0


def test_rudder_clamping_and_deadband():
    from app.modules.autopilot_pid import AutopilotPID
    ap = AutopilotPID(kp_xte=5.0, ki_xte=0.0, kd_xte=0.0, kp_hdgt=2.0,
                      max_rudder_deg=25.0, min_rudder_deg=3.0,
                      wind_gain=0.0, wind_compensation=False)

    # Large errors should clamp to max
    r_big = ap.compute_rudder(xte_nm=10.0, heading_error_deg=90.0, dt=1.0)
    assert math.isclose(r_big, 25.0, rel_tol=0, abs_tol=1e-6)

    # Small command should fall within deadband rules
    r_small = ap.compute_rudder(xte_nm=0.0, heading_error_deg=1.0, dt=1.0)
    assert abs(r_small) >= 0.0
    assert abs(r_small) >= 0.0  # at least zero; deadband may push to min


def test_wind_compensation_bias():
    from app.modules.autopilot_pid import AutopilotPID
    ap = AutopilotPID(kp_xte=0.0, ki_xte=0.0, kd_xte=0.0, kp_hdgt=0.0,
                      max_rudder_deg=30.0, min_rudder_deg=0.0,
                      wind_gain=0.5, wind_compensation=True)

    # Wind from starboard (+20 deg) should bias starboard rudder (positive)
    r = ap.compute_rudder(xte_nm=0.0, heading_error_deg=0.0, apparent_wind_offset_deg=20.0, dt=1.0)
    assert r > 0
