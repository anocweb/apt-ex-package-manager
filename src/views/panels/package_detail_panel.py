"""Package detail panel controller"""
from PyQt6.QtCore import pyqtSignal
from .base_panel import BasePanel


class PackageDetailPanel(BasePanel):
    """Panel for displaying package details"""
    
    back_requested = pyqtSignal()
    install_requested = pyqtSignal(str, str)
    remove_requested = pyqtSignal(str, str)
    
    def __init__(self, ui_file, package_manager, lmdb_manager, logging_service, app_settings):
        self.current_package = None
        self.return_panel = None
        super().__init__(ui_file, package_manager, lmdb_manager, logging_service, app_settings)
        self.backButton.clicked.connect(self.on_back)
        self.actionButton.clicked.connect(self.on_action)
    
    def show_package(self, package_info, return_panel):
        """Display package details"""
        self.current_package = package_info
        self.return_panel = return_panel
        
        # Set basic info
        self.nameLabel.setText(package_info.get('name', 'Unknown'))
        self.summaryLabel.setText(package_info.get('summary', package_info.get('description', '')[:100]))
        self.descriptionLabel.setText(package_info.get('description', 'No description available'))
        
        # Set version
        version = package_info.get('version', 'Unknown')
        self.versionLabel.setText(f"Version: {version}")
        
        # Set backend
        backend = package_info.get('backend', 'apt').upper()
        self.backendLabel.setText(backend)
        
        # Set action button
        is_installed = package_info.get('installed', False)
        if is_installed:
            self.actionButton.setText("🗑 Remove")
            self.actionButton.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #FF5252;
                }
            """)
        else:
            self.actionButton.setText("⬇ Install")
            self.actionButton.setStyleSheet("""
                QPushButton {
                    background-color: palette(highlight);
                    color: palette(highlighted-text);
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: palette(dark);
                }
            """)
    
    def on_back(self):
        """Handle back button"""
        self.back_requested.emit()
    
    def on_action(self):
        """Handle install/remove action"""
        if not self.current_package:
            return
        
        name = self.current_package.get('name')
        backend = self.current_package.get('backend', 'apt')
        is_installed = self.current_package.get('installed', False)
        
        if is_installed:
            self.remove_requested.emit(name, backend)
        else:
            self.install_requested.emit(name, backend)
    
    def get_title(self):
        """Return panel title"""
        if self.current_package:
            return self.current_package.get('name', 'Package Details')
        return 'Package Details'
