"""Base panel class for all panel controllers"""
from PyQt6.QtWidgets import QWidget
from PyQt6 import uic


class BasePanel(QWidget):
    """Base class for all panel controllers"""
    
    def __init__(self, ui_file, package_manager, lmdb_manager, logging_service, app_settings):
        super().__init__()
        self.package_manager = package_manager
        self.lmdb_manager = lmdb_manager
        self.logging_service = logging_service
        self.app_settings = app_settings
        self.logger = logging_service.get_logger(self.__class__.__name__)
        
        # Load UI
        uic.loadUi(ui_file, self)
        
        # Setup panel
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Override to setup UI components"""
        pass
    
    def connect_signals(self):
        """Override to connect signals"""
        pass
    
    def on_show(self):
        """Called when panel becomes visible"""
        pass
    
    def get_context_actions(self):
        """Return list of (text, callback) tuples for context actions"""
        return []
    
    def get_title(self):
        """Return panel title"""
        return ""
