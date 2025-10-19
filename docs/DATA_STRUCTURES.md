# Data Structures and Contracts

## Overview

This document defines the required data structures that all backend plugins must use when returning data to the application. These structures ensure consistent UI rendering and type safety across all backends.

## Core Data Models

### Package

The primary data structure representing a software package.

```python
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any

@dataclass
class Package:
    """Unified package representation for all backends"""
    
    # === Required Fields ===
    package_id: str          # Unique identifier (e.g., 'firefox', 'org.mozilla.Firefox')
    name: str                # Display name (e.g., 'Firefox')
    version: str             # Version string (e.g., '121.0')
    backend: str             # Backend identifier ('apt', 'flatpak', 'snap', 'appimage')
    
    # === Optional Fields ===
    summary: Optional[str] = None           # Short description (1 line)
    description: Optional[str] = None       # Full description (multiple paragraphs)
    icon_url: Optional[str] = None          # URL or path to icon
    homepage: Optional[str] = None          # Project homepage URL
    license: Optional[str] = None           # License identifier (e.g., 'GPL-3.0')
    
    # Size information (in bytes)
    size: Optional[int] = None              # Download size
    installed_size: Optional[int] = None    # Installed size on disk
    
    # === Status Flags ===
    is_installed: bool = False              # Whether package is installed
    is_upgradable: bool = False             # Whether update is available
    
    # === Categorization ===
    category: Optional[str] = None          # Sidebar category (see Category Mapping)
    
    # === Ratings ===
    rating: Optional[float] = None          # Average rating (0.0 - 5.0)
    review_count: Optional[int] = None      # Number of reviews
    
    # === Backend-Specific Data ===
    metadata: Dict = field(default_factory=dict)  # Backend-specific fields (see below)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for storage/serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Package':
        """Create from dict (for deserialization)"""
        return cls(**data)
```

**Field Requirements:**
- `package_id`: MUST be unique within backend, used for install/remove operations
- `name`: MUST be human-readable display name
- `version`: MUST be valid version string
- `backend`: MUST match plugin's `backend_id`
- `category`: SHOULD be one of the standard sidebar categories
- `rating`: IF provided, MUST be between 0.0 and 5.0
- `metadata`: MUST be JSON-serializable dict

**Example - APT Package:**
```python
Package(
    package_id='firefox',
    name='Firefox',
    version='121.0-1ubuntu1',
    backend='apt',
    summary='Safe and easy web browser from Mozilla',
    description='Firefox is a powerful, extensible web browser...',
    category='internet',
    size=58000000,
    installed_size=220000000,
    is_installed=True,
    metadata={
        'section': 'web',
        'priority': 'optional',
        'maintainer': 'Ubuntu Developers',
        'architecture': 'amd64'
    }
)
```

**Example - Flatpak Package:**
```python
Package(
    package_id='org.mozilla.Firefox',
    name='Firefox',
    version='121.0',
    backend='flatpak',
    summary='Fast, Private & Safe Web Browser',
    icon_url='https://dl.flathub.org/repo/appstream/x86_64/icons/128x128/org.mozilla.firefox.png',
    category='internet',
    rating=4.5,
    review_count=1234,
    metadata={
        'remote': 'flathub',
        'ref': 'app/org.mozilla.Firefox/x86_64/stable',
        'branch': 'stable',
        'permissions': ['network', 'x11', 'pulseaudio']
    }
)
```

### PackageSummary

Lightweight package summary for list views (optimized for memory).

```python
@dataclass
class PackageSummary:
    """Lightweight package summary for list views"""
    
    # === Required Fields ===
    package_id: str
    name: str
    version: str
    backend: str
    
    # === Optional Fields ===
    summary: Optional[str] = None
    category: Optional[str] = None
    size: Optional[int] = None
    installed_size: Optional[int] = None
    is_installed: bool = False
    icon_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for storage/serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageSummary':
        """Create from dict (for deserialization)"""
        return cls(**data)
    
    @classmethod
    def from_package(cls, pkg: Package) -> 'PackageSummary':
        """Create summary from full package"""
        return cls(
            package_id=pkg.package_id,
            name=pkg.name,
            version=pkg.version,
            backend=pkg.backend,
            summary=pkg.summary,
            category=pkg.category,
            size=pkg.size,
            installed_size=pkg.installed_size,
            is_installed=pkg.is_installed,
            icon_url=pkg.icon_url
        )
```

**Usage:**
- Use `PackageSummary` for list views (Home, Installed, Category)
- Use full `Package` for detail views
- Store both in LMDB with split keys (`:summary` and `:full`)

### PackageUpdate

Represents an available package update.

```python
@dataclass
class PackageUpdate:
    """Package update information for Updates view"""
    
    # === Required Fields ===
    package_id: str          # Package identifier
    name: str                # Display name
    current_version: str     # Currently installed version
    new_version: str         # Available version
    backend: str             # Backend identifier
    
    # === Optional Fields ===
    description: Optional[str] = None       # Update description
    is_security: bool = False               # Security update flag
    size: Optional[int] = None              # Download size in bytes
    changelog: Optional[str] = None         # Changelog/release notes
    release_date: Optional[str] = None      # Release date (ISO format)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for storage/serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageUpdate':
        """Create from dict (for deserialization)"""
        return cls(**data)
```

**Example:**
```python
PackageUpdate(
    package_id='firefox',
    name='Firefox',
    current_version='120.0',
    new_version='121.0',
    backend='apt',
    description='Security and stability update',
    is_security=True,
    size=58000000,
    changelog='- Fixed CVE-2024-1234\n- Improved performance'
)
```

### Repository

Represents a package repository or remote source.

```python
@dataclass
class Repository:
    """Repository/remote source for Settings view"""
    
    # === Required Fields ===
    id: str                  # Unique identifier
    name: str                # Display name
    url: str                 # Repository URL
    backend: str             # Backend identifier
    
    # === Optional Fields ===
    enabled: bool = True                    # Whether repository is active
    scope: str = 'system'                   # 'system' or 'user'
    description: Optional[str] = None       # Repository description
    metadata: Dict = field(default_factory=dict)  # Backend-specific data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for storage/serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Repository':
        """Create from dict (for deserialization)"""
        return cls(**data)
```

**Example - APT Repository:**
```python
Repository(
    id='ubuntu-main',
    name='Ubuntu Main Repository',
    url='http://archive.ubuntu.com/ubuntu',
    backend='apt',
    enabled=True,
    scope='system',
    metadata={
        'components': ['main', 'restricted', 'universe', 'multiverse'],
        'distribution': 'jammy'
    }
)
```

**Example - Flatpak Remote:**
```python
Repository(
    id='flathub',
    name='Flathub',
    url='https://dl.flathub.org/repo/',
    backend='flatpak',
    enabled=True,
    scope='user',
    description='Central repository of Flatpak applications',
    metadata={
        'gpg_key': 'https://dl.flathub.org/repo/flathub.gpg',
        'priority': 1
    }
)
```

### CategoryInfo

Represents a package category with count information.

```python
@dataclass
class CategoryInfo:
    """Category information with package count"""
    
    # === Required Fields ===
    id: str                  # Sidebar category ID
    name: str                # Display name
    icon: str                # Icon emoji or identifier
    package_count: int       # Number of packages in category
    backend: str             # Backend identifier
```

**Example:**
```python
CategoryInfo(
    id='games',
    name='Games',
    icon='🎮',
    package_count=342,
    backend='apt'
)
```

## Plugin Method Return Types

### Required Methods

```python
def search_packages(self, query: str) -> List[Package]:
    """
    Search for packages matching query.
    
    Returns:
        List of Package objects with ALL required fields populated.
        Empty list if no results.
    """
    pass

def install_package(self, package_id: str) -> bool:
    """
    Install a package.
    
    Args:
        package_id: The package_id from Package object
    
    Returns:
        True if successful, False otherwise
    """
    pass

def remove_package(self, package_id: str) -> bool:
    """
    Remove a package.
    
    Args:
        package_id: The package_id from Package object
    
    Returns:
        True if successful, False otherwise
    """
    pass

def get_installed_packages(self, limit: int = None, offset: int = 0) -> List[Package]:
    """
    Get list of installed packages.
    
    Returns:
        List of Package objects with is_installed=True.
        MUST support pagination via limit/offset.
    """
    pass
```

### Optional Methods

```python
def get_upgradable_packages(self) -> List[PackageUpdate]:
    """
    Get packages with available updates.
    
    Returns:
        List of PackageUpdate objects.
        Empty list if no updates or not supported.
    """
    return []

def update_package(self, package_id: str) -> bool:
    """
    Update a single package.
    
    Returns:
        True if successful, False otherwise
    """
    return False

def get_packages_by_category(self, category: str) -> List[Package]:
    """
    Get packages in a sidebar category.
    
    Args:
        category: One of the standard sidebar categories
    
    Returns:
        List of Package objects in that category
    """
    return []

def get_repositories(self) -> List[Repository]:
    """
    Get list of repositories/remotes.
    
    Returns:
        List of Repository objects.
        Empty list if not supported.
    """
    return []
```

## Standard Sidebar Categories

All plugins MUST map their backend categories to these standard categories:

| Category ID | Display Name | Icon | Description |
|-------------|--------------|------|-------------|
| `games` | Games | 🎮 | Gaming applications |
| `graphics` | Graphics | 🎨 | Image editing, design tools |
| `internet` | Internet | 🌐 | Web browsers, email, networking |
| `multimedia` | Multimedia | 🎵 | Audio/video players, editors |
| `office` | Office | 📄 | Productivity, documents |
| `development` | Development | 🔧 | IDEs, compilers, dev tools |
| `system` | System | ⚙️ | System utilities, admin tools |
| `utilities` | Utilities | 🔨 | General utilities, tools |
| `education` | Education | 🎓 | Educational software |
| `science` | Science & Math | 🧪 | Scientific, math applications |
| `accessibility` | Accessibility | ♿ | Accessibility tools |
| `all` | All Applications | 📱 | All packages (special) |

## Category Mapping

Plugins MUST implement `get_sidebar_category_mapping()` to map backend-specific categories to standard sidebar categories.

### Method Signature

```python
def get_sidebar_category_mapping(self) -> Dict[str, List[str]]:
    """
    Map sidebar categories to backend-specific categories.
    
    Returns:
        Dict mapping sidebar category IDs to list of backend category names.
        Each sidebar category can map to multiple backend categories.
    
    Example for APT:
        {
            'games': ['games', 'games/action', 'games/strategy'],
            'internet': ['web', 'mail', 'net'],
            'development': ['devel', 'libdevel', 'vcs']
        }
    """
    pass
```

### Backend Category Examples

**APT Sections → Sidebar Categories:**
```python
{
    'games': ['games'],
    'graphics': ['graphics'],
    'internet': ['web', 'mail', 'net', 'comm'],
    'multimedia': ['sound', 'video'],
    'office': ['editors', 'text', 'doc'],
    'development': ['devel', 'libdevel', 'vcs', 'debug'],
    'system': ['admin', 'base', 'utils'],
    'utilities': ['utils', 'misc'],
    'education': ['education'],
    'science': ['science', 'math'],
    'accessibility': ['accessibility']
}
```

**Flatpak Categories → Sidebar Categories:**
```python
{
    'games': ['Game'],
    'graphics': ['Graphics'],
    'internet': ['Network', 'WebBrowser', 'Email'],
    'multimedia': ['Audio', 'Video', 'AudioVideo'],
    'office': ['Office'],
    'development': ['Development', 'IDE'],
    'system': ['System'],
    'utilities': ['Utility'],
    'education': ['Education'],
    'science': ['Science'],
    'accessibility': ['Accessibility']
}
```

**Snap Categories → Sidebar Categories:**
```python
{
    'games': ['games'],
    'graphics': ['art-and-design'],
    'internet': ['social', 'news-and-weather'],
    'multimedia': ['music-and-audio', 'photo-and-video'],
    'office': ['productivity'],
    'development': ['development'],
    'system': ['server-and-cloud', 'devices-and-iot'],
    'utilities': ['utilities'],
    'education': ['education'],
    'science': ['science'],
    'accessibility': ['accessibility']
}
```

### Helper Method

Plugins can implement a helper to map individual packages:

```python
def map_to_sidebar_category(self, backend_category: str) -> Optional[str]:
    """
    Map a backend category to sidebar category.
    
    Args:
        backend_category: Backend-specific category name
    
    Returns:
        Sidebar category ID or None if no mapping
    """
    mapping = self.get_sidebar_category_mapping()
    for sidebar_cat, backend_cats in mapping.items():
        if backend_category in backend_cats:
            return sidebar_cat
    return None
```

## Backend-Specific Metadata

The `metadata` field in Package and Repository objects is for backend-specific data that doesn't fit standard fields.

### APT Metadata Example
```python
metadata = {
    'section': 'web',              # APT section
    'priority': 'optional',        # Package priority
    'architecture': 'amd64',       # Architecture
    'maintainer': 'Ubuntu Developers',
    'depends': 'libc6, libx11-6',  # Dependencies
    'conflicts': 'firefox-esr',    # Conflicts
    'source': 'firefox (121.0)'    # Source package
}
```

### Flatpak Metadata Example
```python
metadata = {
    'remote': 'flathub',           # Remote name
    'ref': 'app/org.mozilla.Firefox/x86_64/stable',
    'branch': 'stable',            # Branch
    'commit': 'abc123...',         # Commit hash
    'runtime': 'org.freedesktop.Platform/x86_64/23.08',
    'permissions': [               # Flatpak permissions
        'network',
        'x11',
        'pulseaudio',
        'dri'
    ]
}
```

### Snap Metadata Example
```python
metadata = {
    'publisher': 'mozilla✓',       # Publisher with verification
    'channel': 'stable',           # Channel
    'revision': '1234',            # Revision number
    'confinement': 'strict',       # Confinement type
    'grade': 'stable',             # Grade
    'tracking': 'latest/stable'    # Tracking channel
}
```

### AppImage Metadata Example
```python
metadata = {
    'filename': 'Firefox-121.0.AppImage',
    'download_url': 'https://...',
    'sha256': 'abc123...',
    'github_repo': 'mozilla/firefox',
    'release_tag': 'v121.0',
    'executable': True
}
```

## Plugin Settings

Plugins can provide settings that appear in the Settings view.

### Settings Schema

Define plugin settings using `get_settings_schema()`:

```python
def get_settings_schema(self) -> Dict[str, Any]:
    """
    Define plugin settings schema.
    
    Returns:
        Dict with setting definitions. Each setting has:
        - type: Setting type (string, boolean, choice, integer, password)
        - label: Display label
        - default: Default value
        - description: Help text
        - required: Whether setting is required (optional)
        - choices: List of choices for 'choice' type (optional)
    """
    return {
        'repository_url': {
            'type': 'string',
            'label': 'Repository URL',
            'default': 'https://dl.flathub.org/repo/',
            'description': 'Flatpak repository URL',
            'required': True
        },
        'branch': {
            'type': 'choice',
            'label': 'Default Branch',
            'choices': ['stable', 'beta', 'dev'],
            'default': 'stable',
            'description': 'Default branch for installations'
        },
        'auto_update': {
            'type': 'boolean',
            'label': 'Auto Update',
            'default': True,
            'description': 'Automatically update packages'
        },
        'cache_ttl': {
            'type': 'integer',
            'label': 'Cache TTL (hours)',
            'default': 24,
            'description': 'How long to cache package data'
        },
        'api_token': {
            'type': 'password',
            'label': 'API Token',
            'default': '',
            'description': 'Authentication token for private repositories'
        }
    }
```

### Setting Types

| Type | Widget | Example Use Case |
|------|--------|------------------|
| `string` | QLineEdit | URLs, paths, text values |
| `boolean` | QCheckBox | Enable/disable flags |
| `choice` | QComboBox | Dropdown selections |
| `integer` | QSpinBox | Numeric values, timeouts |
| `password` | QLineEdit (masked) | Credentials, tokens |

### Custom Settings Widget (Optional)

For complex settings UI, provide a custom widget:

```python
from PyQt6.QtWidgets import QWidget

def get_settings_widget(self, parent: QWidget) -> QWidget:
    """
    Create custom settings widget.
    
    Args:
        parent: Parent widget
    
    Returns:
        QWidget with plugin settings UI
    
    Note:
        Only implement if get_settings_schema() is insufficient.
        Widget should emit signals when settings change.
    """
    widget = QWidget(parent)
    # Build custom UI with layouts, widgets, etc.
    return widget
```

### Settings Change Handler

Respond to setting changes:

```python
def on_settings_changed(self, setting_key: str, value: Any) -> None:
    """
    Called when a setting changes.
    
    Args:
        setting_key: The setting that changed
        value: New value
    
    Note:
        Use this to reload configuration, refresh caches, etc.
    """
    if setting_key == 'repository_url':
        self._reload_repository(value)
    elif setting_key == 'branch':
        self._update_default_branch(value)
    elif setting_key == 'cache_ttl':
        self._update_cache_ttl(value)
```

### Example Settings Implementations

**APT Plugin Settings:**
```python
def get_settings_schema(self) -> Dict[str, Any]:
    return {
        'use_recommends': {
            'type': 'boolean',
            'label': 'Install Recommended Packages',
            'default': True,
            'description': 'Install recommended dependencies'
        },
        'use_suggests': {
            'type': 'boolean',
            'label': 'Install Suggested Packages',
            'default': False,
            'description': 'Install suggested packages'
        },
        'auto_clean': {
            'type': 'boolean',
            'label': 'Auto Clean Cache',
            'default': True,
            'description': 'Automatically clean package cache after operations'
        }
    }
```

**Flatpak Plugin Settings:**
```python
def get_settings_schema(self) -> Dict[str, Any]:
    return {
        'default_remote': {
            'type': 'choice',
            'label': 'Default Remote',
            'choices': ['flathub', 'flathub-beta', 'fedora'],
            'default': 'flathub',
            'description': 'Default Flatpak remote'
        },
        'installation_scope': {
            'type': 'choice',
            'label': 'Installation Scope',
            'choices': ['user', 'system'],
            'default': 'user',
            'description': 'Install for current user or system-wide'
        }
    }
```

**AppImage Plugin Settings:**
```python
def get_settings_schema(self) -> Dict[str, Any]:
    return {
        'storage_path': {
            'type': 'string',
            'label': 'Storage Path',
            'default': '~/Applications',
            'description': 'Where to store AppImage files'
        },
        'auto_integrate': {
            'type': 'boolean',
            'label': 'Auto Desktop Integration',
            'default': True,
            'description': 'Automatically create desktop entries'
        },
        'check_updates': {
            'type': 'boolean',
            'label': 'Check for Updates',
            'default': True,
            'description': 'Automatically check for AppImage updates'
        }
    }
```

## Data Validation

Plugins SHOULD validate data before returning:

```python
from models.validators import validate_package, validate_package_list

def search_packages(self, query: str) -> List[Package]:
    results = self._fetch_results(query)
    
    packages = []
    for result in results:
        pkg = Package(
            package_id=result['id'],
            name=result['name'],
            version=result['version'],
            backend=self.backend_id,
            # ... other fields
        )
        packages.append(pkg)
    
    # Validate before returning
    return validate_package_list(packages)
```

## Caching Considerations

When caching Package objects in LMDB:

1. **Serialize to dict** before storing:
```python
cache_data = package.to_dict()
```

2. **Deserialize from dict** when loading:
```python
package = Package.from_dict(cache_data)
```

3. **Split-key storage** for memory efficiency:
```python
# Store lightweight summary
summary = PackageSummary.from_package(package)
lmdb_cache.add(f'{package_id}:summary', summary.to_dict())

# Store full data
lmdb_cache.add(f'{package_id}:full', package.to_dict())
```

4. **Cache key format**:
```python
summary_key = f"{package_id}:summary"
full_key = f"{package_id}:full"
```

## View Data Requirements

### Home View
- Featured packages: List[Package] (max 6)
- Recently updated: List[Package] (max 6)
- Popular packages: List[Package] (max 6)

### Installed View
- Packages: List[Package] with `is_installed=True`
- Support pagination (limit/offset)

### Updates View
- Updates: List[PackageUpdate]
- Separate security updates (`is_security=True`)

### Category View
- Packages: List[Package] with matching `category`
- Support pagination

### Settings View
- Repositories: List[Repository]
- Backend settings: Dict from `get_settings_schema()`

## Error Handling

Plugins MUST handle errors gracefully:

```python
def search_packages(self, query: str) -> List[Package]:
    try:
        results = self._search_backend(query)
        return self._convert_to_packages(results)
    except Exception as e:
        if self.logger:
            self.logger.error(f"Search failed: {e}")
        return []  # Return empty list, don't raise
```

## Testing Data Structures

Example test to verify plugin compliance:

```python
def test_search_returns_valid_packages():
    plugin = MyPlugin()
    results = plugin.search_packages('test')
    
    assert isinstance(results, list)
    for pkg in results:
        assert isinstance(pkg, Package)
        assert pkg.package_id
        assert pkg.name
        assert pkg.version
        assert pkg.backend == plugin.backend_id
        if pkg.rating is not None:
            assert 0 <= pkg.rating <= 5

def test_category_mapping():
    plugin = MyPlugin()
    mapping = plugin.get_sidebar_category_mapping()
    
    assert isinstance(mapping, dict)
    # All keys must be standard sidebar categories
    valid_categories = {'games', 'graphics', 'internet', 'multimedia', 
                       'office', 'development', 'system', 'utilities',
                       'education', 'science', 'accessibility', 'all'}
    for category in mapping.keys():
        assert category in valid_categories

def test_serialization():
    pkg = Package(
        package_id='test',
        name='Test Package',
        version='1.0',
        backend='test'
    )
    
    # Test to_dict
    data = pkg.to_dict()
    assert isinstance(data, dict)
    assert data['package_id'] == 'test'
    
    # Test from_dict
    pkg2 = Package.from_dict(data)
    assert pkg2.package_id == pkg.package_id
    assert pkg2.name == pkg.name
```

## Summary

**Plugins MUST:**
- Return List[Package] for package queries
- Return List[PackageUpdate] for update queries
- Return List[Repository] for repository queries
- Populate ALL required fields
- Implement `get_sidebar_category_mapping()` to map categories
- Use standard sidebar categories in Package.category field
- Handle errors gracefully (return empty lists)
- Use `field(default_factory=dict)` for mutable defaults

**Plugins SHOULD:**
- Validate data before returning
- Populate optional fields when available
- Use metadata dict for backend-specific data
- Cache expensive operations
- Implement `get_settings_schema()` for configurable options
- Use PackageSummary for list views (memory efficiency)
- Implement serialization methods (to_dict/from_dict)

**Plugins MUST NOT:**
- Return None instead of empty list
- Raise exceptions for normal failures
- Use non-standard category IDs
- Return invalid rating values (outside 0-5)
- Use mutable defaults without field(default_factory)
