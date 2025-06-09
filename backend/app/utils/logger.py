"""
Comprehensive logging system for the Work Order application.
Provides structured logging with proper log levels and formatting.
"""

import json
import logging
import sys
from datetime import datetime
from enum import Enum
from typing import Any

from app.core.config import settings


class LogLevel(str, Enum):
    """Standard log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        # Create base log structure
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


class WorkOrderLogger:
    """Central logger for the Work Order application."""

    def __init__(self, name: str = "workorder"):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Configure the logger with appropriate handlers and formatters."""
        # Clear any existing handlers
        self.logger.handlers.clear()

        # Set log level based on environment
        if settings.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)

        # Use structured JSON format for production, simple format for development
        if settings.debug:
            # Simple format for development
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | "
                "%(module)s:%(funcName)s:%(lineno)d | %(message)s"
            )
        else:
            # Structured JSON format for production
            formatter = StructuredFormatter()

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Prevent duplicate logs
        self.logger.propagate = False

    def debug(self, message: str, extra_data: dict[str, Any] | None = None) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, extra_data)

    def info(self, message: str, extra_data: dict[str, Any] | None = None) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, extra_data)

    def warning(self, message: str, extra_data: dict[str, Any] | None = None) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, extra_data)

    def error(
        self,
        message: str,
        extra_data: dict[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, extra_data, exc_info)

    def critical(
        self,
        message: str,
        extra_data: dict[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, extra_data, exc_info)

    def _log(
        self,
        level: LogLevel,
        message: str,
        extra_data: dict[str, Any] | None = None,
        exc_info: bool = False,
    ) -> None:
        """Internal logging method."""
        # Create log record with extra data
        extra = {"extra_data": extra_data} if extra_data else {}

        # Map our LogLevel enum to logging levels
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }

        self.logger.log(level_map[level], message, extra=extra, exc_info=exc_info)

    def log_request(
        self,
        method: str,
        url: str,
        user_id: str | None = None,
        duration_ms: float | None = None,
    ) -> None:
        """Log HTTP request information."""
        extra_data = {
            "type": "http_request",
            "method": method,
            "url": url,
            "user_id": user_id,
            "duration_ms": duration_ms,
        }
        self.info(f"{method} {url}", extra_data)

    def log_database_operation(
        self,
        operation: str,
        table: str,
        duration_ms: float | None = None,
        record_count: int | None = None,
    ) -> None:
        """Log database operation information."""
        extra_data = {
            "type": "database_operation",
            "operation": operation,
            "table": table,
            "duration_ms": duration_ms,
            "record_count": record_count,
        }
        self.debug(f"Database {operation} on {table}", extra_data)

    def log_geocoding(
        self,
        query: str,
        success: bool,
        latitude: float | None = None,
        longitude: float | None = None,
        error: str | None = None,
    ) -> None:
        """Log geocoding operation information."""
        extra_data = {
            "type": "geocoding",
            "query": query,
            "success": success,
            "latitude": latitude,
            "longitude": longitude,
            "error": error,
        }
        if success:
            self.info(f"Geocoding successful for: {query}", extra_data)
        else:
            self.warning(f"Geocoding failed for: {query}", extra_data)


# Global logger instance
logger = WorkOrderLogger()


# Convenience functions for backward compatibility with existing debug utilities
def debug_log(message: str, extra_data: dict[str, Any] | None = None) -> None:
    """Backward compatible debug logging."""
    logger.debug(message, extra_data)


def debug_log_dict(label: str, data: dict) -> None:
    """Backward compatible dict logging."""
    logger.debug(label, {"data": data})


def debug_log_exception(label: str, exception: Exception) -> None:
    """Backward compatible exception logging."""
    logger.error(
        label,
        {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        },
        exc_info=True,
    )
