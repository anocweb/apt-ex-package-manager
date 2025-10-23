# Plugin Dependencies Feature

## Overview
The plugin dependency system allows plugins to declare their system and Python dependencies with version requirements. The system automatically checks dependencies during plugin discovery and provides a dedicated UI panel for viewing plugin status.

## Features

### Dependency Declaration
Plugins declare dependencies in two categories:

**System Dependencies:**
- External binaries/packages (e.g., `apt-get`, `flatpak`)
- Version constraints (minimum/maximum versions)
- Version detection commands

**Python Dependencies:**
- Python packages with pip-style version specs
- Supports operators: `>=`, `>`, `<=`, `<`, `==`, `!=`

### Automatic Dependency Checking
- Dependencies checked during plugin discovery
- Version validation against constraints
- Detailed status tracking per plugin
- Missing dependencies logged with helpful messages

### Plugins Panel UI
Access via **🔌 Plugins** in the sidebar (below Settings).

**Features:**
- Lists all discovered plugins (available + unavailable)
- Visual status indicators (✅ Available / ❌ Unavailable)
- Capability badges for each plugin
- Expandable dependency sections showing:
  - System dependencies with versions
  - Python dependencies with versions
  - Satisfaction status per dependency
- Installation instructions for missing dependencies
- Copy-to-clipboard for install commands
- Refresh button to re-check after installing dependencies

## Implementation

### Core Components

**Version Checker** (`src/utils/version_checker.py`):
- Parse version strings into comparable tuples
- Compare versions (semver-style)
- Check version constraints
- Parse pip-style package specs

**Dependency Checker** (`src/utils/dependency_checker.py`):
- Check system command existence
- Extract versions from command output
- Check Python module importability
- Get Python module versions
- Validate dependencies against constraints

**Base Controller** (`src/controllers/base_controller.py`):
- `get_system_dependencies()` - Declare system deps
- `get_python_dependencies()` - Declare Python deps

**Package Manager** (`src/controllers/package_manager.py`):
- `plugin_status` - Track detailed plugin status
- `get_plugin_status()` - Get status for all plugins
- `refresh_plugin_status()` - Re-check dependencies

**Plugins Panel** (`src/views/panels/plugins_panel.py`):
- Display plugin cards with status
- Show dependency details
- Provide installation instructions
- Copy commands to clipboard

## Usage

### For Plugin Developers

Declare dependencies in your plugin:

```python
class MyPlugin(BasePackageController):
    def get_system_dependencies(self) -> List[Dict]:
        return [
            {
                'name': 'MyTool',
                'command': 'mytool',
                'package': 'mytool',
                'min_version': '2.0.0',
                'version_command': ['mytool', '--version']
            }
        ]
    
    def get_python_dependencies(self) -> List[str]:
        return ['requests>=2.25.0', 'PyGObject>=3.40.0']
```

### For Users

1. Open **🔌 Plugins** panel from sidebar
2. View status of all plugins
3. Check dependency requirements
4. Install missing dependencies using provided commands
5. Click **🔄 Refresh** to re-check after installation

## Example Plugin Status

```
Plugin: APT Packages (apt)
  Status: ✅ Available
  Capabilities: search, install, remove, list_installed, list_updates, categories
  
  System Dependencies:
    ✓ APT (apt-get) v3.1.6
  
  Python Dependencies:
    ✓ apt v2.3.0
```

```
Plugin: Flatpak Applications (flatpak)
  Status: ❌ Unavailable
  Capabilities: (none - unavailable)
  
  System Dependencies:
    ✗ Flatpak (flatpak) Missing (requires >=1.12.0)
  
  Python Dependencies:
    ✓ PyGObject v3.40.1
  
  Missing dependencies:
    • Flatpak (command: flatpak)
  
  Install: sudo apt install flatpak
  [📋 Copy]
```

## Benefits

### For Developers
- Clear dependency declaration
- Automatic validation
- Version constraint support
- Helpful error messages

### For Users
- Understand why plugins are unavailable
- Get actionable installation instructions
- See exactly what's missing
- Easy dependency management

### For the Application
- Graceful degradation when dependencies missing
- No crashes from missing dependencies
- Clear plugin availability status
- Better user experience

## Technical Details

### Version Parsing
Versions parsed into tuples for comparison:
- `"2.4.5"` → `(2, 4, 5)`
- `"1.0"` → `(1, 0)`

### Constraint Checking
Supports standard comparison operators:
- `>=2.0.0` - Minimum version
- `<3.0.0` - Maximum version
- `==2.5.0` - Exact version
- `!=1.0.0` - Exclude version

### Plugin Status Structure
```python
{
    'backend_id': 'apt',
    'display_name': 'APT Packages',
    'available': True,
    'plugin': <APTPlugin instance>,
    'capabilities': {'search', 'install', ...},
    'dependencies': {
        'system': [
            {
                'name': 'APT',
                'command': 'apt-get',
                'required_version': '>=2.0.0',
                'installed_version': '3.1.6',
                'satisfied': True
            }
        ],
        'python': [
            {
                'package': 'apt',
                'required_version': '',
                'installed_version': '2.3.0',
                'satisfied': True
            }
        ]
    },
    'missing_dependencies': []
}
```

## Testing

Run the test script:
```bash
.venv/bin/python3 test_plugin_dependencies.py
```

This validates:
- Version parsing and comparison
- Dependency checking
- Plugin registration with dependencies
- Status tracking
- Refresh functionality
