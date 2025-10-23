# Plugin Development Rules

## Plugin Architecture Standards

### Plugin Location
- Built-in plugins: `src/controllers/plugins/`
- Plugin files named: `{backend}_plugin.py`
- Class named: `{Backend}Plugin` (e.g., `APTPlugin`, `FlatpakPlugin`)

### Plugin Interface Requirements
- All plugins MUST inherit from `BasePackageController`
- All plugins MUST implement required abstract methods
- All plugins MUST declare capabilities via `get_capabilities()`
- All plugins MUST check availability via `is_available()`
- All plugins MUST map categories to standard sidebar categories
- All plugins MUST declare dependencies via `get_system_dependencies()` and `get_python_dependencies()`
- All plugins SHOULD provide settings schema for backend-specific options

### Required Methods
```python
@property backend_id() -> str          # Unique identifier
@property display_name() -> str        # UI display name
@property version() -> str             # Plugin version (default: "1.0.0")
is_available() -> bool                 # System availability check
get_capabilities() -> Set[str]         # Supported operations
search_packages(query) -> List[Package]
install_package(package_id) -> bool
remove_package(package_id) -> bool
get_installed_packages(limit, offset) -> List[Package]
get_sidebar_category_mapping() -> Dict[str, List[str]]  # Category mapping
get_system_dependencies() -> List[Dict]  # System dependencies with versions
get_python_dependencies() -> List[str]   # Python packages with version specs
```

### Optional Methods (with defaults)
```python
get_upgradable_packages() -> List[Dict]
update_package(package_id) -> bool
get_categories() -> List[str]
get_packages_by_category(category) -> List[Package]
get_all_packages_for_cache() -> List[Dict]
update_installed_status(connection_manager) -> bool
map_to_sidebar_category(backend_category) -> Optional[str]
get_settings_schema() -> Dict
get_settings_widget(parent) -> QWidget
on_settings_changed(setting_key, value) -> None
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

### Standard Sidebar Categories
All plugins must map their categories to these:
- `games` - Gaming applications
- `graphics` - Image editing, design
- `internet` - Web, email, networking
- `multimedia` - Audio/video
- `office` - Productivity, documents
- `development` - IDEs, dev tools
- `system` - System utilities
- `utilities` - General tools
- `education` - Educational software
- `science` - Scientific applications
- `accessibility` - Accessibility tools
- `all` - All packages

### Plugin Registration
- Plugins auto-discovered from `plugins/` directory
- PackageManager checks dependencies during registration
- Only plugins with satisfied dependencies are registered
- Plugin status tracked in `PackageManager.plugin_status`
- View plugin status in Plugins panel (🔌 Plugins in sidebar)

### Backend-Specific Metadata
- Use `Package.metadata` dict for backend-specific data
- Keep metadata serializable (JSON-compatible)
- Document metadata fields in plugin docstring

### Error Handling
- Plugins should handle errors gracefully
- Return empty lists/False on errors, don't raise
- Log errors using provided logging_service
- Use timeouts for subprocess calls

### Testing Requirements
- Each plugin must have unit tests
- Test availability detection
- Test all capability methods
- Mock external dependencies
- Test error conditions

## PackageManager Integration

### Backend Routing
- PackageManager routes operations to appropriate backend
- Support backend parameter: `method(args, backend='apt')`
- Support multi-backend operations (search all, etc.)
- Default backend configurable by user

### View Integration
- Views MUST NOT access backends directly
- Views use PackageManager unified API only
- Views check capabilities before showing UI
- Views display backend badges on packages

## Migration from Monolithic to Plugin

### Phase 1: Interface
1. Create `BasePackageController` abstract class
2. Define all required/optional methods
3. Add capability constants

### Phase 2: Convert Existing
1. Move `apt_controller.py` to `plugins/apt_plugin.py`
2. Rename class to `APTPlugin`
3. Inherit from `BasePackageController`
4. Implement all required methods

### Phase 3: Registry
1. Add `backends` dict to PackageManager
2. Implement `register_backend()` method
3. Implement `_discover_plugins()` method
4. Update all operation methods to route

### Phase 4: Views
1. Remove direct `apt_controller` access
2. Use unified PackageManager methods
3. Add backend selection UI
4. Handle capability differences

## Dependency Declaration

### System Dependencies
Declare system binaries/packages with version constraints:
```python
def get_system_dependencies(self) -> List[Dict]:
    return [
        {
            'name': 'Flatpak',
            'command': 'flatpak',
            'package': 'flatpak',
            'min_version': '1.12.0',
            'version_command': ['flatpak', '--version']
        }
    ]
```

### Python Dependencies
Declare Python packages with pip-style version specs:
```python
def get_python_dependencies(self) -> List[str]:
    return ['PyGObject>=3.40.0', 'requests>=2.25.0,<3.0.0']
```

### Version Constraints
Supported operators: `>=`, `>`, `<=`, `<`, `==`, `!=`

## Documentation Requirements
- Document plugin capabilities in docstring
- Document metadata fields used
- Document system requirements and dependencies
- Document category mapping logic
- Document available settings and their effects
- Provide usage examples
- Include testing instructions

## Reference Documentation
- See `docs/PLUGIN_ARCHITECTURE.md` for complete architecture
- See `docs/PLUGIN_EXAMPLE.md` for implementation example
- See `docs/DATA_STRUCTURES.md` for required data structures and contracts
