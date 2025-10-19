"""Installed packages panel controller"""
from PyQt6.QtWidgets import QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from .base_panel import BasePanel
from workers.installed_packages_worker import InstalledPackagesWorker
from widgets.installed_list_item import InstalledListItem


class InstalledPanel(BasePanel):
    """Panel for displaying installed packages"""
    
    remove_requested = pyqtSignal(str)
    
    def setup_ui(self):
        """Setup installed panel UI"""
        scroll_widget = self.installedScrollArea.widget()
        if not scroll_widget.layout():
            from PyQt6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(scroll_widget)
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)
    
    def on_show(self):
        """Load installed packages when shown"""
        self.load_packages()
    
    def get_title(self):
        """Return panel title"""
        return "Installed Packages"
    
    def load_packages(self):
        """Load installed packages using worker thread"""
        scroll_widget = self.installedScrollArea.widget()
        container_layout = scroll_widget.layout()
        
        # Clear existing items
        while container_layout.count():
            item = container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get APT backend
        apt_backend = self.package_manager.get_backend('apt')
        if not apt_backend:
            return
        
        # Create and start worker
        self.worker = InstalledPackagesWorker(apt_backend, self.lmdb_manager)
        self.worker.initial_batch_signal.connect(self.on_initial_loaded)
        self.worker.remaining_batch_signal.connect(self.on_remaining_loaded)
        self.worker.error_signal.connect(self.on_error)
        self.worker.start()
    
    def on_initial_loaded(self, packages):
        """Handle initial batch of packages"""
        scroll_widget = self.installedScrollArea.widget()
        container_layout = scroll_widget.layout()
        
        # Clear loading message
        while container_layout.count():
            item = container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not packages:
            no_packages_label = QLabel("No packages installed")
            no_packages_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_packages_label.setStyleSheet("font-size: 18px; color: palette(window-text);")
            
            top_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            container_layout.addItem(top_spacer)
            container_layout.addWidget(no_packages_label)
            bottom_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            container_layout.addItem(bottom_spacer)
        else:
            for pkg_info in packages:
                item = InstalledListItem(pkg_info)
                item.remove_requested.connect(self.remove_requested.emit)
                container_layout.addWidget(item)
        
        scroll_widget.updateGeometry()
        self.installedScrollArea.updateGeometry()
    
    def on_remaining_loaded(self, packages):
        """Handle remaining batch of packages"""
        scroll_widget = self.installedScrollArea.widget()
        container_layout = scroll_widget.layout()
        
        # Remove spacer if exists
        if container_layout.count() > 0:
            last_item = container_layout.itemAt(container_layout.count() - 1)
            if last_item.spacerItem():
                container_layout.removeItem(last_item)
        
        # Add remaining packages
        for pkg_info in packages:
            item = InstalledListItem(pkg_info)
            item.remove_requested.connect(self.remove_requested.emit)
            container_layout.addWidget(item)
        
        # Add spacer at bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        container_layout.addItem(spacer)
        
        scroll_widget.updateGeometry()
        self.installedScrollArea.updateGeometry()
    
    def on_error(self, error_message):
        """Handle error loading packages"""
        scroll_widget = self.installedScrollArea.widget()
        container_layout = scroll_widget.layout()
        
        # Clear loading message
        while container_layout.count():
            item = container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        error_label = QLabel(f"Error loading installed packages: {error_message}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: #FF6B6B; font-size: 14px;")
        container_layout.addWidget(error_label)
