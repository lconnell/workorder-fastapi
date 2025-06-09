"""Debug utilities for conditional logging."""

from app.core.config import settings


def debug_log(message: str) -> None:
    """Log a debug message only if DEBUG=true in environment."""
    if settings.debug:
        print(f"DEBUG: {message}")


def debug_log_dict(label: str, data: dict) -> None:
    """Log a dictionary as debug message only if DEBUG=true in environment."""
    if settings.debug:
        print(f"DEBUG: {label}: {data}")


def debug_log_exception(label: str, exception: Exception) -> None:
    """Log an exception as debug message only if DEBUG=true in environment."""
    if settings.debug:
        import traceback

        print(f"DEBUG: {label}: {exception}")
        print(f"DEBUG: {label} traceback: {traceback.format_exc()}")
