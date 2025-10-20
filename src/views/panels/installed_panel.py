"""Installed packages panel controller"""
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from .base_panel import BasePanel
from workers.installed_packages_worker import InstalledPackagesWorker
from widgets.virtual_installed_container import VirtualInstalledContainer


class InstalledPanel(BasePanel):
    """Panel for displaying installed packages"""
    
    remove_requested = pyqtSignal(str)
    
    def setup_ui(self):
        """Setup installed panel UI"""
        # Replace scroll area with virtual container
        self.virtual_container = VirtualInstalledContainer()
        self.virtual_container.remove_requested.connect(self.remove_requested.emit)
        
        # Replace in layout
        parent_layout = self.installedScrollArea.parent().layout()
        if parent_layout:
            parent_layout.replaceWidget(self.installedScrollArea, self.virtual_container)
            self.installedScrollArea.setParent(None)
    
    def on_show(self):
        """Load installed packages when shown"""
        self.load_packages()
    
    def get_title(self):
        """Return panel title"""
        return "Installed Packages"
    
    def load_packages(self):
        """Load installed packages using worker thread"""
        print("[InstalledPanel] load_packages() called")
        
        # Get APT backend
        apt_backend = self.package_manager.get_backend('apt')
        if not apt_backend:
            print("[InstalledPanel] ERROR: APT backend not found")
            return
        
        # Create and start worker
        print("[InstalledPanel] Creating worker thread")
        self.worker = InstalledPackagesWorker(apt_backend, self.lmdb_manager)
        self.worker.initial_batch_signal.connect(self.on_initial_loaded)
        self.worker.remaining_batch_signal.connect(self.on_remaining_loaded)
        self.worker.error_signal.connect(self.on_error)
        print("[InstalledPanel] Starting worker thread")
        self.worker.start()
    
    def on_initial_loaded(self, packages):
        """Handle initial batch of packages"""
        print(f"[InstalledPanel] on_initial_loaded() called with {len(packages)} packages")
        self.virtual_container.set_packages(packages)
    
    def on_remaining_loaded(self, packages):
        """Handle remaining batch of packages"""
        print(f"[InstalledPanel] on_remaining_loaded() called with {len(packages)} packages")
        self.virtual_container.add_packages(packages)
    
    def on_error(self, error_message):
        """Handle error loading packages"""
        print(f"[InstalledPanel] ERROR: {error_message}")
        self.virtual_container.set_packages([])
