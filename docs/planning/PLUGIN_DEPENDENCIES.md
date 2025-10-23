# Plugin Dependencies Implementation Plan

## Overview
Add version-aware dependency management for plugins with a dedicated Plugins panel in the UI.

## Goals
- Plugins declare system and Python dependencies with version requirements
- Automatic dependency checking during plugin discovery
- Dedicated UI panel showing plugin status and dependencies
- Clear installation instructions for missing dependencies

## Dependency Types

### System Dependencies
External binaries/packages with version constraints:
```python
{
    'name': 'Flatpak',
    'command': 'flatpak',
    'package': 'flatpak',
    'min_version': '1.12.0',
    'max_version': None,
    'version_command': ['flatpak', '--version']
}
```

### Python Dependencies
Python packages with pip-style version specs:
```python
['PyGObject>=3.40.0', 'requests>=2.25.0,<3.0.0']
```

## Architecture Changes

### 1. BasePackageController Interface
Add methods:
- `get_system_dependencies() -> List[Dict[str, Any]]`
- `get_python_dependencies() -> List[str]`
- `check_dependencies() -> Dict[str, Any]`

### 2. New Utilities
- `src/utils/version_checker.py` - Version parsing and comparison
- `src/utils/dependency_checker.py` - Dependency validation

### 3. PackageManager Enhancement
- Track detailed plugin status including dependency info
- `get_plugin_status() -> Dict[str, Dict]`
- `refresh_plugin_status()`

### 4. UI Components
- Add Plugins button to sidebar (below Settings)
- New Plugins panel showing:
  - All discovered plugins (available + unavailable)
  - Per-plugin status cards
  - Dependency details with versions
  - Installation instructions

## Plugin Status Data Structure
```python
{
    'apt': {
        'available': True,
        'plugin': <APTPlugin instance>,
        'backend_id': 'apt',
        'display_name': 'APT Packages',
        'capabilities': {'search', 'install', ...},
        'dependencies': {
            'system': [
                {
                    'name': 'APT',
                    'command': 'apt-get',
                    'required_version': '>=2.0.0',
                    'installed_version': '2.4.5',
                    'satisfied': True
                }
            ],
            'python': [
                {
                    'package': 'apt',
                    'required_version': None,
                    'installed_version': '2.3.0',
                    'satisfied': True
                }
            ]
        },
        'missing_dependencies': []
    }
}
```

## Implementation Steps

1. ✅ Create version_checker.py utility
2. ✅ Create dependency_checker.py utility
3. ✅ Update BasePackageController with dependency methods
4. ✅ Implement in APTPlugin
5. ✅ Update PackageManager plugin tracking
6. ✅ Create plugins_panel.ui in Qt Designer
7. ✅ Create plugins_panel.py controller
8. ✅ Update main_window.ui - add plugins button
9. ✅ Update main_view.py - wire up panel
10. ✅ Test with APT plugin
11. ✅ Document in plugin development guide

## User Experience

### Graceful Degradation
- Plugins with missing dependencies don't crash the app
- Listed as "unavailable" with clear reasons
- Actionable installation instructions provided

### Plugin Panel Features
- Visual status indicators (✓ Available / ✗ Unavailable)
- Expandable dependency sections
- Copy-to-clipboard for install commands
- Refresh button to re-check after installing dependencies

## Testing Scenarios
1. All dependencies satisfied (APT on Ubuntu)
2. Missing system dependency (Flatpak not installed)
3. Missing Python dependency (module not importable)
4. Wrong version installed (too old/too new)
5. Multiple plugins with mixed availability
