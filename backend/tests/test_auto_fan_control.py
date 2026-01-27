"""Tests for automatic fan control module."""

import pytest


def test_pid_controller_basic():
    """Test basic PID controller functionality.
    
    Verifies that PID controller calculates correct output
    based on proportional, integral, and derivative terms.
    """
    from app.modules.auto_fan_control import PIDController
    
    # Create PID controller with known gains
    pid = PIDController(kp=2.0, ki=0.5, kd=0.1, setpoint=60.0)
    
    # Test 1: Temperature below setpoint (should increase fan speed)
    # Current temp = 70°C, Target = 60°C, Error = -10°C
    output1 = pid.update(current_value=70.0, dt=1.0)
    
    # With high temp, output should be high to cool down
    # P-term: 2.0 * (-10) = -20
    # Output base is 50, so 50 - (-20 + I + D) = 70+ (approximately)
    assert output1 > 50, "Fan should speed up when temp is above target"
    
    # Test 2: Temperature at setpoint (should maintain)
    pid.reset()
    output2 = pid.update(current_value=60.0, dt=1.0)
    
    # At setpoint, error = 0, output should be near base (50%)
    assert 45 < output2 < 55, "Fan should maintain moderate speed at target temp"
    
    # Test 3: Temperature well below setpoint (should decrease fan speed)
    pid.reset()
    output3 = pid.update(current_value=50.0, dt=1.0)
    
    # With low temp, output should be lower
    # Error = +10°C (below target), P-term = 2.0 * 10 = 20
    # Output = 50 - (20) = 30 (approximately)
    assert output3 < 50, "Fan should slow down when temp is below target"


def test_pid_controller_integral_accumulation():
    """Test that PID integral term accumulates over time.
    
    Verifies integral windup prevention and steady-state error correction.
    """
    from app.modules.auto_fan_control import PIDController
    
    pid = PIDController(kp=1.0, ki=0.5, kd=0.0, setpoint=60.0)
    
    # Simulate sustained error (temp stays at 65°C)
    outputs = []
    for _ in range(5):
        output = pid.update(current_value=65.0, dt=1.0)
        outputs.append(output)
    
    # Output should increase over time due to integral accumulation
    assert outputs[4] > outputs[0], "Integral term should accumulate with sustained error"
    
    # Verify anti-windup is working (output doesn't explode)
    assert all(0 <= o <= 150 for o in outputs), "PID output should stay in reasonable range"


def test_pid_controller_reset():
    """Test PID controller state reset."""
    from app.modules.auto_fan_control import PIDController
    
    pid = PIDController(kp=2.0, ki=0.5, kd=0.1, setpoint=60.0)
    
    # Accumulate some state
    for _ in range(3):
        pid.update(current_value=70.0, dt=1.0)
    
    # Verify state has accumulated
    assert pid.state.integral != 0.0
    assert pid.state.last_error != 0.0
    
    # Reset
    pid.reset()
    
    # Verify state is cleared
    assert pid.state.integral == 0.0
    assert pid.state.last_error == 0.0


def test_fan_control_status():
    """Test fan control status reporting.
    
    Verifies that status dictionary contains all expected fields.
    """
    from app.modules.auto_fan_control import AutoFanControl
    
    fan_control = AutoFanControl()
    
    status = fan_control.get_status()
    
    # Verify required fields
    assert "running" in status
    assert "enabled" in status
    assert "gpio_available" in status
    assert "current_temp" in status
    assert "target_temp" in status
    assert "current_pwm" in status
    assert "pid_params" in status
    assert "pwm_limits" in status
    
    # Verify PID params structure
    assert "kp" in status["pid_params"]
    assert "ki" in status["pid_params"]
    assert "kd" in status["pid_params"]
    
    # Verify PWM limits structure
    assert "min" in status["pwm_limits"]
    assert "max" in status["pwm_limits"]
    
    # Verify not running by default
    assert status["running"] == False
