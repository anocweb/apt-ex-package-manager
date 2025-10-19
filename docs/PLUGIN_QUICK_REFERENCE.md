# Plugin Architecture Quick Reference

## For Application Developers

### Basic Operations

```python
# Search all backends
results = package_manager.search_packages("firefox")

# Search specific backend
results = package_manager.search_packages("firefox", backend='apt')

# Install package
package_manager.install_package("firefox", backend='apt')

# Remove package
package_manager.remove_package("firefox", backend='apt')

# List installed
packages = package_manager.get_installed_packages()
packages = package_manager.get_installed_packages(backend='apt')
```

### Backend Management

```python
# Get available backends
backends = package_manager.get_available_backends()
# Returns: ['apt', 'flatpak', ...]

# Get specific backend
backend = package_manager.get_backend('apt')

# Check capabilities
caps = backend.get_capabilities()
# Returns: {'search', 'install', 'remove', ...}

# Backend info
print(backend.backend_id)      # 'apt'
print(backend.display_name)    # 'APT Packages'
print(backend.is_available())  # True/False
```

### Capability Checking

```python
backend = package_manager.get_backend('flatpak')
if backend and 'categories' in backend.get_capabilities():
    categories = backend.get_categories()
```

## For Plugin Developers

### Minimal Plugin Template

```python
from controllers.base_controller import BasePackageController
from models.package_model import Package
from typing import List, Set
import shutil

class MyPlugin(BasePackageController):
    def __init__(self, lmdb_manager=None, logging_service=None):
        self.lmdb_manager = lmdb_manager
        self.logger = logging_service.get_logger('my') if logging_service else None
    
    @property
    def backend_id(self) -> str:
        return 'my'
    
    @property
    def display_name(self) -> str:
        return 'My Packages'
    
    def is_available(self) -> bool:
        return shutil.which('my-command') is not None
    
    def get_capabilities(self) -> Set[str]:
        return {'search', 'install', 'remove', 'list_installed'}
    
    def search_packages(self, query: str) -> List[Package]:
        # Implement search
        return []
    
    def install_package(self, package_id: str) -> bool:
        # Implement install
        return True
    
    def remove_package(self, package_id: str) -> bool:
        # Implement remove
        return True
    
    def get_installed_packages(self, limit: int = None, offset: int = 0) -> List[Package]:
        # Implement list
        return []
```

### Standard Capabilities

- `search` - Search packages
- `install` - Install packages
- `remove` - Remove packages
- `update` - Update packages
- `list_installed` - List installed
- `list_updates` - List updates
- `categories` - Category browsing
- `ratings` - Ratings support
- `repositories` - Repository management
- `dependencies` - Dependency info
- `permissions` - Permission management

### Category Mapping

```python
def get_sidebar_category_mapping(self) -> Dict[str, List[str]]:
    return {
        'games': ['games', 'game'],
        'graphics': ['graphics', 'design'],
        'internet': ['network', 'web', 'mail'],
        'multimedia': ['audio', 'video'],
        'office': ['office', 'productivity'],
        'development': ['devel', 'programming'],
        'system': ['system', 'admin'],
        'utilities': ['utility', 'tools'],
        'education': ['education'],
        'science': ['science'],
        'accessibility': ['accessibility'],
    }
```

## File Locations

### Plugin Files
- Development: `src/controllers/plugins/mybackend_plugin.py`
- System: `/usr/share/apt-ex-package-manager/plugins/`
- User: `~/.config/apt-ex-package-manager/plugins/`

### Core Files
- Base interface: `src/controllers/base_controller.py`
- Package manager: `src/controllers/package_manager.py`
- Package model: `src/models/package_model.py`

## Testing

```bash
# Run plugin tests
python test_plugins.py

# Test in Python
from controllers.package_manager import PackageManager
from cache import LMDBManager

pm = PackageManager(LMDBManager())
print(pm.get_available_backends())
```

## Common Patterns

### Multi-Backend Search
```python
def search_all(query):
    results = {}
    for backend_id in package_manager.get_available_backends():
        backend = package_manager.get_backend(backend_id)
        results[backend_id] = backend.search_packages(query)
    return results
```

### Capability-Based UI
```python
def setup_ui():
    for backend_id in package_manager.get_available_backends():
        backend = package_manager.get_backend(backend_id)
        if 'categories' in backend.get_capabilities():
            show_category_browser()
```

### Backend-Specific Install
```python
def install(package):
    # Use package's backend
    success = package_manager.install_package(
        package.name,
        backend=package.backend
    )
```

## Migration Checklist

- [ ] Replace `apt_controller` with `package_manager`
- [ ] Add `backend` parameter to operations
- [ ] Show backend badges on packages
- [ ] Check capabilities before showing features
- [ ] Test with multiple backends

## Documentation

- **Full Guide**: [docs/architecture/PLUGIN_IMPLEMENTATION.md](../architecture/PLUGIN_IMPLEMENTATION.md)
- **Migration**: [docs/developer/PLUGIN_MIGRATION_GUIDE.md](../developer/PLUGIN_MIGRATION_GUIDE.md)
- **Design**: [docs/architecture/PLUGIN_ARCHITECTURE.md](../architecture/PLUGIN_ARCHITECTURE.md)

## Quick Links

- Plugin directory: `src/controllers/plugins/`
- Base controller: `src/controllers/base_controller.py`
- Test script: `test_plugins.py`
- Status: `docs/STATUS.md`
