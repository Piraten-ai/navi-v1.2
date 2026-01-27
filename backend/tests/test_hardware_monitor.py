"""Tests for hardware monitoring module."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest


def test_hardware_metrics_to_dict():
    """Test HardwareMetrics conversion to dictionary.
    
    Verifies that hardware metrics are correctly structured
    for JSON serialization and API responses.
    """
    from app.modules.hardware_monitor import HardwareMetrics
    
    # Create metrics with sample data
    metrics = HardwareMetrics(
        cpu_temp=45.5,
        gpu_temp=50.2,
        thermal_temp=42.0,
        fan_rpm=3200,
        fan_pwm_percent=55,
        ram_used=2048.0,
        ram_total=8192.0,
        ram_percent=25.0,
        power_watts=12.5,
        voltage=5.0,
        current=2.5,
        cpu_usage_percent=30.0,
        gpu_usage_percent=20.0,
        timestamp=datetime(2026, 1, 23, 12, 0, 0)
    )
    
    # Convert to dictionary
    result = metrics.to_dict()
    
    # Verify structure
    assert "temperatures" in result
    assert result["temperatures"]["cpu"] == 45.5
    assert result["temperatures"]["gpu"] == 50.2
    assert result["temperatures"]["thermal"] == 42.0
    
    assert "fan" in result
    assert result["fan"]["rpm"] == 3200
    assert result["fan"]["pwm_percent"] == 55
    
    assert "memory" in result
    assert result["memory"]["used_mb"] == 2048.0
    assert result["memory"]["total_mb"] == 8192.0
    assert result["memory"]["percent"] == 25.0
    
    assert "power" in result
    assert result["power"]["watts"] == 12.5
    assert result["power"]["voltage"] == 5.0
    assert result["power"]["current"] == 2.5
    
    assert "system" in result
    assert result["system"]["cpu_percent"] == 30.0
    assert result["system"]["gpu_percent"] == 20.0
    
    assert "timestamp" in result
    assert result["timestamp"] == "2026-01-23T12:00:00"


def test_hardware_monitor_mock_metrics():
    """Test hardware monitor with mock metrics on non-Jetson platform.
    
    Verifies that the monitor generates realistic mock data
    when running on non-Jetson hardware (development mode).
    """
    from app.modules.hardware_monitor import HardwareMonitor
    
    # Create monitor instance
    monitor = HardwareMonitor()
    
    # Should detect as non-Jetson on test system
    assert monitor._is_jetson == False
    
    # Update metrics (should use mock data)
    monitor._update_mock_metrics()
    
    # Verify mock metrics are generated
    assert monitor.metrics.cpu_temp is not None
    assert 30.0 < monitor.metrics.cpu_temp < 60.0  # Reasonable temp range
    
    assert monitor.metrics.gpu_temp is not None
    assert 35.0 < monitor.metrics.gpu_temp < 65.0
    
    assert monitor.metrics.fan_rpm is not None
    assert 2500 < monitor.metrics.fan_rpm < 3500  # Typical fan range
    
    assert monitor.metrics.ram_total == 8192.0
    assert monitor.metrics.ram_used is not None
    assert 0 < monitor.metrics.ram_used < monitor.metrics.ram_total
    
    # Verify metrics can be serialized
    metrics_dict = monitor.get_metrics()
    assert isinstance(metrics_dict, dict)
    assert "temperatures" in metrics_dict
    assert "fan" in metrics_dict
    assert "memory" in metrics_dict
