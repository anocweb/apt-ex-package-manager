"""Category panel controller"""
from PyQt6.QtCore import pyqtSignal
from .base_panel import BasePanel
from widgets.virtual_category_container import VirtualCategoryContainer


class CategoryPanel(BasePanel):
    """Panel for displaying packages by category"""
    
    install_requested = pyqtSignal(str)
    remove_requested = pyqtSignal(str)
    refresh_requested = pyqtSignal()
    package_selected = pyqtSignal(dict)
    
    def __init__(self, ui_file, package_manager, lmdb_manager, logging_service, app_settings):
        self.current_category = None
        super().__init__(ui_file, package_manager, lmdb_manager, logging_service, app_settings)
    
    def setup_ui(self):
        """Setup category panel UI"""
        # Replace category scroll area with virtual scrolling container
        self.virtual_category_container = VirtualCategoryContainer()
        self.categoryLayout.replaceWidget(self.categoryScrollArea, self.virtual_category_container)
        self.categoryScrollArea.setParent(None)
        
        # Connect signals
        self.virtual_category_container.install_requested.connect(self.on_install_or_remove)
        self.virtual_category_container.package_selected.connect(self.package_selected.emit)
    
    def on_install_or_remove(self, package_name):
        """Handle install or remove request"""
        # Check if package is installed to determine which signal to emit
        try:
            from cache import PackageCacheModel
            pkg_cache = PackageCacheModel(self.lmdb_manager, 'apt')
            package = pkg_cache.get_package(package_name)
            
            if package and package.is_installed:
                self.remove_requested.emit(package_name)
            else:
                self.install_requested.emit(package_name)
        except:
            self.install_requested.emit(package_name)
    
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
        self.virtual_category_container.verticalScrollBar().setValue(0)
        
        # Get packages from cache by section
        try:
            from cache import PackageCacheModel
            pkg_cache = PackageCacheModel(self.lmdb_manager, 'apt')
            
            if category == 'all':
                packages = pkg_cache.get_all_packages(limit=100)
            else:
                # Get section mapping from backend
                apt_backend = self.package_manager.get_backend('apt')
                if not apt_backend:
                    self.virtual_category_container.set_packages([])
                    return
                
                mapping = apt_backend.get_sidebar_category_mapping()
                sections = mapping.get(category, [])
                
                # Load packages from cache by section
                packages = []
                for section in sections:
                    section_packages = pkg_cache.get_packages_by_section(section)
                    packages.extend(section_packages)
                    if len(packages) >= 100:
                        break
                packages = packages[:100]
            
            self.virtual_category_container.set_packages(packages)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading category {category}: {e}")
            self.virtual_category_container.set_packages([])
    
    def on_refresh(self):
        """Handle refresh request"""
        self.refresh_requested.emit()
