from .apt_controller import APTController
from .base_controller import BasePackageController
from models.package_model import Package
from cache import LMDBManager
from utils.dependency_checker import DependencyChecker
from utils.path_resolver import PathResolver
from typing import Dict, List, Optional
import os
import sys
import importlib.util

class PackageManager:
    def __init__(self, lmdb_manager: LMDBManager, logging_service=None, app_settings=None):
        self.lmdb_manager = lmdb_manager
        self.logging_service = logging_service
        self.logger = logging_service.get_logger('package_manager') if logging_service else None
        self.app_settings = app_settings
        self.backends: Dict[str, BasePackageController] = {}
        self.plugin_status: Dict[str, Dict] = {}
        self.default_backend = 'apt'
        
        # Maintain backward compatibility
        self.apt_controller = APTController(lmdb_manager, logging_service)
        
        # Auto-discover and register plugins
        self._discover_plugins()
        
        # Load backend priority from settings
        if app_settings:
            self._load_backend_priority()
    
    def _discover_plugins(self):
        """Auto-discover and register backend plugins"""
        plugin_paths = PathResolver.get_plugin_paths()
        
        for plugin_dir in plugin_paths:
            if not os.path.exists(plugin_dir):
                continue
            
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
            
            for filename in os.listdir(plugin_dir):
                if filename.endswith('_plugin.py'):
                    module_name = filename[:-3]
                    try:
                        spec = importlib.util.spec_from_file_location(
                            module_name, 
                            os.path.join(plugin_dir, filename)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                issubclass(attr, BasePackageController) and 
                                attr is not BasePackageController):
                                plugin = attr(self.lmdb_manager, self.logging_service)
                                self.register_backend(plugin)
                                break
                    except Exception as e:
                        if self.logging_service:
                            self.logging_service.error(f"Failed to load plugin {filename}: {e}")
    
    def register_backend(self, controller: BasePackageController):
        """Register a backend plugin"""
        # Validate settings implementation
        has_custom_widget = controller.get_settings_widget() is not None
        has_schema = bool(controller.get_settings_schema())
        
        if has_custom_widget and has_schema:
            if self.logging_service:
                logger = self.logging_service.get_logger('package_manager')
                logger.warning(
                    f"Plugin '{controller.backend_id}' implements both get_settings_widget() and "
                    f"get_settings_schema(). Only one should be implemented. "
                    f"Standard settings schema will be ignored in favor of custom widget."
                )
        
        # Check dependencies
        dep_status = DependencyChecker.check_plugin_dependencies(controller)
        
        status_info = {
            'backend_id': controller.backend_id,
            'display_name': controller.display_name,
            'version': controller.version,
            'available': controller.is_available() and dep_status['all_satisfied'],
            'plugin': controller if (controller.is_available() and dep_status['all_satisfied']) else None,
            'capabilities': controller.get_capabilities() if controller.is_available() else set(),
            'dependencies': {
                'system': dep_status['system'],
                'python': dep_status['python']
            },
            'missing_dependencies': dep_status['missing']
        }
        
        self.plugin_status[controller.backend_id] = status_info
        
        if status_info['available']:
            self.backends[controller.backend_id] = controller
            if self.logging_service:
                self.logging_service.info(f"Registered backend: {controller.display_name} ({controller.backend_id})")
        else:
            if self.logging_service:
                reason = ', '.join(dep_status['missing']) if dep_status['missing'] else 'not available'
                self.logging_service.debug(f"Backend not available: {controller.display_name} - {reason}")
    
    def get_backend(self, backend: str = None) -> Optional[BasePackageController]:
        """Get backend controller by ID"""
        backend = backend or self.default_backend
        return self.backends.get(backend)
    
    def get_available_backends(self) -> List[str]:
        """Get list of available backend IDs"""
        return list(self.backends.keys())
    
    def get_plugin_status(self) -> Dict[str, Dict]:
        """Get detailed status of all plugins"""
        return self.plugin_status
    
    def get_plugin_settings_widget(self, backend_id: str, parent=None):
        """Get settings widget for a plugin (custom widget takes precedence over schema)"""
        controller = self.get_backend(backend_id)
        if not controller:
            return None
        
        # Custom widget takes precedence
        custom_widget = controller.get_settings_widget(parent)
        if custom_widget:
            return custom_widget
        
        # Fall back to schema-based widget
        schema = controller.get_settings_schema()
        if schema:
            # Import here to avoid circular dependency
            from utils.settings_widget_factory import SettingsWidgetFactory
            return SettingsWidgetFactory.create_from_schema(schema, parent)
        
        return None
    
    def refresh_plugin_status(self):
        """Re-check all plugin dependencies"""
        self.backends.clear()
        self.plugin_status.clear()
        self._discover_plugins()
        if self.app_settings:
            self._load_backend_priority()
    
    def get_backends_by_priority(self) -> List[BasePackageController]:
        """Get backends ordered by priority"""
        if not self.app_settings:
            return list(self.backends.values())
        
        priority_order = self.app_settings.get_backend_priority()
        if not priority_order:
            return list(self.backends.values())
        
        ordered = []
        for backend_id in priority_order:
            if backend_id in self.backends:
                ordered.append(self.backends[backend_id])
        
        # Add any backends not in priority list
        for backend in self.backends.values():
            if backend not in ordered:
                ordered.append(backend)
        
        return ordered
    
    def _load_backend_priority(self):
        """Load backend priority from settings"""
        priority = self.app_settings.get_backend_priority()
        if priority and len(priority) > 0:
            # Use first in priority as default
            if priority[0] in self.backends:
                self.default_backend = priority[0]
    
    def set_backend_priority(self, priority_order: List[str]):
        """Set backend priority order"""
        if self.app_settings:
            self.app_settings.set_backend_priority(priority_order)
            if priority_order and len(priority_order) > 0:
                self.default_backend = priority_order[0]
    
    def search_packages(self, query, backend: str = None):
        """Search packages across backends (respects priority order)"""
        if backend:
            controller = self.get_backend(backend)
            return controller.search_packages(query) if controller else []
        
        # Search all backends in priority order
        results = []
        for controller in self.get_backends_by_priority():
            if 'search' in controller.get_capabilities():
                results.extend(controller.search_packages(query))
        
        # Fallback to old controller if no plugins
        if not results:
            return self.apt_controller.search_packages(query)
        return results
    
    def install_package(self, package_name, backend: str = None):
        """Install package using specified or default backend"""
        controller = self.get_backend(backend)
        if controller:
            return controller.install_package(package_name)
        return self.apt_controller.install_package(package_name)
    
    def remove_package(self, package_name, backend: str = None):
        """Remove package using specified or default backend"""
        controller = self.get_backend(backend)
        if controller:
            return controller.remove_package(package_name)
        return self.apt_controller.remove_package(package_name)
    
    def get_installed_packages(self, backend: str = None, limit: int = None, offset: int = 0):
        """Get installed packages from specified or all backends"""
        if backend:
            controller = self.get_backend(backend)
            return controller.get_installed_packages(limit, offset) if controller else []
        
        # Get from all backends
        results = []
        for controller in self.backends.values():
            if 'list_installed' in controller.get_capabilities():
                results.extend(controller.get_installed_packages(limit, offset))
        
        # Fallback to old controller if no plugins
        if not results:
            return self.apt_controller.get_installed_packages()
        return results
    
    def get_upgradable_packages(self, backend: str = None) -> List[Dict]:
        """Get packages with available updates"""
        if backend:
            controller = self.get_backend(backend)
            return controller.get_upgradable_packages() if controller else []
        
        # Get from all backends
        results = []
        for controller in self.backends.values():
            if 'list_updates' in controller.get_capabilities():
                results.extend(controller.get_upgradable_packages())
        
        # Fallback to old controller if no plugins
        if not results and hasattr(self.apt_controller, 'get_upgradable_packages'):
            return self.apt_controller.get_upgradable_packages()
        return results