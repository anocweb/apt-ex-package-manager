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
        self.statusbar.showMessage(f"{self.status_base_message}{dots}")
        self.status_dots = (self.status_dots + 1) % 3
