"""Category panel controller"""
from PyQt6.QtCore import pyqtSignal
from .base_panel import BasePanel
from widgets.virtual_category_container import VirtualCategoryContainer


class CategoryPanel(BasePanel):
    """Panel for displaying packages by category"""
    
    install_requested = pyqtSignal(str)
    refresh_requested = pyqtSignal()
    
    def __init__(self, ui_file, package_manager, lmdb_manager, logging_service, app_settings):
        self.current_category = None
        super().__init__(ui_file, package_manager, lmdb_manager, logging_service, app_settings)
    
    def setup_ui(self):
        """Setup category panel UI"""
        # Replace category scroll area with virtual scrolling container
        self.virtual_category_container = VirtualCategoryContainer()
        self.categoryLayout.replaceWidget(self.categoryScrollArea, self.virtual_category_container)
        self.categoryScrollArea.setParent(None)
        
        # Connect install signal
        self.virtual_category_container.install_requested.connect(self.install_requested.emit)
    
    def get_context_actions(self):
        """Return context actions for category panel"""
        return [("🔄 Refresh Cache", self.on_refresh)]
    
    def get_title(self):
        """Return panel title"""
        if self.current_category:
            return f"{self.current_category.title()} Packages"
        return "Category Packages"
    
    def load_category(self, category):
        """Load packages for a category"""
        self.current_category = category
        self.virtual_category_container.set_packages([])
        self.virtual_category_container.verticalScrollBar().setValue(0)
        # TODO: Load packages from cache
    
    def on_refresh(self):
        """Handle refresh request"""
        self.refresh_requested.emit()
