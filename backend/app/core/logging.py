"""Bulletproof logging configuration with JSON structured logging."""

import logging
import sys
from pathlib import Path
from typing import Any
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger

from app.core.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        if not log_record.get("timestamp"):
            log_record["timestamp"] = self.formatTime(record, self.datefmt)

        # Add log level
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        # Add logger name
        log_record["logger"] = record.name

        # Add module and function info
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Add environment
        log_record["environment"] = settings.ENVIRONMENT


class ConsoleFormatter(logging.Formatter):
    """Colored console formatter for better readability."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.BOLD}{levelname:8}{self.RESET}"

        # Format the message
        formatted = super().format(record)

        # Reset levelname for other handlers
        record.levelname = levelname

        return formatted


def setup_logging() -> None:
    """Configure application logging with file and console handlers.

    Sets up:
    - JSON formatted rotating file handler
    - Colored console handler for development
    - Module-specific log levels
    - Graceful error handling
    """
    # Create logs directory if it doesn't exist
    log_file_path = Path(settings.LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels, filter in handlers

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

    if settings.LOG_JSON:
        # Use JSON formatter for console in production
        console_formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
    else:
        # Use colored formatter for console in development
        console_formatter = ConsoleFormatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File Handler (always JSON for machine parsing)
    try:
        file_handler = RotatingFileHandler(
            filename=settings.LOG_FILE,
            maxBytes=settings.LOG_MAX_BYTES,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)  # Capture all levels in file

        file_formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # If file handler fails, log to console but don't crash
        root_logger.error(f"Failed to setup file logging: {e}")

    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Log startup message
    root_logger.info(
        "Logging configured",
        extra={
            "log_level": settings.LOG_LEVEL,
            "log_file": settings.LOG_FILE,
            "log_format": "json" if settings.LOG_JSON else "text",
            "environment": settings.ENVIRONMENT,
        },
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Logger name, typically __name__ of the calling module

    Returns:
        Configured logger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Processing started", extra={"user_id": 123})
    """
    logger = logging.getLogger(name)

    # Ensure logger inherits root configuration
    logger.propagate = True

    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds contextual information to all log records."""

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Add contextual information to log records."""
        # Add context from adapter to extra
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra

        return msg, kwargs


def get_contextual_logger(name: str, **context: Any) -> LoggerAdapter:
    """Get a logger with contextual information added to all records.

    Args:
        name: Logger name
        **context: Contextual key-value pairs to add to all log records

    Returns:
        Logger adapter with context

    Example:
        logger = get_contextual_logger(__name__, request_id="abc-123", user_id=456)
        logger.info("User action completed")  # Will include request_id and user_id
    """
    base_logger = get_logger(name)
    return LoggerAdapter(base_logger, context)


# Exception logging helper
def log_exception(logger: logging.Logger, exception: Exception, message: str = "An error occurred", **extra: Any) -> None:
    """Log an exception with full traceback and context.

    Args:
        logger: Logger instance
        exception: Exception to log
        message: Custom error message
        **extra: Additional context to log
    """
    extra_data = {"exception_type": type(exception).__name__, "exception_message": str(exception), **extra}

    logger.error(message, exc_info=True, extra=extra_data)


# Initialize logging on module import
setup_logging()
