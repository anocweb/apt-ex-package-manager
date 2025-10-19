from .apt_controller import APTController
from .base_controller import BasePackageController
from models.package_model import Package
from cache import LMDBManager
from typing import Dict, List, Optional
import os
import sys
import importlib.util

class PackageManager:
    def __init__(self, lmdb_manager: LMDBManager, logging_service=None):
        self.lmdb_manager = lmdb_manager
        self.logging_service = logging_service
        self.backends: Dict[str, BasePackageController] = {}
        self.default_backend = 'apt'
        
        # Maintain backward compatibility
        self.apt_controller = APTController(lmdb_manager, logging_service)
        
        # Auto-discover and register plugins
        self._discover_plugins()
    
    def _discover_plugins(self):
        """Auto-discover and register backend plugins"""
        plugin_paths = [
            os.path.expanduser('~/.config/apt-ex-package-manager/plugins'),
            '/usr/share/apt-ex-package-manager/plugins',
            os.path.join(os.path.dirname(__file__), 'plugins'),
        ]
        
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
        if controller.is_available():
            self.backends[controller.backend_id] = controller
            if self.logging_service:
                self.logging_service.info(f"Registered backend: {controller.display_name} ({controller.backend_id})")
        else:
            if self.logging_service:
                self.logging_service.debug(f"Backend not available: {controller.display_name} ({controller.backend_id})")
    
    def get_backend(self, backend: str = None) -> Optional[BasePackageController]:
        """Get backend controller by ID"""
        backend = backend or self.default_backend
        return self.backends.get(backend)
    
    def get_available_backends(self) -> List[str]:
        """Get list of available backend IDs"""
        return list(self.backends.keys())
    
    def search_packages(self, query, backend: str = None):
        """Search packages across backends"""
        if backend:
            controller = self.get_backend(backend)
            return controller.search_packages(query) if controller else []
        
        # Search all backends
        results = []
        for controller in self.backends.values():
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