"""
Ingeniøren (The Engineer) - System Diagnostics & Performance Monitoring Module
Gordon's Avatar - Health monitoring, fan control, leeway calculations
"""

import psutil
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
import asyncio

logger = logging.getLogger(__name__)


class IngeniørenModule:
    """System diagnostics, performance monitoring, and auto fan control"""

    def __init__(self):
        self.baseline_signature: Optional[np.ndarray] = None
        self.metrics_history: List[Dict] = []
        self.alerts: List[Dict] = []
        self.calibrated = False
        
        # Fan control settings
        self.fan_mode = "auto"  # "auto" or "manual"
        self.fan_speed = 50  # 0-100%
        
        # Physics state (Leeway/Drift calculations)
        self.current_drift_knot = 0.0
        self.leeway_angle = 0.0
        
        logger.info("INGENIØREN (Gordon) initialized - System Engineer & Physics")

    def get_diagnostics(self) -> Dict:
        """Get comprehensive system diagnostics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk metrics
            disk = psutil.disk_usage("/")

            # Process count
            try:
                process_count = len(psutil.pids())
            except:
                process_count = 0

            # Network metrics
            try:
                net_io = psutil.net_io_counters()
                network = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                }
            except (OSError, AttributeError):
                network = {"available": False}

            # Temperature (if available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    cpu_temp = None
                    for name, entries in temps.items():
                        if "cpu" in name.lower() or "core" in name.lower():
                            cpu_temp = entries[0].current if entries else None
                            break
                    temperature = {"cpu_temp_c": cpu_temp} if cpu_temp else {"available": False}
                else:
                    temperature = {"available": False}
            except (OSError, AttributeError):
                temperature = {"available": False}

            # Boot time
            try:
                boot_time = datetime.fromtimestamp(psutil.boot_time())
                uptime_seconds = (datetime.utcnow() - boot_time).total_seconds()
            except:
                uptime_seconds = 0

            diagnostics = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "usage_percent": float(cpu_percent) if cpu_percent is not None else 0.0,
                    "frequency_mhz": float(cpu_freq.current) if cpu_freq and cpu_freq.current else None,
                    "cores": int(cpu_count) if cpu_count else 1,
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent,
                },
                "swap": {
                    "total_gb": round(swap.total / (1024**3), 2),
                    "used_gb": round(swap.used / (1024**3), 2),
                    "usage_percent": swap.percent,
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": disk.percent,
                },
                "network": network,
                "temperature": temperature,
                "system": {
                    "process_count": process_count,
                    "uptime_seconds": uptime_seconds,
                    "boot_time": boot_time.isoformat() if uptime_seconds > 0 else None,
                },
                "fan": {
                    "mode": self.fan_mode,
                    "speed": self.fan_speed,
                },
                "physics": {
                    "leeway_angle_deg": round(self.leeway_angle, 2),
                    "drift_speed_knot": round(self.current_drift_knot, 2),
                },
            }

            # Check for alerts
            self._check_thresholds(diagnostics)

            # Store in history (keep last 1000)
            self.metrics_history.append(diagnostics)
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)

            return diagnostics

        except Exception as e:
            logger.error(f"Failed to get diagnostics: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

    def _check_thresholds(self, diagnostics: Dict):
        """Check if any metrics exceed thresholds and auto-adjust fan"""
        alerts = []

        # CPU threshold
        cpu_usage = diagnostics["cpu"]["usage_percent"]
        if cpu_usage > 90:
            alerts.append({
                "type": "CPU_CRITICAL",
                "message": f"CPU usage at {cpu_usage}%",
                "severity": "CRITICAL",
                "timestamp": diagnostics["timestamp"],
            })
            self._set_fan_speed(100)
        elif cpu_usage > 75:
            alerts.append({
                "type": "CPU_HIGH",
                "message": f"CPU usage at {cpu_usage}%",
                "severity": "WARNING",
                "timestamp": diagnostics["timestamp"],
            })
            self._set_fan_speed(80)
        else:
            self._set_fan_speed(50)

        # Memory threshold
        if diagnostics["memory"]["usage_percent"] > 85:
            alerts.append({
                "type": "MEMORY_HIGH",
                "message": f"Memory usage at {diagnostics['memory']['usage_percent']}%",
                "severity": "WARNING",
                "timestamp": diagnostics["timestamp"],
            })

        # Disk threshold
        if diagnostics["disk"]["usage_percent"] > 90:
            alerts.append({
                "type": "DISK_CRITICAL",
                "message": f"Disk usage at {diagnostics['disk']['usage_percent']}%",
                "severity": "CRITICAL",
                "timestamp": diagnostics["timestamp"],
            })

        # Temperature threshold
        if "cpu_temp_c" in diagnostics["temperature"] and diagnostics["temperature"]["cpu_temp_c"]:
            temp = diagnostics["temperature"]["cpu_temp_c"]
            if temp > 85:
                alerts.append({
                    "type": "TEMPERATURE_CRITICAL",
                    "message": f"CPU temperature at {temp}°C - COOLING REQUIRED",
                    "severity": "CRITICAL",
                    "timestamp": diagnostics["timestamp"],
                })
                self._set_fan_speed(100)
            elif temp > 75:
                alerts.append({
                    "type": "TEMPERATURE_WARNING",
                    "message": f"CPU temperature at {temp}°C",
                    "severity": "WARNING",
                    "timestamp": diagnostics["timestamp"],
                })
                self._set_fan_speed(90)

        self.alerts.extend(alerts)

        # Keep only recent alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]

    def _set_fan_speed(self, speed: int):
        """Set fan speed (0-100%)"""
        if self.fan_mode == "auto":
            self.fan_speed = max(0, min(100, speed))
            logger.info(f"Auto fan adjusted to {self.fan_speed}%")

    def update_leeway(self, wind_speed: float, wind_angle: float, boat_speed: float):
        """Calculate leeway based on wind/speed physics"""
        # Simple formula: Leeway ~ K * Wind / Speed^2
        if boat_speed > 1.0:
            self.leeway_angle = (wind_speed * 3.0) / (boat_speed * boat_speed)
            self.leeway_angle = min(self.leeway_angle, 15.0)  # Cap at 15 degrees
        else:
            self.leeway_angle = 0.0
        
        self.current_drift_knot = wind_speed * 0.03  # 3% of wind speed
        logger.debug(f"Leeway updated: {self.leeway_angle}° drift: {self.current_drift_knot}kt")

    def get_health_status(self) -> Dict:
        """Get overall system health status"""
        if not self.metrics_history:
            return {"status": "unknown", "message": "No metrics data"}

        latest = self.metrics_history[-1]
        
        # Calculate health score (0-100)
        health_score = 100
        factors = []
        
        cpu = latest["cpu"]["usage_percent"]
        if cpu > 90:
            health_score -= 40
            factors.append(f"CPU critical: {cpu}%")
        elif cpu > 75:
            health_score -= 20
            factors.append(f"CPU high: {cpu}%")
        
        mem = latest["memory"]["usage_percent"]
        if mem > 85:
            health_score -= 20
            factors.append(f"Memory high: {mem}%")
        
        disk = latest["disk"]["usage_percent"]
        if disk > 90:
            health_score -= 20
            factors.append(f"Disk full: {disk}%")
        
        if factors:
            status = "critical" if health_score < 30 else "warning" if health_score < 70 else "healthy"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "factors": factors,
            "cpu_usage": cpu,
            "memory_usage": mem,
            "disk_usage": disk,
            "fan_speed": self.fan_speed,
            "timestamp": latest["timestamp"],
        }

    def get_metrics(self, hours: int = 24) -> List[Dict]:
        """Get historical metrics"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]
        return recent_metrics

    def get_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """Get alerts, optionally filtered by severity"""
        if severity:
            return [a for a in self.alerts if a["severity"] == severity]
        return self.alerts

    def get_status(self) -> Dict:
        """Get module status"""
        recent_alerts = [
            a for a in self.alerts
            if datetime.fromisoformat(a["timestamp"]) > datetime.utcnow() - timedelta(hours=1)
        ]

        return {
            "module": "ingenioren",
            "status": "ready",
            "metrics_stored": len(self.metrics_history),
            "total_alerts": len(self.alerts),
            "alerts_last_hour": len(recent_alerts),
            "health": self.get_health_status(),
            "fan_speed": self.fan_speed,
            "physics": {
                "leeway_angle": self.leeway_angle,
                "drift_speed": self.current_drift_knot,
            },
        }


# Global instance
ingenioren = IngeniørenModule()
