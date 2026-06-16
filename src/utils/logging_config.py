import sys
import logging
from pathlib import Path
import logging.handlers
import socket
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
import atexit
import re
import os

# Ensure logs directory exists
LOG_BASE_DIR = Path(os.getenv("LOG_BASE_DIR", "logs"))
LOG_DIR_APP = Path(os.getenv("LOG_DIR_APP", str(LOG_BASE_DIR / "app_logs")))
LOG_DIR_AUDIT = Path(os.getenv("LOG_DIR_AUDIT", str(LOG_BASE_DIR / "perf_logs")))
LOG_DIR_MONITOR = Path(os.getenv("LOG_DIR_MONITOR", str(LOG_BASE_DIR / "monitor_logs")))

LOG_DIR_APP.mkdir(parents=True, exist_ok=True)
LOG_DIR_AUDIT.mkdir(parents=True, exist_ok=True)
LOG_DIR_MONITOR.mkdir(parents=True, exist_ok=True)

# Define log file paths
APP_LOG_FILE = LOG_DIR_APP / "app.log"
AUDIT_LOG_FILE = LOG_DIR_AUDIT / "audit.log"
MONITOR_LOG_FILE = LOG_DIR_MONITOR / "monitor.log"

# Define Log Formatters
STANDARD_FORMATTER = {
    "format": "%(asctime)s - %(name)s:%(funcName)s - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}
MONITOR_FORMATTER = {
    "format": '%(asctime)s %(message)s',
    "datefmt": "%Y-%m-%d %H:%M:%S",
}

JSON_FORMATTER = {
    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}


class LoggerNameFilter(logging.Filter):
    def __init__(self, allowed_logger_names):
        super().__init__()
        self.allowed_names = allowed_logger_names if isinstance(allowed_logger_names, list) else [allowed_logger_names]

    def filter(self, record):
        return record.name in self.allowed_names


class DesensitizeFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            msg = record.msg
            msg = re_email.sub("***[邮箱]***", msg)
            msg = re_id.sub("***[身份证]***", msg)
            msg = re_card.sub("***[卡号]***", msg)
            msg = re_tel.sub("***[电话]***", msg)
            msg = re_phone.sub("***[手机]***", msg)
            record.msg = msg
            return True


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
    app_handler.addFilter(DesensitizeFilter())
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
    audit_handler.addFilter(LoggerNameFilter("audit"))
    audit_handler.addFilter(DesensitizeFilter())
    monitor_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(MONITOR_LOG_FILE),
        when='midnight',
        backupCount=10,
        encoding="utf-8",
    )
    monitor_handler.setLevel(logging.INFO)
    monitor_handler.setFormatter(logging.Formatter(
        fmt=MONITOR_FORMATTER["format"],
        datefmt=MONITOR_FORMATTER["datefmt"]
    ))
    monitor_handler.addFilter(LoggerNameFilter("monitor"))
    # Create QueueListener with actual handlers
    _queue_listener = logging.handlers.QueueListener(
        log_queue,
        app_handler,
        audit_handler,
        monitor_handler,
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
        #  "%(asctime)s - %(name)s:%(funcName)s - %(levelname)s - %(message)s",
        "monitor_standard": MONITOR_FORMATTER
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
        "file_monitor": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "monitor_standard",
            "filename": str(MONITOR_LOG_FILE),
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
        },
        "monitor": {
            "level": "INFO",
            "handlers": ["file_monitor"],
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file_app"],
    }
}

# 脱敏数据编译
re_email = re.compile(
    r"[A-Za-z\d][-_.A-Za-z\d]{1,20}@[A-Za-z\d]{1,20}(\.[a-zA-Z0-9-]{2,8}){0,3}\.(com|cn|net|org|edu|gov|biz|info|name|coop|idv)")
re_id = re.compile(r"[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]")
re_card = re.compile(r"([\D]|^)(\d{16,19})([\D]|$)")
re_tel = re.compile(r"\(?0\d{2,3}\)?[-\s]?\d{7,8}")
re_phone = re.compile(r"1[3-9]\d{9}")


def desensitize_msg(message):
    try:
        if isinstance(message, str):
            # 邮箱
            if "@" in message:
                message = re_email.sub("***[邮箱]***", message)
            # 身份证
            message = re_id.sub("***[身份证]***", message)
            # 卡号
            message = re_card.sub("***[卡号]***", message)
            # 电话
            # message = re.sub(r"0\d{2,3}-\d{7,8}","***[电话]***",message)
            message = re_tel.sub("***[座机]***", message)  # 010- 123456 (010)xxxxx
            # 手机
            message = re_phone.sub("***[手机]***", message)
        return message
    except:
        return message


LOG_FORMAT = '[%(levelname)s][%(hostname)s][%(asctime)s] %(message)s'

hostname = socket.gethostname()
logger = logging.getLogger("logger")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)  # INFO
stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
file_handler = logging.handlers.TimedRotatingFileHandler(MONITOR_LOG_FILE, when='midnight', backupCount=15,
                                                         encoding='utf-8')
file_handler.setLevel(logging.INFO)  # DEBUG, 敏感信息为DEBUG等级，不会显示在PAAS
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

logger.setLevel(logging.INFO)  # DEBUG

log_queue = Queue()
queue_handler = QueueHandler(log_queue)
logger.addHandler(queue_handler)
listener = QueueListener(log_queue, file_handler, stream_handler)
listener.start()
atexit.register(listener.stop)

logger = logging.LoggerAdapter(logger, {
    "hostname": hostname
})


# 记录脱敏数据
def log_desensitize(message):
    message = desensitize_msg(message)
    logger.info(message)


# def log_monitor(traceid, app_id, type, cost, success):
#     monitor_logger = logging.getLogger("monitor")
#     monitor_logger.info(f'traceid={traceid}||appId={app_id}||transClass={type}||cost={round(cost * 1000)}||flag={int(success)}')

def log_monitor(traceid, app_id, trans_class, version, cost, success, return_code):
    monitor_logger = logging.getLogger("monitor")
    monitor_logger.info(
        f'traceid={traceid}||'
        f'moduleId={app_id}||'
        f'transClass={trans_class}||'
        f'version={version}||'
        f'cost={round(cost * 1000)}||'
        f'flag={int(success)}||'
        f'returnCode={return_code}'
    )
