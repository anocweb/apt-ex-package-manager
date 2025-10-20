# Plugin Architecture for Backend Package Managers

> **Status**: PLANNED - Design specification for future implementation
> **Current**: APT controller is monolithic (src/controllers/apt_controller.py)
> **Timeline**: No specific timeline

## Overview

This document describes the planned plugin architecture for adding new package management backends (APT, Flatpak, Snap, AppImage, etc.) to Apt-Ex Package Manager without modifying core code. This is a design specification that will require refactoring the current APT implementation.

## End Goal Architecture

### Directory Structure
```
apt-ex-package-manager/
├── src/
│   ├── controllers/
│   │   ├── base_controller.py          # Abstract base class (NEW)
│   │   ├── package_manager.py          # Plugin registry & coordinator (REFACTOR)
│   │   └── plugins/                    # Plugin directory (NEW)
│   │       ├── __init__.py
│   │       ├── apt_plugin.py           # APT backend plugin
│   │       ├── flatpak_plugin.py       # Flatpak backend plugin
│   │       └── appimage_plugin.py      # AppImage backend plugin
│   ├── models/
│   │   └── package_model.py            # Unified package model (EXISTS)
│   └── repositories/
│       └── base_repository.py          # Repository interface (EXISTS)
```

### Plugin Storage Locations
- **Development**: `src/controllers/plugins/` (source code)
- **System installation**: `/usr/share/apt-ex-package-manager/plugins/` (installed plugins)
- **User plugins** (future): `~/.config/apt-ex-package-manager/plugins/` (user-installed)

**Note**: During installation, built-in plugins are copied to `/usr/share/apt-ex-package-manager/plugins/`. The application loads plugins from the system location when installed, or from `src/controllers/plugins/` when running from source.

## Plugin Interface

### 1. BasePackageController (Abstract Interface)

All backend plugins must inherit from `BasePackageController`:

```python
from abc import ABC, abstractmethod
from typing import List, Set, Dict, Optional
from models.package_model import Package

class BasePackageController(ABC):
    """Abstract base class for package management backends"""
    
    # === Identity & Availability ===
    
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
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available on system"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Set[str]:
        """Return supported operations
        
        Standard capabilities:
        - 'search': Search packages
        - 'install': Install packages
        - 'remove': Remove packages
        - 'update': Update packages
        - 'list_installed': List installed packages
        - 'list_updates': List available updates
        - 'categories': Browse by categories
        - 'ratings': Support ratings/reviews
        """
        pass
    
    # === Core Operations ===
    
    @abstractmethod
    def search_packages(self, query: str) -> List[Package]:
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
    def get_installed_packages(self, limit: int = None, offset: int = 0) -> List[Package]:
        """Get list of installed packages"""
        pass
    
    # === Optional Operations (default implementations) ===
    
    def get_upgradable_packages(self) -> List[Dict]:
        """Get packages with available updates"""
        return []
    
    def update_package(self, package_id: str) -> bool:
        """Update a single package"""
        return False
    
    def get_categories(self) -> List[str]:
        """Get available categories"""
        return []
    
    def get_packages_by_category(self, category: str) -> List[Package]:
        """Get packages in a category"""
        return []
    
    def map_to_sidebar_category(self, backend_category: str) -> Optional[str]:
        """Map backend-specific category to sidebar category
        
        Must return one of the standard sidebar categories:
        - 'games'
        - 'graphics'
        - 'internet'
        - 'multimedia'
        - 'office'
        - 'development'
        - 'system'
        - 'utilities'
        - 'education'
        - 'science'
        - 'accessibility'
        - 'all'
        
        Return None if category doesn't map to sidebar.
        """
        return None
    
    def get_sidebar_category_mapping(self) -> Dict[str, List[str]]:
        """Get mapping of sidebar categories to backend categories
        
        Returns dict mapping sidebar category to list of backend categories.
        Example for APT:
        {
            'games': ['games'],
            'graphics': ['graphics'],
            'internet': ['net', 'web', 'mail'],
            'multimedia': ['sound', 'video'],
            ...
        }
        """
        return {}
    
    # === Cache Integration ===
    
    def get_all_packages_for_cache(self) -> List[Dict]:
        """Get all packages for caching (optional)"""
        return []
    
    def update_installed_status(self, connection_manager) -> bool:
        """Update installed status in cache (optional)"""
        return False
    
    # === Settings Integration ===
    
    def get_settings_widget(self, parent=None):
        """Return QWidget for backend-specific settings (optional)
        
        This widget will be added to the Settings panel under a
        collapsible section for this backend.
        
        Return None if no settings needed.
        """
        return None
    
    def get_settings_schema(self) -> Dict:
        """Return settings schema for this backend (optional)
        
        Schema format:
        {
            'setting_key': {
                'type': 'string|bool|int|list',
                'label': 'Display Label',
                'default': default_value,
                'description': 'Help text',
                'options': [...] # For list type
            }
        }
        
        Settings are stored in AppSettings with key:
        f'{backend_id}.{setting_key}'
        """
        return {}
    
    def on_settings_changed(self, setting_key: str, value):
        """Called when a setting is changed (optional)
        
        Use this to react to setting changes, e.g., refresh data,
        reconnect to services, etc.
        """
        pass
    
    # === Privilege Escalation ===
    
    def get_privilege_helper(self):
        """Return privilege helper client for this backend (optional)
        
        Returns BasePrivilegeHelper instance if backend uses privilege
        helper for elevated operations, None otherwise.
        
        Privilege helpers enable credential caching across multiple
        operations without elevating the entire application.
        """
        return None
    
    def requires_elevation(self, operation: str) -> bool:
        """Check if operation requires privilege elevation
        
        Args:
            operation: Operation name ('install', 'remove', 'update', etc.)
        
        Returns:
            True if operation requires root/admin privileges
        """
        return False
```

### 2. Plugin Registration

Plugins are auto-discovered and registered:

```python
class PackageManager:
    def __init__(self, connection_manager, logging_service=None):
        self.connection_manager = connection_manager
        self.logging_service = logging_service
        self.backends: Dict[str, BasePackageController] = {}
        self.default_backend = 'apt'
        
        # Auto-discover and register plugins
        self._discover_plugins()
    
    def _discover_plugins(self):
        """Auto-discover and register backend plugins"""
        import os
        import sys
        import importlib.util
        
        # Plugin search paths (in priority order)
        plugin_paths = [
            os.path.expanduser('~/.config/apt-ex-package-manager/plugins'),  # User plugins
            '/usr/share/apt-ex-package-manager/plugins',  # System installation
            os.path.join(os.path.dirname(__file__), 'plugins'),  # Development
        ]
        
        for plugin_dir in plugin_paths:
            if not os.path.exists(plugin_dir):
                continue
            
            # Add to Python path if not already there
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)
            
            # Discover plugin files
            for filename in os.listdir(plugin_dir):
                if filename.endswith('_plugin.py'):
                    module_name = filename[:-3]  # Remove .py
                    try:
                        spec = importlib.util.spec_from_file_location(
                            module_name, 
                            os.path.join(plugin_dir, filename)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Find plugin class (e.g., APTPlugin, FlatpakPlugin)
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                issubclass(attr, BasePackageController) and 
                                attr is not BasePackageController):
                                # Instantiate and register
                                plugin = attr(self.connection_manager, self.logging_service)
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
```

### 3. Unified Operations

PackageManager provides unified operations across all backends:

```python
def search_packages(self, query: str, backend: str = None) -> List[Package]:
    """Search packages across backends"""
    if backend:
        return self.backends[backend].search_packages(query)
    
    # Search all backends
    results = []
    for controller in self.backends.values():
        if 'search' in controller.get_capabilities():
            results.extend(controller.search_packages(query))
    return results

def install_package(self, package_id: str, backend: str = None) -> bool:
    """Install package using specified or default backend"""
    backend = backend or self.default_backend
    if backend in self.backends:
        return self.backends[backend].install_package(package_id)
    return False
```

## Implementation Steps

### Phase 1: Create Base Interface (Week 1)

**Step 1.1**: Create `src/controllers/base_controller.py`
- Define `BasePackageController` abstract class
- Define all required and optional methods
- Add capability constants

**Step 1.2**: Create plugin directory structure
```bash
mkdir -p src/controllers/plugins
touch src/controllers/plugins/__init__.py
```

### Phase 2: Refactor Existing APT Controller (Week 1-2)

**Step 2.1**: Convert `APTController` to plugin
- Move `src/controllers/apt_controller.py` → `src/controllers/plugins/apt_plugin.py`
- Rename class: `APTController` → `APTPlugin`
- Inherit from `BasePackageController`
- Implement all required methods
- Add capability declaration

**Step 2.2**: Update imports
- Update all files importing `APTController`
- Temporarily maintain backward compatibility

### Phase 3: Refactor PackageManager (Week 2)

**Step 3.1**: Add plugin registry to `PackageManager`
- Add `self.backends = {}` dictionary
- Add `register_backend()` method
- Add `_discover_plugins()` method

**Step 3.2**: Implement plugin discovery
- Scan `src/controllers/plugins/` directory
- Import and instantiate plugin classes
- Register available backends

**Step 3.3**: Update operation methods
- Change from direct `self.apt_controller.method()` calls
- Route to appropriate backend via `self.backends[backend_id]`
- Support multi-backend operations (search all, etc.)

### Phase 4: Update Views (Week 3)

**Step 4.1**: Remove direct controller access
- Replace `self.package_manager.apt_controller` with `self.package_manager`
- Use unified PackageManager methods

**Step 4.2**: Add backend selection UI
- Add backend filter/selector to search
- Show backend badges on package cards
- Allow user to choose default backend

**Step 4.3**: Handle backend-specific features
- Check capabilities before showing UI elements
- Gracefully handle missing capabilities

### Phase 5: Add Additional Backends (Week 4+)

**Step 5.1**: Create Flatpak plugin
- Create `src/controllers/plugins/flatpak_plugin.py`
- Implement `BasePackageController` interface
- Test and validate

**Step 5.2**: Create AppImage plugin
- Create `src/controllers/plugins/appimage_plugin.py`
- Implement `BasePackageController` interface
- Test and validate

**Step 5.3**: Update documentation
- Document each plugin's capabilities
- Add plugin development guide

## Plugin Documentation

For detailed plugin-specific documentation, see:
- [Plugin Documentation Directory](../plugins/) - Per-plugin documentation
- [APT Plugin](../plugins/apt/) - APT-specific features (locking, caching)
- [Flatpak Plugin](../plugins/flatpak/) - Flatpak-specific features (planned)
- [AppImage Plugin](../plugins/appimage/) - AppImage-specific features (planned)

## Plugin Development Guide

### Creating a New Plugin

1. **Create plugin file**: `src/controllers/plugins/mybackend_plugin.py`

2. **Implement interface**:
```python
from controllers.base_controller import BasePackageController
from models.package_model import Package
from typing import List, Set

class MyBackendPlugin(BasePackageController):
    def __init__(self, connection_manager=None, logging_service=None):
        self.connection_manager = connection_manager
        self.logging_service = logging_service
    
    @property
    def backend_id(self) -> str:
        return 'mybackend'
    
    @property
    def display_name(self) -> str:
        return 'My Backend Packages'
    
    def is_available(self) -> bool:
        # Check if backend is installed
        import shutil
        return shutil.which('mybackend') is not None
    
    def get_capabilities(self) -> Set[str]:
        return {'search', 'install', 'remove', 'list_installed'}
    
    def search_packages(self, query: str) -> List[Package]:
        # Implement search logic
        pass
    
    # ... implement other required methods
```

3. **Test plugin**:
```python
# Test availability
plugin = MyBackendPlugin()
assert plugin.is_available()

# Test capabilities
assert 'search' in plugin.get_capabilities()

# Test operations
results = plugin.search_packages('firefox')
assert len(results) > 0
```

4. **Register plugin**: Auto-discovered on next app start

### Plugin Capabilities

Standard capability strings:

| Capability | Description |
|------------|-------------|
| `search` | Search packages by query |
| `install` | Install packages |
| `remove` | Remove/uninstall packages |
| `update` | Update individual packages |
| `list_installed` | List installed packages |
| `list_updates` | List available updates |
| `categories` | Browse by categories |
| `ratings` | Support ratings/reviews |
| `repositories` | Manage repositories/remotes |
| `dependencies` | Show dependency information |
| `permissions` | Manage app permissions (Flatpak) |

### Category Mapping

Plugins must map their backend-specific categories to the standard sidebar categories:

**Standard Sidebar Categories:**
- `games` - Gaming applications
- `graphics` - Image editing, design tools
- `internet` - Web browsers, email, networking
- `multimedia` - Audio/video players, editors
- `office` - Productivity, documents, editors
- `development` - IDEs, compilers, dev tools
- `system` - System utilities, admin tools
- `utilities` - General utilities, tools
- `education` - Educational software
- `science` - Scientific, math applications
- `accessibility` - Accessibility tools
- `all` - All packages (special category)

**Implementation:**

```python
def get_sidebar_category_mapping(self) -> Dict[str, List[str]]:
    """Map sidebar categories to backend categories"""
    return {
        'games': ['games', 'game'],  # Backend categories that map to 'games'
        'graphics': ['graphics', 'design'],
        'internet': ['network', 'web', 'mail', 'communication'],
        'multimedia': ['audio', 'video', 'sound'],
        'office': ['office', 'productivity', 'text', 'editors'],
        'development': ['devel', 'programming', 'ide'],
        'system': ['system', 'admin', 'core'],
        'utilities': ['utility', 'tools', 'misc'],
        'education': ['education', 'teaching'],
        'science': ['science', 'math', 'engineering'],
        'accessibility': ['accessibility', 'a11y'],
    }

def map_to_sidebar_category(self, backend_category: str) -> Optional[str]:
    """Map a backend category to sidebar category"""
    mapping = self.get_sidebar_category_mapping()
    for sidebar_cat, backend_cats in mapping.items():
        if backend_category.lower() in [c.lower() for c in backend_cats]:
            return sidebar_cat
    return None
```

**Example - APT Sections:**
```python
# APT has sections like 'games', 'net', 'sound', 'devel'
mapping = {
    'games': ['games'],
    'graphics': ['graphics'],
    'internet': ['net', 'web', 'mail'],
    'multimedia': ['sound', 'video'],
    'office': ['editors', 'text', 'doc'],
    'development': ['devel', 'libdevel', 'python', 'perl'],
    'system': ['admin', 'base', 'kernel', 'shells'],
    'utilities': ['utils', 'misc', 'otherosfs'],
}
```

**Example - Flatpak Categories:**
```python
# Flatpak uses FreeDesktop categories
mapping = {
    'games': ['Game'],
    'graphics': ['Graphics'],
    'internet': ['Network', 'WebBrowser', 'Email'],
    'multimedia': ['Audio', 'Video', 'AudioVideo'],
    'office': ['Office', 'TextEditor'],
    'development': ['Development', 'IDE'],
    'system': ['System', 'Settings'],
    'utilities': ['Utility'],
    'education': ['Education'],
    'science': ['Science'],
}
```

### Backend-Specific Metadata

Use `Package.metadata` dict for backend-specific data:

```python
# APT-specific
package.metadata = {
    'section': 'games',
    'priority': 'optional',
    'depends': 'libc6, libx11-6'
}

# Flatpak-specific
package.metadata = {
    'remote': 'flathub',
    'ref': 'app/org.mozilla.Firefox/x86_64/stable',
    'permissions': ['network', 'x11']
}
```

### Plugin Settings Integration

Plugins can provide backend-specific settings that appear in the Settings panel.

**Method 1: Settings Schema (Simple)**

```python
def get_settings_schema(self) -> Dict:
    return {
        'default_remote': {
            'type': 'list',
            'label': 'Default Remote',
            'default': 'flathub',
            'description': 'Default Flatpak remote for installations',
            'options': ['flathub', 'fedora', 'gnome-nightly']
        },
        'auto_update': {
            'type': 'bool',
            'label': 'Auto-update packages',
            'default': True,
            'description': 'Automatically update packages in background'
        },
        'install_scope': {
            'type': 'list',
            'label': 'Installation Scope',
            'default': 'user',
            'description': 'Install packages for user or system',
            'options': ['user', 'system']
        }
    }
```

Settings are automatically rendered in the Settings panel and stored as:
- `flatpak.default_remote`
- `flatpak.auto_update`
- `flatpak.install_scope`

**Method 2: Custom Widget (Advanced)**

```python
def get_settings_widget(self, parent=None):
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
    
    widget = QWidget(parent)
    layout = QVBoxLayout(widget)
    
    # Add custom UI elements
    layout.addWidget(QLabel('Flatpak Remotes'))
    
    add_remote_btn = QPushButton('Add Remote')
    add_remote_btn.clicked.connect(self.show_add_remote_dialog)
    layout.addWidget(add_remote_btn)
    
    return widget
```

**Reacting to Setting Changes:**

```python
def on_settings_changed(self, setting_key: str, value):
    if setting_key == 'default_remote':
        self.default_remote = value
        self.logger.info(f"Default remote changed to: {value}")
    elif setting_key == 'auto_update':
        if value:
            self.start_auto_update_timer()
        else:
            self.stop_auto_update_timer()
```

**Accessing Settings in Plugin:**

```python
from settings.app_settings import AppSettings

class FlatpakPlugin(BasePackageController):
    def __init__(self, connection_manager=None, logging_service=None):
        self.settings = AppSettings()
        self.default_remote = self.settings.get(f'{self.backend_id}.default_remote', 'flathub')
    
    def install_package(self, package_id: str) -> bool:
        remote = self.default_remote
        # Use setting in installation logic
        ...
```

## Migration Checklist

- [ ] Create `BasePackageController` interface
- [ ] Create `plugins/` directory structure
- [ ] Convert `APTController` to `APTPlugin`
- [ ] Add plugin registry to `PackageManager`
- [ ] Implement plugin discovery mechanism
- [ ] Refactor `PackageManager` methods to route to backends
- [ ] Update all views to use unified `PackageManager` API
- [ ] Remove direct `apt_controller` access from views
- [ ] Add backend selection UI components
- [ ] Test with APT plugin only
- [ ] Create Flatpak plugin
- [ ] Create AppImage plugin
- [ ] Update user documentation
- [ ] Add plugin development guide

## Data Structure Requirements

All plugins MUST return standardized data structures. See [Data Structures Documentation](DATA_STRUCTURES.md) for complete specifications.

**Core Models:**
- `Package` - Unified package representation
- `PackageUpdate` - Update information
- `Repository` - Repository/remote source
- `CategoryInfo` - Category with package count

**Required Fields:**
- Package: `package_id`, `name`, `version`, `backend`
- PackageUpdate: `package_id`, `name`, `current_version`, `new_version`, `backend`
- Repository: `id`, `name`, `url`, `backend`

**Return Types:**
- Search/list methods: `List[Package]`
- Update methods: `List[PackageUpdate]`
- Repository methods: `List[Repository]`
- NEVER return `None`, always return empty list on error

## Benefits of Plugin Architecture

1. **Extensibility**: Add new backends without modifying core code
2. **Maintainability**: Each backend isolated in its own module
3. **Testability**: Test backends independently
4. **Flexibility**: Enable/disable backends at runtime
5. **User Choice**: Users can install only needed backends
6. **Community**: Third-party developers can create plugins

## Privilege Escalation Integration

### Overview

Plugins can integrate with privilege escalation helpers to maintain elevated privileges across multiple operations without elevating the entire application. This provides better UX by reducing authentication prompts.

### Architecture

```
Main Application (Unprivileged)
    ↓
PackageManager
    ↓
Backend Plugins (Unprivileged)
    ↓
Privilege Helpers (D-Bus Services, Root)
    ↓
System Package Managers
```

### Plugin Integration

Plugins can optionally provide privilege helpers:

```python
from services.privilege.base_helper import BasePrivilegeHelper

class APTPlugin(BasePackageController):
    def __init__(self, lmdb_manager=None, logging_service=None):
        self._privilege_helper = APTPrivilegeHelper(logging_service)
    
    def get_privilege_helper(self) -> Optional[BasePrivilegeHelper]:
        """Return privilege helper client for this backend"""
        return self._privilege_helper
    
    def requires_elevation(self, operation: str) -> bool:
        """Check if operation requires privilege elevation"""
        return operation in ['install', 'remove', 'update']
    
    def install_package(self, package_name):
        # Try helper first, fallback to pkexec
        if self._privilege_helper.is_available():
            success, message = self._privilege_helper.install_package(package_name)
            return success
        
        # Fallback to pkexec
        return self._install_via_pkexec(package_name)
```

### Backend-Specific Helpers

- **APT**: Uses D-Bus helper with PolicyKit (credential caching)
- **Flatpak**: No helper needed (supports user-level installs)
- **AppImage**: No helper needed (no elevation required)

### Benefits

- **Credential Caching**: PolicyKit caches credentials for 5 minutes
- **Backend Independence**: Each plugin decides if/how to handle privileges
- **Graceful Fallback**: Falls back to pkexec if helper unavailable
- **Security**: Main application remains unprivileged

### Implementation Details

See [Privilege Escalation Implementation Plan](../planning/PRIVILEGE_ESCALATION_IMPLEMENTATION.md) for complete implementation details.

## Future Enhancements

- **Plugin metadata**: Version, author, dependencies
- **Plugin configuration**: Per-plugin settings UI
- **Plugin marketplace**: Discover and install plugins
- **Hot reload**: Load plugins without restart
- **Plugin sandboxing**: Security isolation
- **Plugin dependencies**: Declare required libraries
- **Plugin hooks**: Event system for plugins to interact
