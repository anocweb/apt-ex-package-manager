from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QEvent
from settings.app_settings import AppSettings
import logging

class WindowStateManager:
    """Manages window geometry and state persistence for any QMainWindow"""
    
    def __init__(self, window: QMainWindow, settings_key: str):
        self.window = window
        self.settings_key = settings_key
        self.settings = AppSettings()
        self.logger = logging.getLogger(f"apt-ex-manager.ui.{settings_key}")
        
        # Override window events
        self.original_resize_event = window.resizeEvent
        self.original_change_event = window.changeEvent
        
        window.resizeEvent = self.resize_event
        window.changeEvent = self.change_event
    
    def resize_event(self, event):
        """Handle resize events and save geometry"""
        self.original_resize_event(event)
        if not self.window.isMaximized() and not self.window.isFullScreen():
            self.logger.debug(f"Saving geometry - pos: {self.window.pos()}, size: {self.window.size()}")
            self.save_geometry()
    
    def change_event(self, event):
        """Handle window state changes"""
        self.original_change_event(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self.logger.debug(f"State changed - fullscreen: {self.window.isFullScreen()}, maximized: {self.window.isMaximized()}")
            self.save_geometry()
    
    def save_geometry(self):
        """Save window geometry to settings"""
        self.settings.set(f"{self.settings_key}/geometry", self.window.saveGeometry())
        if hasattr(self.window, 'saveState'):
            self.settings.set(f"{self.settings_key}/state", self.window.saveState())
    
    def restore_geometry(self):
        """Restore window geometry from settings"""
        geometry = self.settings.get(f"{self.settings_key}/geometry")
        if geometry:
            self.window.restoreGeometry(geometry)
            self.logger.debug(f"Restored geometry - pos: {self.window.pos()}, size: {self.window.size()}")
        else:
            self.logger.debug(f"No saved geometry found, using default - pos: {self.window.pos()}, size: {self.window.size()}")
        
        # Restore window state if available
        if hasattr(self.window, 'restoreState'):
            state = self.settings.get(f"{self.settings_key}/state")
            if state:
                self.window.restoreState(state)