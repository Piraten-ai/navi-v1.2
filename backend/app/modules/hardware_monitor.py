"""Hardware monitoring module for Jetson devices.

This module provides real-time monitoring of:
- CPU/GPU temperatures
- Fan RPM (via GPIO tachometer)
- Memory usage
- Power consumption (optional INA219 via I2C)

Designed for NVIDIA Jetson Orin Nano but gracefully degrades on other platforms.
"""

from __future__ import annotations

import asyncio
import logging
import platform
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# Optional dependencies
try:
    import Jetson.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False

try:
    from jtop import jtop
    JTOP_AVAILABLE = True
except ImportError:
    JTOP_AVAILABLE = False

try:
    import smbus2
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class HardwareMetrics:
    """Hardware monitoring metrics."""
    
    # Temperatures (Celsius)
    cpu_temp: Optional[float] = None
    gpu_temp: Optional[float] = None
    thermal_temp: Optional[float] = None
    
    # Fan
    fan_rpm: Optional[int] = None
    fan_pwm_percent: Optional[int] = None
    
    # Memory (MB)
    ram_used: Optional[float] = None
    ram_total: Optional[float] = None
    ram_percent: Optional[float] = None
    
    # Power (Watts, Volts, Amps)
    power_watts: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    
    # System
    cpu_usage_percent: Optional[float] = None
    gpu_usage_percent: Optional[float] = None
    
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "temperatures": {
                "cpu": self.cpu_temp,
                "gpu": self.gpu_temp,
                "thermal": self.thermal_temp
            },
            "fan": {
                "rpm": self.fan_rpm,
                "pwm_percent": self.fan_pwm_percent
            },
            "memory": {
                "used_mb": self.ram_used,
                "total_mb": self.ram_total,
                "percent": self.ram_percent
            },
            "power": {
                "watts": self.power_watts,
                "voltage": self.voltage,
                "current": self.current
            },
            "system": {
                "cpu_percent": self.cpu_usage_percent,
                "gpu_percent": self.gpu_usage_percent
            },
            "timestamp": self.timestamp.isoformat()
        }


class HardwareMonitor:
    """Hardware monitoring for Jetson devices."""
    
    def __init__(self):
        """Initialize hardware monitor."""
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.metrics = HardwareMetrics()
        
        # Fan tachometer state
        self._fan_pulse_count = 0
        self._fan_last_measurement = datetime.utcnow()
        
        # I2C bus for power monitoring
        self._i2c_bus: Optional[smbus2.SMBus] = None
        
        # jtop instance
        self._jtop_instance: Optional[jtop] = None
        
        self._is_jetson = self._detect_jetson()
        
        if not self._is_jetson:
            logger.warning("Not running on Jetson - hardware monitoring will use mock data")
    
    def _detect_jetson(self) -> bool:
        """Detect if running on Jetson hardware."""
        try:
            machine = platform.machine()
            # Jetson uses ARM architecture
            if machine not in ['aarch64', 'arm64']:
                return False
            
            # Check for Jetson-specific files
            try:
                with open('/etc/nv_tegra_release', 'r') as f:
                    return 'tegra' in f.read().lower()
            except FileNotFoundError:
                return False
        except Exception:
            return False
    
    async def start(self) -> None:
        """Start hardware monitoring."""
        if not settings.HARDWARE_MONITOR_ENABLED:
            logger.info("Hardware monitoring disabled in config")
            return
        
        try:
            # Initialize GPIO for fan tachometer
            if GPIO_AVAILABLE and self._is_jetson:
                self._init_gpio()
            
            # Initialize I2C for power monitoring
            if SMBUS_AVAILABLE and settings.HARDWARE_INA219_ENABLED:
                self._init_i2c()
            
            # Initialize jtop
            if JTOP_AVAILABLE and self._is_jetson:
                self._jtop_instance = jtop()
                self._jtop_instance.start()
                logger.info("jtop initialized for Jetson monitoring")
            
            self._running = True
            self._task = asyncio.create_task(self._monitor_loop())
            logger.info("Hardware monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start hardware monitor: {e}")
    
    async def stop(self) -> None:
        """Stop hardware monitoring."""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        # Cleanup GPIO
        if GPIO_AVAILABLE:
            try:
                GPIO.cleanup()
            except Exception as e:
                logger.warning(f"GPIO cleanup error: {e}")
        
        # Cleanup I2C
        if self._i2c_bus:
            try:
                self._i2c_bus.close()
            except Exception:
                pass
            self._i2c_bus = None
        
        # Cleanup jtop
        if self._jtop_instance:
            try:
                self._jtop_instance.close()
            except Exception:
                pass
            self._jtop_instance = None
        
        logger.info("Hardware monitoring stopped")
    
    def _init_gpio(self) -> None:
        """Initialize GPIO for fan tachometer."""
        try:
            GPIO.setmode(GPIO.TEGRA_SOC)
            GPIO.setup(settings.HARDWARE_FAN_TACH_GPIO, GPIO.IN)
            GPIO.add_event_detect(
                settings.HARDWARE_FAN_TACH_GPIO,
                GPIO.RISING,
                callback=self._fan_pulse_callback
            )
            logger.info(f"Fan tachometer initialized on GPIO{settings.HARDWARE_FAN_TACH_GPIO}")
        except Exception as e:
            logger.error(f"GPIO initialization failed: {e}")
    
    def _fan_pulse_callback(self, channel) -> None:
        """GPIO callback for fan tachometer pulses."""
        self._fan_pulse_count += 1
    
    def _init_i2c(self) -> None:
        """Initialize I2C bus for INA219 power monitoring."""
        try:
            self._i2c_bus = smbus2.SMBus(settings.HARDWARE_I2C_BUS)
            logger.info(f"I2C bus {settings.HARDWARE_I2C_BUS} initialized for power monitoring")
        except Exception as e:
            logger.error(f"I2C initialization failed: {e}")
            self._i2c_bus = None
    
    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        logger.info("Hardware monitor loop started")
        
        while self._running:
            try:
                # Update all metrics
                await self._update_metrics()
                
                # Log to InfluxDB if enabled
                if settings.HARDWARE_LOG_METRICS:
                    await self._log_metrics()
                
                # Wait for next poll interval
                await asyncio.sleep(settings.HARDWARE_POLL_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in hardware monitor loop: {e}")
                await asyncio.sleep(settings.HARDWARE_POLL_INTERVAL)
    
    async def _update_metrics(self) -> None:
        """Update all hardware metrics."""
        if self._jtop_instance and self._is_jetson:
            self._update_from_jtop()
        else:
            self._update_mock_metrics()
        
        # Update fan RPM from GPIO
        if GPIO_AVAILABLE and self._is_jetson:
            self._update_fan_rpm()
        
        # Update power from I2C
        if self._i2c_bus:
            self._update_power_ina219()
        
        self.metrics.timestamp = datetime.utcnow()
    
    def _update_from_jtop(self) -> None:
        """Update metrics from jtop (Jetson)."""
        try:
            if not self._jtop_instance or not self._jtop_instance.ok():
                return
            
            stats = self._jtop_instance.stats
            
            # Temperatures
            if 'Temp CPU' in stats:
                self.metrics.cpu_temp = stats['Temp CPU']
            if 'Temp GPU' in stats:
                self.metrics.gpu_temp = stats['Temp GPU']
            if 'Temp thermal' in stats:
                self.metrics.thermal_temp = stats['Temp thermal']
            
            # Memory
            ram = self._jtop_instance.memory
            if ram:
                self.metrics.ram_used = ram['RAM']['used'] / 1024  # Convert to MB
                self.metrics.ram_total = ram['RAM']['tot'] / 1024
                self.metrics.ram_percent = ram['RAM']['use']
            
            # CPU/GPU usage
            cpu = self._jtop_instance.cpu
            if cpu:
                self.metrics.cpu_usage_percent = cpu['total']['user'] + cpu['total']['system']
            
            gpu = self._jtop_instance.gpu
            if gpu:
                self.metrics.gpu_usage_percent = gpu.get('val', 0)
            
            # Fan PWM
            fan = self._jtop_instance.fan
            if fan:
                self.metrics.fan_pwm_percent = fan.get('speed', 0)
            
        except Exception as e:
            logger.error(f"Error reading jtop metrics: {e}")
    
    def _update_mock_metrics(self) -> None:
        """Generate mock metrics for non-Jetson platforms."""
        import random
        
        self.metrics.cpu_temp = 45.0 + random.uniform(-5, 5)
        self.metrics.gpu_temp = 50.0 + random.uniform(-5, 5)
        self.metrics.thermal_temp = 42.0 + random.uniform(-3, 3)
        
        self.metrics.fan_rpm = 3000 + random.randint(-200, 200)
        self.metrics.fan_pwm_percent = 50 + random.randint(-10, 10)
        
        self.metrics.ram_used = 2048.0 + random.uniform(-200, 200)
        self.metrics.ram_total = 8192.0
        self.metrics.ram_percent = (self.metrics.ram_used / self.metrics.ram_total) * 100
        
        self.metrics.cpu_usage_percent = 25.0 + random.uniform(-10, 10)
        self.metrics.gpu_usage_percent = 15.0 + random.uniform(-5, 5)
    
    def _update_fan_rpm(self) -> None:
        """Calculate fan RPM from GPIO pulses."""
        try:
            now = datetime.utcnow()
            elapsed = (now - self._fan_last_measurement).total_seconds()
            
            if elapsed >= 1.0:  # Update every second
                # Fan typically has 2 pulses per revolution
                rpm = (self._fan_pulse_count / 2.0) * (60.0 / elapsed)
                self.metrics.fan_rpm = int(rpm)
                
                # Reset counters
                self._fan_pulse_count = 0
                self._fan_last_measurement = now
                
        except Exception as e:
            logger.error(f"Error calculating fan RPM: {e}")
    
    def _update_power_ina219(self) -> None:
        """Read power metrics from INA219 via I2C."""
        try:
            if not self._i2c_bus:
                return
            
            # INA219 register addresses
            INA219_ADDRESS = 0x40
            INA219_REG_BUS_VOLTAGE = 0x02
            INA219_REG_CURRENT = 0x04
            INA219_REG_POWER = 0x03
            
            # Read voltage (register 0x02, 2 bytes)
            data = self._i2c_bus.read_word_data(INA219_ADDRESS, INA219_REG_BUS_VOLTAGE)
            voltage_raw = ((data & 0xFF) << 8) | (data >> 8)  # Swap bytes
            self.metrics.voltage = (voltage_raw >> 3) * 0.004  # LSB = 4mV
            
            # Read current (register 0x04, 2 bytes)
            data = self._i2c_bus.read_word_data(INA219_ADDRESS, INA219_REG_CURRENT)
            current_raw = ((data & 0xFF) << 8) | (data >> 8)
            if current_raw > 32767:
                current_raw -= 65536
            self.metrics.current = current_raw * 0.001  # LSB = 1mA
            
            # Calculate power
            if self.metrics.voltage and self.metrics.current:
                self.metrics.power_watts = self.metrics.voltage * self.metrics.current
            
        except Exception as e:
            logger.debug(f"Error reading INA219: {e}")
    
    async def _log_metrics(self) -> None:
        """Log metrics to InfluxDB (placeholder)."""
        # TODO: Implement InfluxDB logging when needed
        pass
    
    def get_metrics(self) -> dict:
        """Get current hardware metrics as dictionary."""
        return self.metrics.to_dict()
    
    def get_status(self) -> dict:
        """Get hardware monitor status."""
        return {
            "running": self._running,
            "is_jetson": self._is_jetson,
            "gpio_available": GPIO_AVAILABLE,
            "jtop_available": JTOP_AVAILABLE,
            "i2c_available": SMBUS_AVAILABLE and self._i2c_bus is not None,
            "last_update": self.metrics.timestamp.isoformat() if self.metrics.timestamp else None
        }


# Module instance (not auto-started)
_hardware_monitor: Optional[HardwareMonitor] = None


def get_hardware_monitor() -> HardwareMonitor:
    """Get the hardware monitor instance."""
    global _hardware_monitor
    if _hardware_monitor is None:
        _hardware_monitor = HardwareMonitor()
    return _hardware_monitor
