"""Status bar management service"""
from PyQt6.QtCore import QTimer


class StatusService:
    """Manages status bar messages and animations"""
    
    def __init__(self, statusbar):
        self.statusbar = statusbar
        self.animation_timer = None
        self.status_dots = 0
        self.status_base_message = ""
    
    def show_message(self, message, timeout=0):
        """Show a status message with optional timeout (milliseconds)"""
        if hasattr(self.statusbar, 'show_message'):
            self.statusbar.show_message(message, timeout)
        else:
            self.statusbar.showMessage(message, timeout)
    
    def clear_message(self):
        """Clear the status message"""
        self.statusbar.clearMessage()
    
    def start_animation(self, base_message):
        """Start animated status with dots"""
        self.status_base_message = base_message
        self.status_dots = 0
        
        if self.animation_timer:
            self.animation_timer.stop()
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_dots)
        self.animation_timer.start(500)
        self._animate_dots()
    
    def stop_animation(self):
        """Stop animated status"""
        if self.animation_timer:
            self.animation_timer.stop()
            self.animation_timer = None
    
    def update_message(self, message):
        """Update the base status message during animation"""
        self.status_base_message = message
    
    def _animate_dots(self):
        """Animate the dots in status message"""
        dots = "." * (self.status_dots + 1)
        message = f"{self.status_base_message}{dots}"
        if hasattr(self.statusbar, 'show_message'):
            self.statusbar.show_message(message)
        else:
            self.statusbar.showMessage(message)
        self.status_dots = (self.status_dots + 1) % 3
    
    def start_operation(self, operation_type, package_name):
        """Start showing operation in status bar"""
        if hasattr(self.statusbar, 'start_operation'):
            self.statusbar.start_operation(operation_type, package_name)
    
    def set_operation_complete(self, success, message):
        """Mark operation as complete"""
        if hasattr(self.statusbar, 'set_complete'):
            self.statusbar.set_complete(success, message)
