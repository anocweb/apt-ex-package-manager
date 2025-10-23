"""Plugins panel for managing backend plugins"""
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6 import uic
from widgets.plugin_card import PluginCard

class PluginsPanel(QWidget):
    """Panel for displaying plugin status and dependencies"""
    
    refresh_requested = pyqtSignal()
    
    def __init__(self, ui_file, package_manager, lmdb_manager, logging_service, app_settings):
        super().__init__()
        self.package_manager = package_manager
        self.lmdb_manager = lmdb_manager
        self.logging_service = logging_service
        self.app_settings = app_settings
        self.logger = logging_service.get_logger('ui') if logging_service else None
        
        uic.loadUi(ui_file, self)
        
    def get_title(self) -> str:
        return "Plugins"
    
    def get_context_actions(self):
        return [
            ("🔄 Refresh", self.refresh_plugins)
        ]
    
    def on_show(self):
        """Called when panel is shown"""
        self.load_plugins()
    
    def load_plugins(self):
        """Load and display all plugins"""
        # Clear existing
        layout = self.pluginsLayout
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Get plugin status
        plugin_status = self.package_manager.get_plugin_status()
        
        if not plugin_status:
            label = QLabel("No plugins discovered")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            return
        
        # Create card for each plugin
        for backend_id, status in plugin_status.items():
            card = PluginCard(status)
            layout.addWidget(card)
    

    
    def refresh_plugins(self):
        """Refresh plugin status"""
        if self.logger:
            self.logger.info("Refreshing plugin status")
        self.package_manager.refresh_plugin_status()
        self.load_plugins()
        self.refresh_requested.emit()
