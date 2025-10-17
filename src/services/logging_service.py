import logging
import os
import json
from typing import Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal

class LoggingService(QObject):
    """Centralized logging service with multiple destinations"""
    
    # Signal emitted when new log message is added
    log_updated = pyqtSignal()
    
    def __init__(self, app_name: str = "apt-ex-manager", stdout_log_level: str = "WARNING"):
        super().__init__()
        self.app_name = app_name
        self.stdout_log_level = stdout_log_level
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Custom handler for in-app logging
        self.app_log_handler = None
        self.app_log_callback: Optional[Callable] = None
        
        # Store formatted log messages for log view
        self._log_messages = []
        
        # Track registered loggers
        self.registered_loggers = set()
        # Register root logger
        self.registered_loggers.add(app_name)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default console handler"""
        console_handler = logging.StreamHandler()
        # Set console level based on stdout_log_level parameter
        console_level = getattr(logging, self.stdout_log_level.upper(), logging.WARNING)
        console_handler.setLevel(console_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def set_app_log_callback(self, callback: Callable[[str], None]):
        """Set callback for in-app logging display"""
        self.app_log_callback = callback
        
        if self.app_log_handler:
            self.logger.removeHandler(self.app_log_handler)
        
        # Create custom handler for app logging
        self.app_log_handler = AppLogHandler(callback, self)
        self.app_log_handler.setLevel(logging.INFO)
        self.logger.addHandler(self.app_log_handler)
    
    def enable_file_logging(self, log_dir: str):
        """Enable logging to file"""
        # Sanitize path to prevent directory traversal (CWE-22)
        log_dir = os.path.abspath(os.path.expanduser(log_dir))
        home_dir = os.path.expanduser('~')
        if not log_dir.startswith(home_dir):
            raise ValueError(f"Log directory must be within user home directory: {home_dir}")
        
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"{self.app_name}.log")
        
        # Remove existing file handler if any
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                self.logger.removeHandler(handler)
        
        # Add new file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def disable_file_logging(self):
        """Disable file logging"""
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                self.logger.removeHandler(handler)
    
    def get_logger(self, name: str):
        """Get a named logger wrapper that supports data parameter"""
        full_name = f"{self.app_name}.{name}"
        named_logger = logging.getLogger(full_name)
        named_logger.setLevel(logging.DEBUG)
        
        # Prevent propagation to avoid duplicate messages
        named_logger.propagate = False
        
        # Register this logger
        self.registered_loggers.add(full_name)
        
        # Add the same handlers if not already added
        if not named_logger.handlers:
            for handler in self.logger.handlers:
                # Create a copy of the handler to avoid shared state issues
                if isinstance(handler, logging.StreamHandler) and not isinstance(handler, AppLogHandler):
                    # Console handler - respect stdout_log_level
                    console_handler = logging.StreamHandler()
                    console_level = getattr(logging, self.stdout_log_level.upper(), logging.WARNING)
                    console_handler.setLevel(console_level)
                    console_handler.setFormatter(handler.formatter)
                    named_logger.addHandler(console_handler)
                else:
                    # Other handlers (app log handler, file handler)
                    named_logger.addHandler(handler)
        
        return LoggerWrapper(named_logger)
        

    
    def register_logger(self, logger):
        """Register an existing logger with the logging service"""
        if hasattr(logger, 'logger'):
            # It's a LoggerWrapper
            logger_name = logger.logger.name
        else:
            # It's a standard logger
            logger_name = logger.name
        
        self.registered_loggers.add(logger_name)
        
        # Add handlers to the logger if it doesn't have them
        actual_logger = logger.logger if hasattr(logger, 'logger') else logger
        if not actual_logger.handlers:
            for handler in self.logger.handlers:
                actual_logger.addHandler(handler)
    
    def debug(self, message: str, data=None):
        """Log debug message with optional data"""
        if data is not None:
            self.logger.debug(message, extra={'data': data})
        else:
            self.logger.debug(message)
    
    def info(self, message: str, data=None):
        """Log info message with optional data"""
        if data is not None:
            self.logger.info(message, extra={'data': data})
        else:
            self.logger.info(message)
    
    def warning(self, message: str, data=None):
        """Log warning message with optional data"""
        if data is not None:
            self.logger.warning(message, extra={'data': data})
        else:
            self.logger.warning(message)
    
    def error(self, message: str, data=None):
        """Log error message with optional data"""
        if data is not None:
            self.logger.error(message, extra={'data': data})
        else:
            self.logger.error(message)
    
    def critical(self, message: str, data=None):
        """Log critical message with optional data"""
        if data is not None:
            self.logger.critical(message, extra={'data': data})
        else:
            self.logger.critical(message)

class LoggerWrapper:
    """Wrapper for logger that supports data parameter"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def debug(self, message: str, data=None):
        if data is not None:
            self.logger.debug(message, extra={'data': data})
        else:
            self.logger.debug(message)
    
    def info(self, message: str, data=None):
        if data is not None:
            self.logger.info(message, extra={'data': data})
        else:
            self.logger.info(message)
    
    def warning(self, message: str, data=None):
        if data is not None:
            self.logger.warning(message, extra={'data': data})
        else:
            self.logger.warning(message)
    
    def error(self, message: str, data=None):
        if data is not None:
            self.logger.error(message, extra={'data': data})
        else:
            self.logger.error(message)
    
    def critical(self, message: str, data=None):
        if data is not None:
            self.logger.critical(message, extra={'data': data})
        else:
            self.logger.critical(message)

class AppLogHandler(logging.Handler):
    """Custom handler for in-app log display"""
    
    def __init__(self, callback: Callable[[str], None], logging_service):
        super().__init__()
        self.callback = callback
        self.logging_service = logging_service
        # Set formatter to include timestamp, logger name, level, and message
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        self.setFormatter(formatter)
    
    def emit(self, record):
        """Emit log record to app callback"""
        message = self.format(record)
        self.callback(message)
        
        # Handle data field if present
        data_json = None
        if hasattr(record, 'data') and record.data is not None:
            try:
                data_json = json.dumps(record.data, indent=2, default=str)
            except (TypeError, ValueError):
                data_json = str(record.data)
        
        # Store message with optional data for log view
        log_entry = {
            'message': message,
            'data': data_json
        }
        self.logging_service._log_messages.append(log_entry)
        
        # Keep only last 200 messages
        if len(self.logging_service._log_messages) > 200:
            self.logging_service._log_messages = self.logging_service._log_messages[-200:]
        # Emit signal for log view updates
        self.logging_service.log_updated.emit()