# id_service/utils/logging_config.py

import logging
import sys
from typing import Any, Dict
import json
from datetime import datetime

from core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id
        if hasattr(record, 'client_id'):
            log_obj['client_id'] = record.client_id
        if hasattr(record, 'ip_address'):
            log_obj['ip_address'] = record.ip_address
        if hasattr(record, 'trace_id'):
            log_obj['trace_id'] = record.trace_id
        
        # Add exception info if present
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)


def setup_logging():
    """Configure application logging"""
    
    # Set log level based on environment
    log_level = logging.DEBUG if settings.APP_ENV == "development" else logging.INFO
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter based on environment
    if settings.APP_ENV == "production":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Silence noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return root_logger