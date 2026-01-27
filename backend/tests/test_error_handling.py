"""
Unit tests for the error handling system.

Tests:
- Custom exceptions
- Retry decorator
- Error context manager
- Safe execution wrapper
- Logging system
- Validation helpers
"""

import pytest
from datetime import datetime
import json
import logging
from unittest.mock import Mock, patch

# Assuming error_handling.py is in app/core/
# Adjust import path as needed
from app.core.error_handling import (
    AADSException,
    DatabaseError,
    VisionProcessingError,
    NavtexProcessingError,
    AudioProcessingError,
    SensorReadingError,
    ModuleInitializationError,
    ExternalServiceError,
    ConfigurationError,
    AuthenticationError,
    ValidationError,
    ResourceNotFoundError,
    retry,
    ErrorContext,
    safe_execute,
    validate_coordinates,
    validate_confidence_score,
    AADSLogger
)


# ============================================================================
# Exception Tests
# ============================================================================

@pytest.mark.unit
class TestCustomExceptions:
    """Tests for custom exception classes."""

    def test_aads_exception_basic(self):
        """Test basic AADSException creation."""
        error = AADSException("Test error")

        assert error.message == "Test error"
        assert error.error_code == "AADS_ERROR"
        assert error.details == {}
        assert isinstance(error.timestamp, datetime)

    def test_aads_exception_with_details(self):
        """Test AADSException with details."""
        details = {"key": "value", "number": 42}
        error = AADSException("Test error", details=details)

        assert error.details == details

    def test_aads_exception_to_dict(self):
        """Test AADSException to_dict method."""
        error = AADSException("Test", details={"foo": "bar"})
        error_dict = error.to_dict()

        assert error_dict["error_code"] == "AADS_ERROR"
        assert error_dict["message"] == "Test"
        assert error_dict["details"] == {"foo": "bar"}
        assert "timestamp" in error_dict

    def test_database_error(self):
        """Test DatabaseError exception."""
        error = DatabaseError("Connection failed", details={"host": "localhost"})

        assert error.error_code == "DATABASE_ERROR"
        assert error.message == "Connection failed"

    def test_vision_processing_error(self):
        """Test VisionProcessingError exception."""
        error = VisionProcessingError("Detection failed")

        assert error.error_code == "VISION_ERROR"
        assert error.message == "Detection failed"

    def test_navtex_processing_error(self):
        """Test NavtexProcessingError exception."""
        error = NavtexProcessingError("Parse failed")

        assert error.error_code == "NAVTEX_ERROR"

    def test_audio_processing_error(self):
        """Test AudioProcessingError exception."""
        error = AudioProcessingError("Analysis failed")

        assert error.error_code == "AUDIO_ERROR"

    def test_sensor_reading_error(self):
        """Test SensorReadingError exception."""
        error = SensorReadingError("Invalid reading")

        assert error.error_code == "SENSOR_ERROR"

    def test_module_initialization_error(self):
        """Test ModuleInitializationError exception."""
        error = ModuleInitializationError("Module startup failed")

        assert error.error_code == "MODULE_INIT_ERROR"

    def test_external_service_error(self):
        """Test ExternalServiceError exception."""
        error = ExternalServiceError("API unavailable")

        assert error.error_code == "EXTERNAL_SERVICE_ERROR"

    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        error = ConfigurationError("Missing config")

        assert error.error_code == "CONFIG_ERROR"

    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        error = AuthenticationError("Invalid token")

        assert error.error_code == "AUTH_ERROR"

    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Invalid input")

        assert error.error_code == "VALIDATION_ERROR"

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError exception."""
        error = ResourceNotFoundError("Record not found")

        assert error.error_code == "NOT_FOUND_ERROR"


# ============================================================================
# Retry Decorator Tests
# ============================================================================

@pytest.mark.unit
class TestRetryDecorator:
    """Tests for retry decorator."""

    def test_retry_success_first_attempt(self):
        """Test retry when function succeeds on first attempt."""
        call_count = 0

        @retry(max_attempts=3)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_function()

        assert result == "success"
        assert call_count == 1

    def test_retry_success_after_failures(self):
        """Test retry when function succeeds after failures."""
        call_count = 0

        @retry(max_attempts=3, delay=0.1)
        def eventually_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"

        result = eventually_successful()

        assert result == "success"
        assert call_count == 3

    def test_retry_max_attempts_exceeded(self):
        """Test retry when max attempts are exceeded."""
        call_count = 0

        @retry(max_attempts=3, delay=0.1)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Permanent failure")

        with pytest.raises(ValueError):
            always_fails()

        assert call_count == 3

    def test_retry_with_exponential_backoff(self):
        """Test retry with exponential backoff."""
        import time
        call_times = []

        @retry(max_attempts=3, delay=0.1, backoff=2.0)
        def function_with_backoff():
            call_times.append(time.time())
            raise Exception("Fail")

        with pytest.raises(Exception):
            function_with_backoff()

        assert len(call_times) == 3

        # Check delays increase exponentially
        # First retry: ~0.1s, second retry: ~0.2s
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]

        assert delay1 < delay2  # Backoff is working


# ============================================================================
# Error Context Manager Tests
# ============================================================================

@pytest.mark.unit
class TestErrorContext:
    """Tests for ErrorContext context manager."""

    def test_error_context_success(self):
        """Test ErrorContext with successful operation."""
        with ErrorContext("Test operation"):
            result = 1 + 1

        assert result == 2

    def test_error_context_catches_exception(self):
        """Test ErrorContext catches and wraps exceptions."""
        with pytest.raises(AADSException) as exc_info:
            with ErrorContext("Test operation"):
                raise ValueError("Original error")

        error = exc_info.value
        assert "Original error" in str(error)
        assert error.details.get("operation") == "Test operation"

    def test_error_context_with_custom_error_class(self):
        """Test ErrorContext with custom error class."""
        with pytest.raises(DatabaseError) as exc_info:
            with ErrorContext("DB operation", error_class=DatabaseError):
                raise ValueError("DB failed")

        error = exc_info.value
        assert error.error_code == "DATABASE_ERROR"

    def test_error_context_with_details(self):
        """Test ErrorContext includes custom details."""
        custom_details = {"user_id": 123, "action": "update"}

        with pytest.raises(AADSException) as exc_info:
            with ErrorContext("User action", details=custom_details):
                raise ValueError("Action failed")

        error = exc_info.value
        assert error.details["user_id"] == 123
        assert error.details["action"] == "update"


# ============================================================================
# Safe Execute Wrapper Tests
# ============================================================================

@pytest.mark.unit
class TestSafeExecute:
    """Tests for safe_execute wrapper."""

    def test_safe_execute_success(self):
        """Test safe_execute with successful function."""
        def successful_func():
            return 42

        result = safe_execute(successful_func, default=0)
        assert result == 42

    def test_safe_execute_with_exception(self):
        """Test safe_execute returns default on exception."""
        def failing_func():
            raise ValueError("Error")

        result = safe_execute(failing_func, default="fallback")
        assert result == "fallback"

    def test_safe_execute_with_args(self):
        """Test safe_execute with function arguments."""
        def func_with_args(a, b, c=10):
            return a + b + c

        result = safe_execute(func_with_args, 1, 2, c=3, default=0)
        assert result == 6

    def test_safe_execute_logs_error(self, caplog):
        """Test safe_execute logs exceptions."""
        def failing_func():
            raise RuntimeError("Test error")

        with caplog.at_level(logging.ERROR):
            safe_execute(failing_func, default=None, error_msg="Custom error")

        assert "Custom error" in caplog.text


# ============================================================================
# Validation Helper Tests
# ============================================================================

@pytest.mark.unit
class TestValidationHelpers:
    """Tests for validation helper functions."""

    def test_validate_coordinates_valid(self):
        """Test validate_coordinates with valid coordinates."""
        lat, lon = validate_coordinates(78.2232, 15.6267)
        assert lat == 78.2232
        assert lon == 15.6267

    def test_validate_coordinates_invalid_latitude(self):
        """Test validate_coordinates with invalid latitude."""
        with pytest.raises(ValidationError) as exc_info:
            validate_coordinates(95.0, 15.0)

        assert "latitude" in str(exc_info.value).lower()

    def test_validate_coordinates_invalid_longitude(self):
        """Test validate_coordinates with invalid longitude."""
        with pytest.raises(ValidationError) as exc_info:
            validate_coordinates(78.0, 200.0)

        assert "longitude" in str(exc_info.value).lower()

    def test_validate_confidence_score_valid(self):
        """Test validate_confidence_score with valid score."""
        score = validate_confidence_score(0.85)
        assert score == 0.85

    def test_validate_confidence_score_boundary(self):
        """Test validate_confidence_score at boundaries."""
        assert validate_confidence_score(0.0) == 0.0
        assert validate_confidence_score(1.0) == 1.0

    def test_validate_confidence_score_invalid(self):
        """Test validate_confidence_score with invalid score."""
        with pytest.raises(ValidationError):
            validate_confidence_score(1.5)

        with pytest.raises(ValidationError):
            validate_confidence_score(-0.1)


# ============================================================================
# Logger Tests
# ============================================================================

@pytest.mark.unit
class TestAADSLogger:
    """Tests for AADSLogger."""

    def test_logger_creation(self):
        """Test AADSLogger creation."""
        logger = AADSLogger("test_module")
        assert logger.logger.name == "test_module"

    def test_logger_info(self, caplog):
        """Test logger info method."""
        logger = AADSLogger("test")

        with caplog.at_level(logging.INFO):
            logger.info("Test message", {"key": "value"})

        assert "Test message" in caplog.text

    def test_logger_error(self, caplog):
        """Test logger error method."""
        logger = AADSLogger("test")

        with caplog.at_level(logging.ERROR):
            logger.error("Error occurred", {"error_code": "TEST_ERROR"})

        assert "Error occurred" in caplog.text

    def test_logger_warning(self, caplog):
        """Test logger warning method."""
        logger = AADSLogger("test")

        with caplog.at_level(logging.WARNING):
            logger.warning("Warning message")

        assert "Warning message" in caplog.text
