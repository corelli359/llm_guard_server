import sys
import logging
import logging.handlers
import os
from pathlib import Path
from queue import Queue

# Ensure logs directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Define log file paths
APP_LOG_FILE = LOG_DIR / "app.log"
AUDIT_LOG_FILE = LOG_DIR / "audit.log"

# Define Log Formatters
STANDARD_FORMATTER = {
    "format": "%(asctime)s - %(name)s:%(funcName)s - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}

JSON_FORMATTER = {
    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}

# Global queue listener instance
_queue_listener = None

def setup_async_logging():
    """Setup async logging with QueueHandler and QueueListener"""
    global _queue_listener

    # Create queue for async logging
    log_queue = Queue(-1)  # Unlimited size

    # Create actual file handlers
    app_handler = logging.handlers.RotatingFileHandler(
        filename=str(APP_LOG_FILE),
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10,
        encoding="utf-8",
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(logging.Formatter(
        fmt=STANDARD_FORMATTER["format"],
        datefmt=STANDARD_FORMATTER["datefmt"]
    ))

    audit_handler = logging.handlers.RotatingFileHandler(
        filename=str(AUDIT_LOG_FILE),
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10,
        encoding="utf-8",
    )
    audit_handler.setLevel(logging.INFO)
    audit_handler.setFormatter(logging.Formatter(
        fmt=STANDARD_FORMATTER["format"],
        datefmt=STANDARD_FORMATTER["datefmt"]
    ))

    # Create QueueListener with actual handlers
    _queue_listener = logging.handlers.QueueListener(
        log_queue,
        app_handler,
        audit_handler,
        respect_handler_level=True
    )
    _queue_listener.start()

    return log_queue

def stop_async_logging():
    """Stop the async logging queue listener"""
    global _queue_listener
    if _queue_listener:
        _queue_listener.stop()
        _queue_listener = None

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": STANDARD_FORMATTER,
        # "json": JSON_FORMATTER, # Uncomment if json logger is installed
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": sys.stdout,
            "level": "INFO",
        },
        "file_app": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": str(APP_LOG_FILE),
            "maxBytes": 100 * 1024 * 1024,  # 100MB
            "backupCount": 10,
            "encoding": "utf-8",
            "level": "INFO",
        },
        "file_audit": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": str(AUDIT_LOG_FILE),
            "maxBytes": 100 * 1024 * 1024,  # 100MB
            "backupCount": 10,
            "encoding": "utf-8",
            "level": "INFO",
        },
    },
    "loggers": {
        "sanic.root": {
            "level": "INFO",
            "handlers": ["console", "file_app"],
            "propagate": False,
        },
        "sanic.error": {
            "level": "INFO",
            "handlers": ["console", "file_app"],
            "propagate": False,
        },
        "sanic.access": {
            "level": "INFO",
            "handlers": ["console", "file_app"],
            "propagate": False,
        },
        # Dedicated Logger for Audit - will be replaced with QueueHandler
        "audit": {
            "level": "INFO",
            "handlers": ["file_audit"],
            "propagate": False,
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file_app"],
    }
}