"""
Tests for Ingeniøren (The Engineer) Module  
Tests system diagnostics, acoustic monitoring, threshold alerts, and optimization
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import numpy as np
from app.modules.ingenioren import IngeniørenModule


class TestIngeniørenModule:
    """Test initialization and basic setup"""

    def test_initialization(self):
        """Test module initializes correctly"""
        ing = IngeniørenModule()

        assert ing is not None
        assert ing.baseline_signature is None
        assert ing.metrics_history == []
        assert ing.alerts == []
        assert ing.calibrated is False


@patch('psutil.cpu_count')
@patch('psutil.cpu_freq')
@patch('psutil.swap_memory')
@patch('psutil.cpu_percent')
@patch('psutil.virtual_memory')
@patch('psutil.disk_usage')
class TestGetDiagnostics:
    """Test system diagnostics"""

    def test_get_diagnostics_basic_structure(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test diagnostics returns proper structure"""
        mock_cpu.return_value = 45.5
        mock_memory.return_value = Mock(percent=60.0, total=8589934592, used=5153960755, available=3435973836)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()
        diagnostics = ing.get_diagnostics()

        assert "timestamp" in diagnostics
        assert "cpu" in diagnostics
        assert "memory" in diagnostics
        assert "disk" in diagnostics
        assert "swap" in diagnostics

    def test_get_diagnostics_cpu_values(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test CPU values in diagnostics"""
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, total=8589934592, used=5153960755, available=3435973836)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()
        diagnostics = ing.get_diagnostics()

        assert diagnostics["cpu"]["usage_percent"] == 50.0
        assert diagnostics["cpu"]["cores"] == 4
        assert diagnostics["cpu"]["frequency_mhz"] == 2400.0

    def test_get_diagnostics_memory_values(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test memory values in diagnostics"""
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=75.0, total=17179869184, used=12884901888, available=4294967296)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()
        diagnostics = ing.get_diagnostics()

        assert diagnostics["memory"]["usage_percent"] == 75.0
        assert diagnostics["memory"]["total_gb"] == 16.0
        assert diagnostics["memory"]["used_gb"] == 12.0

    def test_get_diagnostics_disk_values(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test disk values in diagnostics"""
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, total=8589934592, used=5153960755, available=3435973836)
        mock_disk.return_value = Mock(percent=85.0, total=214748364800, used=182536308480, free=32212056320)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()
        diagnostics = ing.get_diagnostics()

        assert diagnostics["disk"]["usage_percent"] == 85.0
        assert diagnostics["disk"]["total_gb"] == 200.0


class TestThresholdChecking:
    """Test threshold alert generation"""

    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.swap_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_check_thresholds_cpu_high(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test CPU high threshold alert"""
        mock_cpu.return_value = 95.0
        mock_memory.return_value = Mock(percent=60.0, total=8589934592, used=5153960755, available=3435973836)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()
        diagnostics = ing.get_diagnostics()

        # Check that CPU alert was created
        assert len(ing.alerts) > 0
        cpu_alerts = [a for a in ing.alerts if a["type"] == "CPU_HIGH"]
        assert len(cpu_alerts) == 1

    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.swap_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_check_thresholds_memory_high(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test memory high threshold alert"""
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=90.0, total=8589934592, used=7730941132, available=858993459)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()
        diagnostics = ing.get_diagnostics()

        memory_alerts = [a for a in ing.alerts if a["type"] == "MEMORY_HIGH"]
        assert len(memory_alerts) == 1

    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.swap_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_check_thresholds_disk_high(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test disk high threshold alert"""
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, total=8589934592, used=5153960755, available=3435973836)
        mock_disk.return_value = Mock(percent=95.0, total=107374182400, used=102005473280, free=5368709120)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()
        diagnostics = ing.get_diagnostics()

        disk_alerts = [a for a in ing.alerts if a["type"] == "DISK_HIGH"]
        assert len(disk_alerts) == 1


class TestAcousticCalibration:
    """Test acoustic baseline calibration"""

    def test_calibrate_acoustic_creates_baseline(self):
        """Test acoustic calibration creates baseline"""
        ing = IngeniørenModule()

        result = ing.calibrate_acoustic()

        assert ing.baseline_signature is not None
        assert result["status"] == "calibrated"

    def test_calibrate_acoustic_sets_calibrated_flag(self):
        """Test calibration sets flag"""
        ing = IngeniørenModule()

        assert ing.calibrated is False

        ing.calibrate_acoustic()

        assert ing.calibrated is True

    def test_calibrate_acoustic_baseline_structure(self):
        """Test baseline has proper structure"""
        ing = IngeniørenModule()

        ing.calibrate_acoustic()

        assert isinstance(ing.baseline_signature, np.ndarray)
        assert len(ing.baseline_signature) == 1024

    def test_calibrate_acoustic_with_duration(self):
        """Test calibration with custom duration"""
        ing = IngeniørenModule()

        result = ing.calibrate_acoustic(duration_seconds=30)

        assert result["status"] == "calibrated"
        assert result["duration_seconds"] == 30


class TestAcousticAnomalyDetection:
    """Test acoustic anomaly detection"""

    def test_detect_anomaly_without_calibration(self):
        """Test anomaly detection requires calibration"""
        ing = IngeniørenModule()

        result = ing.detect_acoustic_anomaly()

        assert result["error"] is not None
        assert result["anomaly_detected"] is False

    def test_detect_anomaly_with_calibration(self):
        """Test anomaly detection after calibration"""
        ing = IngeniørenModule()

        ing.calibrate_acoustic()
        result = ing.detect_acoustic_anomaly()

        assert "anomaly_detected" in result
        assert "timestamp" in result

    def test_detect_anomaly_structure(self):
        """Test anomaly detection result structure"""
        ing = IngeniørenModule()

        ing.calibrate_acoustic()
        result = ing.detect_acoustic_anomaly()

        assert "anomaly_detected" in result
        assert "timestamp" in result

    def test_detect_anomaly_with_anomaly(self):
        """Test anomaly detection when anomaly present"""
        ing = IngeniørenModule()

        ing.calibrate_acoustic()

        # Try multiple times to hit the 10% mock probability
        anomaly_found = False
        for _ in range(20):
            result = ing.detect_acoustic_anomaly()
            if result["anomaly_detected"]:
                anomaly_found = True
                assert "type" in result
                assert "severity" in result
                assert "recommendation" in result
                break

        # At least one anomaly should be detected in 20 tries (probability > 0.999)
        assert anomaly_found


class TestSystemOptimization:
    """Test system optimization recommendations"""

    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.swap_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_optimize_basic_structure(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test optimization returns proper structure"""
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, total=8589934592, used=5153960755, available=3435973836)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()
        result = ing.optimize()

        assert "optimizations" in result
        assert "timestamp" in result
        assert isinstance(result["optimizations"], list)

    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.swap_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_optimize_high_cpu(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test optimization with high CPU usage"""
        mock_cpu.return_value = 95.0
        mock_memory.return_value = Mock(percent=60.0, total=8589934592, used=5153960755, available=3435973836)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()
        result = ing.optimize()

        # Should recommend CPU optimization
        optimizations = [o for o in result["optimizations"] if o["type"] == "cpu"]
        assert len(optimizations) > 0

    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.swap_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_optimize_high_memory(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test optimization with high memory usage"""
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=88.0, total=8589934592, used=7558961161, available=1030973430)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()
        result = ing.optimize()

        # Should recommend memory optimization
        optimizations = [o for o in result["optimizations"] if o["type"] == "memory"]
        assert len(optimizations) > 0


class TestMetricsHistory:
    """Test metrics history tracking"""

    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.swap_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_diagnostics_adds_to_history(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test diagnostics are added to history"""
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, total=8589934592, used=5153960755, available=3435973836)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()

        initial_length = len(ing.metrics_history)

        ing.get_diagnostics()

        assert len(ing.metrics_history) == initial_length + 1

    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.swap_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_metrics_all(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test getting all metrics from history"""
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=60.0, total=8589934592, used=5153960755, available=3435973836)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()

        ing.get_diagnostics()
        ing.get_diagnostics()
        ing.get_diagnostics()

        metrics = ing.get_metrics()

        assert len(metrics) == 3


class TestAlertsManagement:
    """Test alert management"""

    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.swap_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_alerts_stored_in_history(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test alerts are stored when triggered"""
        mock_cpu.return_value = 95.0
        mock_memory.return_value = Mock(percent=90.0, total=8589934592, used=7730941132, available=858993459)
        mock_disk.return_value = Mock(percent=95.0, total=107374182400, used=102005473280, free=5368709120)
        mock_swap.return_value = Mock(percent=80.0, total=4294967296, used=3435973836)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()

        ing.get_diagnostics()

        # Should have stored alerts
        assert len(ing.alerts) > 0

    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    @patch('psutil.swap_memory')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_alerts_all(self, mock_disk, mock_memory, mock_cpu, mock_swap, mock_cpu_freq, mock_cpu_count):
        """Test getting all alerts"""
        mock_cpu.return_value = 95.0
        mock_memory.return_value = Mock(percent=60.0, total=8589934592, used=5153960755, available=3435973836)
        mock_disk.return_value = Mock(percent=70.0, total=107374182400, used=75161927680, free=32212254720)
        mock_swap.return_value = Mock(percent=10.0, total=4294967296, used=429496729)
        mock_cpu_freq.return_value = Mock(current=2400.0)
        mock_cpu_count.return_value = 4

        ing = IngeniørenModule()

        ing.get_diagnostics()

        alerts = ing.get_alerts()

        assert len(alerts) > 0


class TestModuleStatus:
    """Test module status reporting"""

    def test_get_status(self):
        """Test getting module status"""
        ing = IngeniørenModule()

        status = ing.get_status()

        assert status["module"] == "ingenioren"
        assert status["status"] == "ready"
        assert "acoustic_calibrated" in status
        assert "metrics_stored" in status

    def test_get_status_tracks_calibration(self):
        """Test status reflects acoustic calibration"""
        ing = IngeniørenModule()

        status_before = ing.get_status()
        assert status_before["acoustic_calibrated"] is False

        ing.calibrate_acoustic()

        status_after = ing.get_status()
        assert status_after["acoustic_calibrated"] is True


class TestEdgeCases:
    """Test edge cases and error handling"""

    @patch('psutil.cpu_percent')
    def test_psutil_exception_handling(self, mock_cpu):
        """Test handling of psutil exceptions"""
        mock_cpu.side_effect = Exception("psutil error")

        ing = IngeniørenModule()

        # Should handle gracefully
        diagnostics = ing.get_diagnostics()

        # Should return error info
        assert "error" in diagnostics

    def test_acoustic_detection_without_data(self):
        """Test acoustic detection with no baseline"""
        ing = IngeniørenModule()

        result = ing.detect_acoustic_anomaly()

        assert result["error"] is not None
        assert result["anomaly_detected"] is False

    def test_get_metrics_empty_history(self):
        """Test getting metrics with empty history"""
        ing = IngeniørenModule()

        metrics = ing.get_metrics()

        assert metrics == []

    def test_get_alerts_no_alerts(self):
        """Test getting alerts when none exist"""
        ing = IngeniørenModule()

        alerts = ing.get_alerts()

        assert alerts == []
