import math

import pytest

from app.modules.leeway_model import estimate_leeway


def test_zero_leeway_at_head_and_tail():
    # Zero when wind dead ahead (0 deg) or astern (180/-180 deg)
    for awa in [0.0, 180.0, -180.0]:
        val = estimate_leeway(wind_speed_kn=15.0, boat_speed_kn=6.0, rel_wind_deg=awa, k=1.0, max_deg=15.0)
        assert abs(val) < 1e-6


def test_symmetry_sign_convention():
    # Odd function: f(+x) == -f(-x)
    for awa in [15.0, 45.0, 60.0, 90.0, 135.0]:
        p = estimate_leeway(wind_speed_kn=12.0, boat_speed_kn=6.0, rel_wind_deg=awa, k=0.7, max_deg=20.0)
        n = estimate_leeway(wind_speed_kn=12.0, boat_speed_kn=6.0, rel_wind_deg=-awa, k=0.7, max_deg=20.0)
        assert pytest.approx(p, rel=1e-6, abs=1e-6) == -n


def test_magnitude_increases_with_wind():
    awa = 60.0
    low = estimate_leeway(wind_speed_kn=8.0, boat_speed_kn=6.0, rel_wind_deg=awa, k=0.5, max_deg=30.0)
    high = estimate_leeway(wind_speed_kn=16.0, boat_speed_kn=6.0, rel_wind_deg=awa, k=0.5, max_deg=30.0)
    assert abs(high) > abs(low)


def test_magnitude_decreases_with_boat_speed():
    awa = 60.0
    slow = estimate_leeway(wind_speed_kn=14.0, boat_speed_kn=4.0, rel_wind_deg=awa, k=0.6, max_deg=30.0)
    fast = estimate_leeway(wind_speed_kn=14.0, boat_speed_kn=8.0, rel_wind_deg=awa, k=0.6, max_deg=30.0)
    assert abs(slow) > abs(fast)


def test_clamping_to_max_deg():
    # Construct parameters that would exceed the max without clamping
    val = estimate_leeway(wind_speed_kn=30.0, boat_speed_kn=1.0, rel_wind_deg=90.0, k=1.5, max_deg=5.0)
    assert val == pytest.approx(5.0)
    val_neg = estimate_leeway(wind_speed_kn=30.0, boat_speed_kn=1.0, rel_wind_deg=-90.0, k=1.5, max_deg=5.0)
    assert val_neg == pytest.approx(-5.0)
