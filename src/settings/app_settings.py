from PyQt6.QtCore import QSettings
from typing import Any, Optional, List
import os

class AppSettings:
    """Application settings manager using QSettings"""
    
    def __init__(self):
        self.settings = QSettings("apt-ex-package-manager", "Apt-Ex Package Manager")
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default settings if not already set"""
        defaults = {
            'default_repository': 'apt',
            'backend_priority': [],
            'sidebar_width': 220,
            'last_selected_page': 'home',
            'plugin_settings': {},
            'ui_theme': 'system',
            'file_logging_enabled': False,
            'log_directory': os.path.join(os.path.expanduser('~'), '.local', 'share', 'apt-ex-package-manager', 'logs'),
            'odrs_enabled': True,
            'operation_panel_height': 300,
            'update_check_enabled': True,
            'update_check_interval': 240,
            'last_update_check': '',
            'show_tray_icon': True
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
    
    def get_plugin_setting(self, backend_id: str, key: str, default: Any = None) -> Any:
        """Get plugin-specific setting"""
        plugin_settings = self.get('plugin_settings', {})
        return plugin_settings.get(backend_id, {}).get(key, default)
    
    def set_plugin_setting(self, backend_id: str, key: str, value: Any):
        """Set plugin-specific setting"""
        plugin_settings = self.get('plugin_settings', {})
        if backend_id not in plugin_settings:
            plugin_settings[backend_id] = {}
        plugin_settings[backend_id][key] = value
        self.set('plugin_settings', plugin_settings)
    
    def get_all_plugin_settings(self, backend_id: str) -> dict:
        """Get all settings for a specific plugin"""
        plugin_settings = self.get('plugin_settings', {})
        return plugin_settings.get(backend_id, {})
    
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
    
    def get_file_logging_enabled(self) -> bool:
        """Get file logging preference"""
        return self.get('file_logging_enabled', False)
    
    def set_file_logging_enabled(self, enabled: bool):
        """Set file logging preference"""
        self.set('file_logging_enabled', enabled)
    
    def get_log_directory(self) -> str:
        """Get log directory path"""
        default_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'apt-ex-package-manager', 'logs')
        return self.get('log_directory', default_dir)
    
    def set_log_directory(self, directory: str):
        """Set log directory path"""
        self.set('log_directory', directory)
    
    def get_odrs_enabled(self) -> bool:
        """Get ODRS (Open Desktop Ratings Service) preference"""
        try:
            value = self.get('odrs_enabled', True)
            return value if isinstance(value, bool) else str(value).lower() == 'true'
        except Exception:
            return True
    
    def set_odrs_enabled(self, enabled: bool):
        """Set ODRS (Open Desktop Ratings Service) preference"""
        self.set('odrs_enabled', enabled)
    
    def get_backend_priority(self) -> List[str]:
        """Get ordered list of backend IDs by priority"""
        priority = self.get('backend_priority', [])
        return priority if isinstance(priority, list) else []
    
    def set_backend_priority(self, backends: List[str]):
        """Set ordered list of backend IDs by priority"""
        self.set('backend_priority', backends)
    
    def get_backend_setting(self, backend_id: str, key: str, default=None):
        """Get backend-specific setting"""
        return self.get_plugin_setting(backend_id, key, default)
    
    def set_backend_setting(self, backend_id: str, key: str, value):
        """Set backend-specific setting"""
        self.set_plugin_setting(backend_id, key, value)
    
    def get_operation_panel_height(self) -> int:
        """Get operation panel height"""
        return int(self.get('operation_panel_height', 300))
    
    def set_operation_panel_height(self, height: int):
        """Set operation panel height"""
        self.set('operation_panel_height', height)
    
    def get_update_check_enabled(self) -> bool:
        """Get update check enabled preference"""
        value = self.get('update_check_enabled', True)
        return value if isinstance(value, bool) else str(value).lower() == 'true'
    
    def set_update_check_enabled(self, enabled: bool):
        """Set update check enabled preference"""
        self.set('update_check_enabled', enabled)
    
    def get_update_check_interval(self) -> int:
        """Get update check interval in minutes"""
        return int(self.get('update_check_interval', 240))
    
    def set_update_check_interval(self, minutes: int):
        """Set update check interval in minutes"""
        self.set('update_check_interval', minutes)
    
    def get_last_update_check(self) -> str:
        """Get last update check timestamp"""
        return self.get('last_update_check', '')
    
    def set_last_update_check(self, timestamp: str):
        """Set last update check timestamp"""
        self.set('last_update_check', timestamp)
    
    def get_show_tray_icon(self) -> bool:
        """Get show tray icon preference"""
        value = self.get('show_tray_icon', True)
        return value if isinstance(value, bool) else str(value).lower() == 'true'
    
    def set_show_tray_icon(self, show: bool):
        """Set show tray icon preference"""
        self.set('show_tray_icon', show)