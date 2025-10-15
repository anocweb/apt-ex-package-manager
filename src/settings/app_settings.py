from PyQt6.QtCore import QSettings
from typing import Any, Optional

class AppSettings:
    """Application settings manager using QSettings"""
    
    def __init__(self):
        self.settings = QSettings("apt-ex-package-manager", "Apt-Ex Package Manager")
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default settings if not already set"""
        defaults = {
            'default_repository': 'apt',
            'window_geometry': None,
            'window_state': None,
            'sidebar_width': 220,
            'last_selected_page': 'home',
            'repository_preferences': {},
            'ui_theme': 'system'
        }
        
        for key, value in defaults.items():
            if not self.settings.contains(key):
                self.settings.setValue(key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return self.settings.value(key, default)
    
    def set(self, key: str, value: Any):
        """Set setting value and save immediately"""
        self.settings.setValue(key, value)
        self.settings.sync()
    
    def get_default_repository(self) -> str:
        """Get default repository type"""
        return self.get('default_repository', 'apt')
    
    def set_default_repository(self, repo_type: str):
        """Set default repository type"""
        self.set('default_repository', repo_type)
    
    def get_repository_preference(self, repo_type: str, key: str, default: Any = None) -> Any:
        """Get repository-specific preference"""
        prefs = self.get('repository_preferences', {})
        return prefs.get(repo_type, {}).get(key, default)
    
    def set_repository_preference(self, repo_type: str, key: str, value: Any):
        """Set repository-specific preference"""
        prefs = self.get('repository_preferences', {})
        if repo_type not in prefs:
            prefs[repo_type] = {}
        prefs[repo_type][key] = value
        self.set('repository_preferences', prefs)
    
    def get_window_geometry(self):
        """Get saved window geometry"""
        return self.get('window_geometry')
    
    def set_window_geometry(self, geometry):
        """Save window geometry"""
        self.set('window_geometry', geometry)
    
    def get_window_state(self):
        """Get saved window state"""
        return self.get('window_state')
    
    def set_window_state(self, state):
        """Save window state"""
        self.set('window_state', state)
    
    def get_sidebar_width(self) -> int:
        """Get sidebar width"""
        return self.get('sidebar_width', 220)
    
    def set_sidebar_width(self, width: int):
        """Set sidebar width"""
        self.set('sidebar_width', width)
    
    def get_last_selected_page(self) -> str:
        """Get last selected page"""
        return self.get('last_selected_page', 'home')
    
    def set_last_selected_page(self, page: str):
        """Set last selected page"""
        self.set('last_selected_page', page)
    
    def clear_all(self):
        """Clear all settings"""
        self.settings.clear()
        self._load_defaults()
    
    def export_settings(self) -> dict:
        """Export all settings to dictionary"""
        settings_dict = {}
        for key in self.settings.allKeys():
            settings_dict[key] = self.settings.value(key)
        return settings_dict
    
    def import_settings(self, settings_dict: dict):
        """Import settings from dictionary"""
        for key, value in settings_dict.items():
            self.set(key, value)