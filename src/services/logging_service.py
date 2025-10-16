import logging
import os
from typing import Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal

class LoggingService(QObject):
    """Centralized logging service with multiple destinations"""
    
    # Signal emitted when new log message is added
    log_updated = pyqtSignal()
    
    def __init__(self, app_name: str = "apt-ex-manager"):
        super().__init__()
        self.app_name = app_name
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Custom handler for in-app logging
        self.app_log_handler = None
        self.app_log_callback: Optional[Callable] = None
        
        # Store formatted log messages for log view
        self._log_messages = []
        
        # Track registered loggers
        self.registered_loggers = set()
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default console handler"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings+ to console
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
        """Get a named logger that uses the same handlers"""
        full_name = f"{self.app_name}.{name}"
        named_logger = logging.getLogger(full_name)
        named_logger.setLevel(logging.DEBUG)
        
        # Prevent propagation to avoid duplicate messages
        named_logger.propagate = False
        
        # Register this logger
        self.registered_loggers.add(full_name)
        self.debug(f"Registered logger: {full_name}")
        
        # Add the same handlers if not already added
        if not named_logger.handlers:
            for handler in self.logger.handlers:
                named_logger.addHandler(handler)
        
        return named_logger
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log critical message"""
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
        try:
            message = self.format(record)
            self.callback(message)
            # Store formatted message for log view
            self.logging_service._log_messages.append(message)
            # Keep only last 200 messages
            if len(self.logging_service._log_messages) > 200:
                self.logging_service._log_messages = self.logging_service._log_messages[-200:]
            # Emit signal for log view updates
            self.logging_service.log_updated.emit()
        except Exception:
            pass  # Ignore errors in logging to prevent recursion