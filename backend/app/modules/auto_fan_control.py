"""Automatic fan control using PID for thermal management.

This module implements a PID (Proportional-Integral-Derivative) controller
to automatically adjust fan speed based on temperature readings from the
hardware monitor. Designed for Jetson devices with PWM fan control.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Optional

try:
    import Jetson.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PIDState:
    """PID controller state."""
    
    setpoint: float  # Target temperature
    kp: float  # Proportional gain
    ki: float  # Integral gain
    kd: float  # Derivative gain
    
    integral: float = 0.0  # Integral accumulator
    last_error: float = 0.0  # Previous error for derivative
    last_time: float = 0.0  # Last update time
    
    def reset(self) -> None:
        """Reset PID state."""
        self.integral = 0.0
        self.last_error = 0.0
        self.last_time = time.time()


class PIDController:
    """PID controller for fan speed regulation."""
    
    def __init__(self, kp: float, ki: float, kd: float, setpoint: float):
        """Initialize PID controller.
        
        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            setpoint: Target value (temperature in Celsius)
        """
        self.state = PIDState(
            setpoint=setpoint,
            kp=kp,
            ki=ki,
            kd=kd
        )
        self.state.reset()
    
    def update(self, current_value: float, dt: Optional[float] = None) -> float:
        """Calculate PID output.
        
        Args:
            current_value: Current measured value (temperature)
            dt: Time delta since last update (optional, auto-calculated)
        
        Returns:
            Control output (PWM duty cycle 0-100)
        """
        # Calculate time delta if not provided
        if dt is None:
            current_time = time.time()
            if self.state.last_time > 0:
                dt = current_time - self.state.last_time
            else:
                dt = 0.0
            self.state.last_time = current_time
        
        # Calculate error
        error = self.state.setpoint - current_value
        
        # Proportional term
        p_term = self.state.kp * error
        
        # Integral term (with anti-windup)
        self.state.integral += error * dt
        # Clamp integral to prevent windup
        max_integral = 50.0  # Maximum contribution from integral
        self.state.integral = max(-max_integral, min(max_integral, self.state.integral))
        i_term = self.state.ki * self.state.integral
        
        # Derivative term
        if dt > 0:
            derivative = (error - self.state.last_error) / dt
        else:
            derivative = 0.0
        d_term = self.state.kd * derivative
        
        # Store error for next iteration
        self.state.last_error = error
        
        # Calculate output (inverted: higher temp → higher PWM)
        # If temp > setpoint, error is negative, so we need to increase fan speed
        output = 50.0 - (p_term + i_term + d_term)  # Base at 50%, adjust from there
        
        return output
    
    def reset(self) -> None:
        """Reset PID controller state."""
        self.state.reset()


class AutoFanControl:
    """Automatic fan speed control using PID."""
    
    def __init__(self):
        """Initialize automatic fan control."""
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._pwm: Optional[GPIO.PWM] = None
        
        self.pid = PIDController(
            kp=settings.FAN_PID_KP,
            ki=settings.FAN_PID_KI,
            kd=settings.FAN_PID_KD,
            setpoint=settings.FAN_TARGET_TEMP
        )
        
        self.current_pwm = 0
        self.current_temp = 0.0
        
        if not GPIO_AVAILABLE:
            logger.warning("Jetson.GPIO not available - fan control will use mock mode")
    
    async def start(self) -> None:
        """Start automatic fan control."""
        if not settings.FAN_CONTROL_ENABLED:
            logger.info("Fan control disabled in config")
            return
        
        try:
            # Initialize GPIO PWM
            if GPIO_AVAILABLE:
                self._init_pwm()
            
            # Reset PID state
            self.pid.reset()
            
            self._running = True
            self._task = asyncio.create_task(self._control_loop())
            logger.info(f"Fan control started (target: {settings.FAN_TARGET_TEMP}°C)")
            
        except Exception as e:
            logger.error(f"Failed to start fan control: {e}")
    
    async def stop(self) -> None:
        """Stop automatic fan control."""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        # Set fan to safe speed before cleanup
        if self._pwm:
            try:
                self._set_pwm(50)  # 50% duty cycle
                self._pwm.stop()
            except Exception as e:
                logger.warning(f"Error stopping PWM: {e}")
        
        # Cleanup GPIO
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
            except Exception as e:
                logger.warning(f"GPIO cleanup error: {e}")
        
        logger.info("Fan control stopped")
    
    def _init_pwm(self) -> None:
        """Initialize GPIO PWM for fan control."""
        try:
            GPIO.setmode(GPIO.TEGRA_SOC)
            GPIO.setup(settings.FAN_PWM_GPIO, GPIO.OUT, initial=GPIO.LOW)
            
            # Create PWM instance (25 kHz frequency is standard for fans)
            self._pwm = GPIO.PWM(settings.FAN_PWM_GPIO, 25000)
            self._pwm.start(0)  # Start with 0% duty cycle
            
            logger.info(f"Fan PWM initialized on GPIO{settings.FAN_PWM_GPIO}")
        except Exception as e:
            logger.error(f"Failed to initialize PWM: {e}")
            self._pwm = None
    
    async def _control_loop(self) -> None:
        """Main fan control loop."""
        logger.info("Fan control loop started")
        
        while self._running:
            try:
                # Get current temperature from hardware monitor
                temp = await self._get_current_temp()
                
                if temp is None:
                    logger.warning("No temperature data available")
                    await asyncio.sleep(settings.FAN_UPDATE_INTERVAL)
                    continue
                
                self.current_temp = temp
                
                # Calculate PID output
                pwm_output = self.pid.update(temp)
                
                # Clamp to min/max PWM
                pwm_duty = max(settings.FAN_MIN_PWM, min(settings.FAN_MAX_PWM, pwm_output))
                pwm_duty = int(pwm_duty)
                
                # Apply PWM
                self._set_pwm(pwm_duty)
                self.current_pwm = pwm_duty
                
                # Log control action
                error = settings.FAN_TARGET_TEMP - temp
                logger.debug(
                    f"Fan control: temp={temp:.1f}°C, target={settings.FAN_TARGET_TEMP:.1f}°C, "
                    f"error={error:.1f}°C, PWM={pwm_duty}%"
                )
                
                # Wait for next update
                await asyncio.sleep(settings.FAN_UPDATE_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in fan control loop: {e}")
                await asyncio.sleep(settings.FAN_UPDATE_INTERVAL)
    
    async def _get_current_temp(self) -> Optional[float]:
        """Get current temperature from hardware monitor.
        
        Returns:
            Current CPU temperature, or None if unavailable
        """
        try:
            # Import here to avoid circular dependency
            from app.modules.hardware_monitor import get_hardware_monitor
            
            monitor = get_hardware_monitor()
            metrics = monitor.metrics
            
            # Use CPU temp as primary, fallback to GPU or thermal
            if metrics.cpu_temp is not None:
                return metrics.cpu_temp
            elif metrics.gpu_temp is not None:
                return metrics.gpu_temp
            elif metrics.thermal_temp is not None:
                return metrics.thermal_temp
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading temperature: {e}")
            return None
    
    def _set_pwm(self, duty_cycle: int) -> None:
        """Set fan PWM duty cycle.
        
        Args:
            duty_cycle: PWM duty cycle (0-100)
        """
        if self._pwm:
            try:
                self._pwm.ChangeDutyCycle(duty_cycle)
            except Exception as e:
                logger.error(f"Error setting PWM: {e}")
        else:
            # Mock mode - just log
            logger.debug(f"[MOCK] Setting fan PWM to {duty_cycle}%")
    
    def get_status(self) -> dict:
        """Get fan control status.
        
        Returns:
            Status dictionary with current state
        """
        return {
            "running": self._running,
            "enabled": settings.FAN_CONTROL_ENABLED,
            "gpio_available": GPIO_AVAILABLE,
            "current_temp": self.current_temp,
            "target_temp": settings.FAN_TARGET_TEMP,
            "current_pwm": self.current_pwm,
            "pid_params": {
                "kp": settings.FAN_PID_KP,
                "ki": settings.FAN_PID_KI,
                "kd": settings.FAN_PID_KD
            },
            "pwm_limits": {
                "min": settings.FAN_MIN_PWM,
                "max": settings.FAN_MAX_PWM
            }
        }
    
    def set_target_temp(self, temp: float) -> None:
        """Update target temperature.
        
        Args:
            temp: New target temperature in Celsius
        """
        if 40.0 <= temp <= 85.0:
            self.pid.state.setpoint = temp
            logger.info(f"Fan control target temperature updated to {temp}°C")
        else:
            logger.warning(f"Invalid target temperature: {temp}°C (must be 40-85°C)")


# Module instance (not auto-started)
_fan_control: Optional[AutoFanControl] = None


def get_fan_control() -> AutoFanControl:
    """Get the fan control instance."""
    global _fan_control
    if _fan_control is None:
        _fan_control = AutoFanControl()
    return _fan_control
