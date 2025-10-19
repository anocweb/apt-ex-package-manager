import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class ThemeService:
    """Handle application icon management and theme detection"""
    
    def __init__(self, app: QApplication):
        self.app = app
        self.base_path = os.path.join(os.path.dirname(__file__), '..', 'icons')
    
    def is_dark_theme(self) -> bool:
        """Check if dark theme is active"""
        palette = self.app.palette()
        return palette.color(palette.ColorRole.Window).lightness() < 128
    
    def get_icon_path(self) -> str:
        """Get appropriate icon path based on theme"""
        if self.is_dark_theme():
            dark_icon = os.path.join(self.base_path, 'app-icon-dark.svg')
            if os.path.exists(dark_icon):
                return dark_icon
        
        # Fallback to light icon
        return os.path.join(self.base_path, 'app-icon.svg')
    
    def setup_application_icon(self) -> None:
        """Set up application icon with multiple sizes"""
        try:
            icon_path = self.get_icon_path()
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                icon.addFile(icon_path, QSize(16, 16))
                icon.addFile(icon_path, QSize(32, 32))
                icon.addFile(icon_path, QSize(48, 48))
                icon.addFile(icon_path, QSize(64, 64))
                self.app.setWindowIcon(icon)
        except Exception:
            pass
