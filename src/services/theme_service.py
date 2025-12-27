import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from utils.path_resolver import PathResolver

class ThemeService:
    """Handle application icon management and theme detection"""
    
    def __init__(self, app: QApplication):
        self.app = app
    
    def is_dark_theme(self) -> bool:
        """Check if dark theme is active"""
        palette = self.app.palette()
        return palette.color(palette.ColorRole.Window).lightness() < 128
    
    def get_icon_path(self) -> str:
        """Get appropriate icon path based on theme"""
        try:
            if self.is_dark_theme():
                try:
                    return PathResolver.get_icon_path('app-icon-dark.svg')
                except FileNotFoundError:
                    pass
            return PathResolver.get_icon_path('app-icon.svg')
        except FileNotFoundError:
            return None
    
    def setup_application_icon(self) -> None:
        """Set up application icon with multiple sizes"""
        try:
            icon_path = self.get_icon_path()
            if icon_path:
                icon = QIcon(icon_path)
                icon.addFile(icon_path, QSize(16, 16))
                icon.addFile(icon_path, QSize(32, 32))
                icon.addFile(icon_path, QSize(48, 48))
                icon.addFile(icon_path, QSize(64, 64))
                self.app.setWindowIcon(icon)
        except Exception:
            pass
