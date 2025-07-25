import logging
import sys
import json
from typing import Any, Dict, Optional
from datetime import datetime
from contextvars import ContextVar

# Context variable for tracking request/job context
request_context: ContextVar[Dict[str, Any]] = ContextVar("request_context", default={})


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "cv-processing-service",
        }

        # Add context information if available
        context = request_context.get()
        if context:
            log_entry.update(context)

        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add any extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_entry[key] = value

        return json.dumps(log_entry)


def setup_logging(
    service_name: str = "cv-processing-service",
    log_level: str = "INFO",
    enable_structured_logging: bool = True,
) -> logging.Logger:
    """Setup centralized logging configuration"""

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    formatter: logging.Formatter  # Added explicit type annotation
    if enable_structured_logging:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create service-specific logger
    service_logger = logging.getLogger(service_name)

    return service_logger


def log_error(
    logger: logging.Logger,
    message: str,
    error: Exception = None,
    extra_context: Dict[str, Any] = None,
):
    """Log error with structured context"""

    context = {
        "error_type": error.__class__.__name__ if error else None,
        "error_message": str(error) if error else None,
    }

    if extra_context:
        context.update(extra_context)

    if error:
        logger.error(message, exc_info=error, extra=context)
    else:
        logger.error(message, extra=context)


def log_service_call(
    logger: logging.Logger,
    service_name: str,
    operation: str,
    status: str,
    duration_ms: Optional[int] = None,
    extra_context: Dict[str, Any] = None,
):
    """Log service-to-service call with structured context"""

    context = {
        "service_call": {
            "target_service": service_name,
            "operation": operation,
            "status": status,
            "duration_ms": duration_ms,
        }
    }

    if extra_context:
        context.update(extra_context)

    if status == "success":
        logger.info(
            f"Service call successful: {service_name}.{operation}", extra=context
        )
    else:
        logger.error(f"Service call failed: {service_name}.{operation}", extra=context)


def set_request_context(
    job_id: str = None,
    user_id: str = None,
    request_id: str = None,
    file_name: str = None,
    **kwargs,
):
    """Set request context for logging"""

    context = {}

    if job_id:
        context["job_id"] = job_id
    if user_id:
        context["user_id"] = user_id
    if request_id:
        context["request_id"] = request_id
    if file_name:
        context["file_name"] = file_name

    context.update(kwargs)
    request_context.set(context)


def clear_request_context():
    """Clear request context"""
    request_context.set({})


class ServiceLogger:
    """Service-specific logger with contextual information"""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)

    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(message, extra=kwargs)

    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error message with context"""
        log_error(self.logger, message, error, kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.logger.warning(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self.logger.debug(message, extra=kwargs)

    def service_call(
        self,
        service_name: str,
        operation: str,
        status: str,
        duration_ms: int = None,
        **kwargs,
    ):
        """Log service call with context"""
        log_service_call(
            self.logger, service_name, operation, status, duration_ms, kwargs
        )
