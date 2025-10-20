# Plugin Architecture Implementation Guide

> **Status**: IMPLEMENTED - Basic plugin architecture is now functional
> **Date**: 2024
> **Version**: 1.0

## Overview

The plugin architecture has been implemented to allow multiple package management backends (APT, Flatpak, AppImage, etc.) to coexist in Apt-Ex Package Manager. This document describes the implementation and how to use it.

## What's Implemented

### Core Components

1. **BasePackageController** (`src/controllers/base_controller.py`)
   - Abstract base class defining the plugin interface
   - All backend plugins must inherit from this class
   - Defines required and optional methods

2. **Plugin Directory** (`src/controllers/plugins/`)
   - Contains all backend plugin implementations
   - Plugins are auto-discovered at runtime
   - Naming convention: `{backend}_plugin.py`

3. **APTPlugin** (`src/controllers/plugins/apt_plugin.py`)
   - Converted from the original APTController
   - Fully functional APT backend implementation
   - Demonstrates complete plugin implementation

4. **FlatpakPlugin** (`src/controllers/plugins/flatpak_plugin.py`)
   - Stub implementation for Flatpak support
   - Shows plugin structure for future development
   - Only loads if Flatpak is installed on system

5. **PackageManager** (refactored `src/controllers/package_manager.py`)
   - Plugin registry and coordinator
   - Auto-discovers and registers plugins
   - Routes operations to appropriate backends
   - Maintains backward compatibility

## Architecture

### Plugin Discovery Flow

```
Application Start
    ↓
PackageManager.__init__()
    ↓
_discover_plugins()
    ↓
Scan plugin directories:
  - ~/.config/apt-ex-package-manager/plugins/
  - /usr/share/apt-ex-package-manager/plugins/
  - src/controllers/plugins/
    ↓
For each *_plugin.py file:
  - Import module
  - Find BasePackageController subclass
  - Instantiate plugin
  - Check is_available()
  - Register if available
    ↓
Plugins ready for use
```

### Operation Routing

```
View calls PackageManager.search_packages(query, backend='apt')
    ↓
PackageManager.get_backend('apt')
    ↓
Returns APTPlugin instance
    ↓
APTPlugin.search_packages(query)
    ↓
Returns List[Package] with backend='apt'
```

## Using the Plugin System

### For Application Developers

**Search across all backends:**
```python
# Search all available backends
results = package_manager.search_packages("firefox")

# Search specific backend
results = package_manager.search_packages("firefox", backend='apt')
```

**Install from specific backend:**
```python
# Install using default backend (apt)
package_manager.install_package("firefox")

# Install using specific backend
package_manager.install_package("org.mozilla.Firefox", backend='flatpak')
```

**Check available backends:**
```python
backends = package_manager.get_available_backends()
# Returns: ['apt', 'flatpak'] (if both are available)
```

**Get backend capabilities:**
```python
backend = package_manager.get_backend('apt')
capabilities = backend.get_capabilities()
# Returns: {'search', 'install', 'remove', 'list_installed', 'list_updates', 'categories'}
```

### For Plugin Developers

**Creating a new plugin:**

1. Create file: `src/controllers/plugins/mybackend_plugin.py`

2. Implement the interface:

```python
from controllers.base_controller import BasePackageController
from models.package_model import Package
from typing import List, Set
import shutil

class MyBackendPlugin(BasePackageController):
    def __init__(self, lmdb_manager=None, logging_service=None):
        self.lmdb_manager = lmdb_manager
        self.logger = logging_service.get_logger('mybackend') if logging_service else None
    
    @property
    def backend_id(self) -> str:
        return 'mybackend'
    
    @property
    def display_name(self) -> str:
        return 'My Backend Packages'
    
    def is_available(self) -> bool:
        # Check if backend command is available
        return shutil.which('mybackend') is not None
    
    def get_capabilities(self) -> Set[str]:
        return {'search', 'install', 'remove', 'list_installed'}
    
    def search_packages(self, query: str) -> List[Package]:
        # Implement search logic
        results = []
        # ... your implementation ...
        return results
    
    def install_package(self, package_id: str) -> bool:
        # Implement install logic
        return True
    
    def remove_package(self, package_id: str) -> bool:
        # Implement remove logic
        return True
    
    def get_installed_packages(self, limit: int = None, offset: int = 0) -> List[Package]:
        # Implement list logic
        return []
```

3. Plugin is automatically discovered on next application start

**Important Notes:**
- Plugin filename MUST end with `_plugin.py`
- Class name should be `{Backend}Plugin` (e.g., `APTPlugin`, `FlatpakPlugin`)
- Must inherit from `BasePackageController`
- Must implement all abstract methods
- `is_available()` determines if plugin is registered
- Return `Package` objects with `backend` parameter set

## Backward Compatibility

The implementation maintains full backward compatibility:

1. **Old APTController still exists** - Views using `package_manager.apt_controller` continue to work
2. **Fallback behavior** - If no plugins are loaded, operations fall back to old controller
3. **Gradual migration** - Views can be updated to use new API incrementally

## Migration Path for Views

**Before (direct controller access):**
```python
results = self.package_manager.apt_controller.search_packages(query)
```

**After (unified API):**
```python
# Search default backend
results = self.package_manager.search_packages(query)

# Search specific backend
results = self.package_manager.search_packages(query, backend='apt')

# Search all backends
results = self.package_manager.search_packages(query)
```

## Testing the Implementation

**Test plugin discovery:**
```python
from controllers.package_manager import PackageManager
from cache import LMDBManager

lmdb = LMDBManager()
pm = PackageManager(lmdb)

# Check registered backends
print(pm.get_available_backends())
# Output: ['apt'] or ['apt', 'flatpak'] depending on system
```

**Test backend routing:**
```python
# Get specific backend
apt = pm.get_backend('apt')
print(apt.display_name)  # "APT Packages"
print(apt.get_capabilities())  # {'search', 'install', ...}

# Search using backend
results = apt.search_packages("firefox")
for pkg in results:
    print(f"{pkg.name} ({pkg.backend})")
```

## Next Steps

### Phase 1: Complete (✓)
- [x] Create BasePackageController interface
- [x] Create plugins directory structure
- [x] Convert APTController to APTPlugin
- [x] Add plugin discovery to PackageManager
- [x] Implement backend routing
- [x] Create stub Flatpak plugin

### Phase 2: View Integration (TODO)
- [ ] Update main_view.py to use unified API
- [ ] Add backend selection UI
- [ ] Show backend badges on packages
- [ ] Handle backend-specific capabilities

### Phase 3: Complete Flatpak Plugin (TODO)
- [ ] Implement Flatpak search
- [ ] Implement Flatpak install/remove
- [ ] Implement Flatpak list installed
- [ ] Add Flatpak repository management

### Phase 4: Additional Backends (TODO)
- [ ] Create AppImage plugin
- [ ] Create Snap plugin (optional)
- [ ] Test multi-backend operations

## Benefits Achieved

1. **Extensibility** - New backends can be added without modifying core code
2. **Modularity** - Each backend is isolated in its own module
3. **Flexibility** - Backends can be enabled/disabled based on system availability
4. **Maintainability** - Easier to maintain and test individual backends
5. **Future-proof** - Architecture supports community plugins

## Known Limitations

1. **No hot reload** - Plugins are discovered at startup only
2. **No plugin metadata** - No version, author, or dependency information
3. **No plugin configuration UI** - Settings integration not yet implemented
4. **No plugin marketplace** - No discovery/installation of third-party plugins

## Plugin-Specific Documentation

For detailed documentation on individual plugins:
- [Plugin Documentation Directory](../plugins/) - Per-plugin documentation
- [APT Plugin](../plugins/apt/) - APT-specific features and implementation
- [Flatpak Plugin](../plugins/flatpak/) - Flatpak-specific features (planned)
- [AppImage Plugin](../plugins/appimage/) - AppImage-specific features (planned)

## References

- [Plugin Architecture Design](PLUGIN_ARCHITECTURE.md) - Original design specification
- [Base Controller API](../api/BASE_CONTROLLER.md) - Complete API reference (TODO)
- [Plugin Development Guide](../developer/PLUGIN_DEVELOPMENT.md) - Detailed guide (TODO)
