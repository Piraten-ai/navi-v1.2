import math
import time

import pytest

from app.modules.wind_estimator import WindEstimator


def test_ewma_smoothing_progressive_response():
    est = WindEstimator(method="ewma", ewma_alpha=0.2)
    t0 = time.time()
    # Start calm
    est.add_sample(awa_deg=0.0, aws_kn=5.0, timestamp=t0)
    s0 = est.get_state()
    assert s0["aws_kn"] == pytest.approx(5.0)
    # Step increase in wind speed
    for i in range(1, 6):
        est.add_sample(awa_deg=0.0, aws_kn=15.0, timestamp=t0 + i)
    sN = est.get_state()
    assert sN["aws_kn"] > 5.0 and sN["aws_kn"] < 15.0


def test_window_pruning_and_means():
    est = WindEstimator(method="window", window_seconds=10.0, gust_percentile=0.95)
    base = 1_000_000.0
    # Add samples over 30 seconds; only last 10 seconds should remain
    for i in range(30):
        est.add_sample(awa_deg=10.0, aws_kn=10.0, timestamp=base + i)
    # After last add, window holds samples from [20..29]
    s = est.get_state()
    assert s["window_size"] <= 11  # allow boundary
    assert s["aws_kn"] == pytest.approx(10.0)


def test_circular_mean_near_wrap():
    est = WindEstimator(method="window", window_seconds=60.0)
    t = 10_000.0
    # Values around the -180/180 wrap: 179 and -179 → mean near 180/-180
    est.add_sample(awa_deg=179.0, aws_kn=12.0, timestamp=t)
    est.add_sample(awa_deg=-179.0, aws_kn=12.0, timestamp=t + 1)
    s = est.get_state()
    # Accept either close to 180 or -180 due to normalization
    assert min(abs(s["awa_deg"] - 180.0), abs(s["awa_deg"] + 180.0)) < 3.0


def test_gust_detection_over_window():
    est = WindEstimator(method="window", window_seconds=20.0, gust_percentile=0.9)
    base = 5_000.0
    # Baseline 10kn for 10s
    for i in range(10):
        est.add_sample(awa_deg=30.0, aws_kn=10.0, timestamp=base + i)
    # Inject spikes
    for i in range(5):
        est.add_sample(awa_deg=30.0, aws_kn=20.0, timestamp=base + 10 + i)
    s = est.get_state()
    assert s["gust_kn"] >= 15.0
    assert s["gust_kn"] >= s["aws_kn"]
