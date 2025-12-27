"""Centralized resource path resolver for development and system-wide installation"""
import os
from typing import Optional, List


class PathResolver:
    """Resolves paths for UI files, icons, plugins, and stylesheets"""
    
    _project_root = None
    
    @classmethod
    def _get_project_root(cls) -> str:
        """Get project root directory"""
        if cls._project_root is None:
            # Start from this file's location and go up to find project root
            current = os.path.dirname(os.path.abspath(__file__))
            while current != '/':
                if os.path.exists(os.path.join(current, 'setup.py')):
                    cls._project_root = current
                    break
                current = os.path.dirname(current)
            else:
                # Fallback: assume we're in src/utils
                cls._project_root = os.path.dirname(os.path.dirname(current))
        return cls._project_root
    
    @classmethod
    def _find_resource(cls, relative_path: str, resource_type: str) -> Optional[str]:
        """Find resource in user config, system, or development paths"""
        search_paths = []
        
        if resource_type == 'plugins':
            search_paths = [
                os.path.expanduser('~/.config/apt-ex-package-manager/plugins'),
                '/usr/share/apt-ex-package-manager/plugins',
                os.path.join(cls._get_project_root(), 'src', 'controllers', 'plugins')
            ]
        else:
            # For ui, icons, styles
            search_paths = [
                os.path.expanduser(f'~/.config/apt-ex-package-manager/{resource_type}'),
                f'/usr/share/apt-ex-package-manager/{resource_type}',
                os.path.join(cls._get_project_root(), 'src', resource_type)
            ]
        
        for base_path in search_paths:
            full_path = os.path.join(base_path, relative_path) if relative_path else base_path
            if os.path.exists(full_path):
                return full_path
        
        return None
    
    @classmethod
    def get_ui_path(cls, relative_path: str) -> str:
        """Get path to UI file (panels/*, widgets/*, windows/*)"""
        path = cls._find_resource(relative_path, 'ui')
        if not path:
            raise FileNotFoundError(f"UI file not found: {relative_path}")
        return path
    
    @classmethod
    def get_icon_path(cls, relative_path: str) -> str:
        """Get path to icon file"""
        path = cls._find_resource(relative_path, 'icons')
        if not path:
            raise FileNotFoundError(f"Icon file not found: {relative_path}")
        return path
    
    @classmethod
    def get_stylesheet_path(cls, relative_path: str) -> str:
        """Get path to stylesheet file (in ui/styles/ subdirectory)"""
        # Stylesheets are in ui/styles/ subdirectory
        path = cls._find_resource(f'styles/{relative_path}', 'ui')
        if not path:
            raise FileNotFoundError(f"Stylesheet file not found: {relative_path}")
        return path
    
    @classmethod
    def get_plugin_paths(cls) -> List[str]:
        """Get list of plugin directories to search"""
        paths = [
            os.path.expanduser('~/.config/apt-ex-package-manager/plugins'),
            '/usr/share/apt-ex-package-manager/plugins',
            os.path.join(cls._get_project_root(), 'src', 'controllers', 'plugins')
        ]
        return [p for p in paths if os.path.exists(p)]
