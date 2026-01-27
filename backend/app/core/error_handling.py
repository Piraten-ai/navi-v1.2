"""
AADS Error Handling Module
=========================
Custom exceptions, retry decorator, error context manager, and validation helpers
for the AADS (Arctic Autonomy Decision Support) system.
"""

import functools
import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar("T")


# ============================================================================
# Custom Exceptions
# ============================================================================


class AADSException(Exception):
    """Base exception for all AADS errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "AADS_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON serialization."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class DatabaseError(AADSException):
    """Database operation errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="DATABASE_ERROR", details=details)


class VisionProcessingError(AADSException):
    """Vision/detection processing errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="VISION_ERROR", details=details)


class NavtexProcessingError(AADSException):
    """NAVTEX message processing errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="NAVTEX_ERROR", details=details)


class AudioProcessingError(AADSException):
    """Audio analysis errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="AUDIO_ERROR", details=details)


class SensorReadingError(AADSException):
    """Sensor reading errors (GPS, IMU, etc.)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="SENSOR_ERROR", details=details)


class ModuleInitializationError(AADSException):
    """Module startup/initialization errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="MODULE_INIT_ERROR", details=details)


class ExternalServiceError(AADSException):
    """External service (Ollama, APIs) errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="EXTERNAL_SERVICE_ERROR", details=details)


class ConfigurationError(AADSException):
    """Configuration/settings errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="CONFIG_ERROR", details=details)


class AuthenticationError(AADSException):
    """Authentication/authorization errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="AUTH_ERROR", details=details)


class ValidationError(AADSException):
    """Input validation errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="VALIDATION_ERROR", details=details)


class ResourceNotFoundError(AADSException):
    """Resource not found errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="NOT_FOUND_ERROR", details=details)


# ============================================================================
# Retry Decorator
# ============================================================================


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 1.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry (exponential backoff)
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff

            # Re-raise the last exception after all retries exhausted
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry failed without exception")

        return wrapper

    return decorator


# ============================================================================
# Error Context Manager
# ============================================================================


class ErrorContext:
    """
    Context manager for wrapping operations with error handling.

    Usage:
        with ErrorContext("Database query", error_class=DatabaseError):
            result = db.query(...)
    """

    def __init__(
        self,
        operation: str,
        error_class: Type[AADSException] = AADSException,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.operation = operation
        self.error_class = error_class
        self.details = details or {}

    def __enter__(self) -> "ErrorContext":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if exc_val is not None:
            # Don't wrap if it's already our exception type
            if isinstance(exc_val, AADSException):
                return False

            # Wrap the exception with our custom type
            error_details = {
                "operation": self.operation,
                "original_error": str(exc_val),
                "original_type": exc_type.__name__ if exc_type else "Unknown",
                **self.details,
            }
            raise self.error_class(
                f"{self.operation} failed: {exc_val}",
                details=error_details,
            ) from exc_val

        return False


# ============================================================================
# Safe Execution Wrapper
# ============================================================================


def safe_execute(
    func: Callable[..., T],
    *args: Any,
    default: T = None,
    error_msg: Optional[str] = None,
    **kwargs: Any,
) -> T:
    """
    Execute a function safely, returning a default value on error.

    Args:
        func: Function to execute
        *args: Positional arguments for the function
        default: Default value to return on error
        error_msg: Optional custom error message for logging
        **kwargs: Keyword arguments for the function

    Returns:
        Function result or default value on error
    """
    logger = logging.getLogger(__name__)

    try:
        return func(*args, **kwargs)
    except Exception as e:
        msg = error_msg or f"Error executing {func.__name__}"
        logger.error(f"{msg}: {e}", exc_info=True)
        return default


# ============================================================================
# Validation Helpers
# ============================================================================


def validate_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    """
    Validate GPS coordinates.

    Args:
        latitude: Latitude value (-90 to 90)
        longitude: Longitude value (-180 to 180)

    Returns:
        Tuple of (latitude, longitude) if valid

    Raises:
        ValidationError: If coordinates are invalid
    """
    if not -90 <= latitude <= 90:
        raise ValidationError(
            f"Invalid latitude: {latitude}. Must be between -90 and 90.",
            details={"latitude": latitude},
        )

    if not -180 <= longitude <= 180:
        raise ValidationError(
            f"Invalid longitude: {longitude}. Must be between -180 and 180.",
            details={"longitude": longitude},
        )

    return (latitude, longitude)


def validate_confidence_score(score: float) -> float:
    """
    Validate a confidence score (0.0 to 1.0).

    Args:
        score: Confidence score to validate

    Returns:
        The score if valid

    Raises:
        ValidationError: If score is invalid
    """
    if not 0.0 <= score <= 1.0:
        raise ValidationError(
            f"Invalid confidence score: {score}. Must be between 0.0 and 1.0.",
            details={"score": score},
        )

    return score


# ============================================================================
# AADS Logger
# ============================================================================


class AADSLogger:
    """
    Custom logger for AADS with structured logging support.

    Provides consistent logging format across all modules.
    """

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message with optional extra data."""
        self.logger.info(message, extra=extra or {})

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message with optional extra data."""
        self.logger.warning(message, extra=extra or {})

    def error(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Log error message with optional extra data and exception info."""
        self.logger.error(message, extra=extra or {}, exc_info=exc_info)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message with optional extra data."""
        self.logger.debug(message, extra=extra or {})

    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log critical message with optional extra data."""
        self.logger.critical(message, extra=extra or {})

    def exception(
        self, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, extra=extra or {})
