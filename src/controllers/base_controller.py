from abc import ABC, abstractmethod
from typing import List, Set, Dict, Optional

class BasePackageController(ABC):
    """Abstract base class for package management backends"""
    
    @property
    @abstractmethod
    def backend_id(self) -> str:
        """Unique backend identifier (e.g., 'apt', 'flatpak')"""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for UI (e.g., 'APT Packages')"""
        pass
    
    @property
    def version(self) -> str:
        """Plugin version (e.g., '1.0.0')"""
        return "1.0.0"
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available on system"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Set[str]:
        """Return supported operations"""
        pass
    
    @abstractmethod
    def search_packages(self, query: str) -> List:
        """Search for packages by name/description"""
        pass
    
    @abstractmethod
    def install_package(self, package_id: str) -> bool:
        """Install a package"""
        pass
    
    @abstractmethod
    def remove_package(self, package_id: str) -> bool:
        """Remove a package"""
        pass
    
    @abstractmethod
    def get_installed_packages(self, limit: int = None, offset: int = 0) -> List:
        """Get list of installed packages"""
        pass
    
    def get_upgradable_packages(self) -> List[Dict]:
        """Get packages with available updates"""
        return []
    
    def update_package(self, package_id: str) -> bool:
        """Update a single package"""
        return False
    
    def get_categories(self) -> List[str]:
        """Get available categories"""
        return []
    
    def get_packages_by_category(self, category: str) -> List:
        """Get packages in a category"""
        return []
    
    def map_to_sidebar_category(self, backend_category: str) -> Optional[str]:
        """Map backend-specific category to sidebar category"""
        return None
    
    def get_sidebar_category_mapping(self) -> Dict[str, List[str]]:
        """Get mapping of sidebar categories to backend categories"""
        return {}
    
    def get_all_packages_for_cache(self) -> List[Dict]:
        """Get all packages for caching (optional)"""
        return []
    
    def update_installed_status(self, lmdb_manager) -> bool:
        """Update installed status in cache (optional)"""
        return False
    
    def get_settings_widget(self, parent=None):
        """Return QWidget for backend-specific settings (optional)
        
        Note: If this method returns a widget, get_settings_schema() will be ignored.
        Do not implement both - use either custom widget OR schema, not both.
        """
        return None
    
    def get_settings_schema(self) -> Dict:
        """Return settings schema for this backend (optional)
        
        Note: This is ignored if get_settings_widget() returns a widget.
        Do not implement both - use either custom widget OR schema, not both.
        """
        return {}
    
    def on_settings_changed(self, setting_key: str, value):
        """Called when a setting is changed (optional)"""
        pass
    
    def get_system_dependencies(self) -> List[Dict]:
        """Return list of required system dependencies with version constraints
        
        Returns:
            List of dicts with keys: name, command, package, min_version, version_command
            Example: [{
                'name': 'Flatpak',
                'command': 'flatpak',
                'package': 'flatpak',
                'min_version': '1.12.0',
                'version_command': ['flatpak', '--version']
            }]
        """
        return []
    
    def get_python_dependencies(self) -> List[str]:
        """Return list of required Python packages with pip-style version specs
        
        Returns:
            List of package specs like: ['PyGObject>=3.40.0', 'requests>=2.25.0']
        """
        return []
