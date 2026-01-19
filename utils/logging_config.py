import sys
import logging
import logging.handlers
import os
from pathlib import Path

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
            "formatter": "standard", # Ideally JSON
            "filename": str(AUDIT_LOG_FILE),
            "maxBytes": 100 * 1024 * 1024,  # 100MB
            "backupCount": 10,
            "encoding": "utf-8",
            "level": "INFO",
        },
        # Queue Handler for Async Logging
        "queue_listener": {
            "class": "logging.handlers.QueueHandler",
            "handlers": ["console", "file_app"], # Default handles console + app log
            "respect_handler_level": True,
        },
    },
    "loggers": {
        "sanic.root": {
            "level": "INFO",
            "handlers": ["queue_listener"], # Send to Queue
            "propagate": False,
        },
        "sanic.error": {
            "level": "INFO",
            "handlers": ["queue_listener"], # Send to Queue
            "propagate": False,
        },
        "sanic.access": {
            "level": "INFO",
            "handlers": ["queue_listener"], # Send to Queue
            "propagate": False,
        },
        # Dedicated Logger for Audit
        "audit": {
            "level": "INFO",
            "handlers": ["file_audit"], # Direct to file (will wrap in queue in app setup if needed, or keep separate)
            "propagate": False,
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["queue_listener"], # Send to Queue
    }
}

def setup_logging_queue():
    """
    Sets up the QueueListener to handle logs asynchronously.
    Returns the listener instance which should be started and stopped with the app.
    """
    import atexit
    
    # Create the queue
    log_queue = queue.Queue(-1) # Infinite queue
    
    # Get the actual handler instances based on the config names
    # Note: dictConfig creates the handlers. We need to access them to pass to QueueListener.
    # But standard dictConfig doesn't expose them easily. 
    # A common pattern is to manually instantiate the QueueListener after dictConfig.
    
    # For simplicity in this context, we will rely on a slightly different pattern:
    # We will let the app setup (llm_server_app.py) initialize the QueueListener 
    # because it needs access to the created handler objects.
    pass