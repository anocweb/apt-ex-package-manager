# Plugin Dependencies Quick Start

## For Users

### Viewing Plugin Status
1. Launch the application
2. Click **🔌 Plugins** in the sidebar (below Settings)
3. View all discovered plugins and their status

### Understanding Plugin Status
- **✅ Available** - Plugin is ready to use
- **❌ Unavailable** - Plugin has missing dependencies

### Installing Missing Dependencies
1. Find the plugin with missing dependencies
2. Look for the yellow warning box showing what's missing
3. Copy the install command using the **📋 Copy** button
4. Run the command in your terminal
5. Click **🔄 Refresh** in the Plugins panel to re-check

## For Plugin Developers

### Plugin Version

Declare your plugin version:

```python
class MyPlugin(BasePackageController):
    @property
    def version(self) -> str:
        return '1.0.0'  # Use semantic versioning
```

### Declaring Dependencies

Add these methods to your plugin class:

```python
from controllers.base_controller import BasePackageController
from typing import List, Dict

class MyPlugin(BasePackageController):
    
    def get_system_dependencies(self) -> List[Dict]:
        """Declare system binary/package dependencies"""
        return [
            {
                'name': 'MyTool',           # Display name
                'command': 'mytool',        # Command to check
                'package': 'mytool',        # Package name for install
                'min_version': '2.0.0',     # Minimum version (optional)
                'version_command': ['mytool', '--version']  # How to get version
            }
        ]
    
    def get_python_dependencies(self) -> List[str]:
        """Declare Python package dependencies"""
        return [
            'requests>=2.25.0',      # With minimum version
            'PyGObject>=3.40.0,<4.0.0',  # With version range
            'lxml'                   # Without version constraint
        ]
```

### Version Constraints

Supported operators:
- `>=` - Minimum version (most common)
- `>` - Greater than
- `<=` - Maximum version
- `<` - Less than
- `==` - Exact version
- `!=` - Not this version

### Testing Your Plugin

```bash
.venv/bin/python3 test_plugin_dependencies.py
```

This will show:
- Whether your plugin is discovered
- Dependency satisfaction status
- What's missing (if anything)
- Installed versions

### Example Output

```
Plugin: My Plugin (myplugin)
  Status: ✗ Unavailable
  System Dependencies:
    ✓ MyTool (mytool) v2.5.0
  Python Dependencies:
    ✗ requests
  Missing: Python: requests
```

## Common Patterns

### System Tool with Version
```python
{
    'name': 'Flatpak',
    'command': 'flatpak',
    'package': 'flatpak',
    'min_version': '1.12.0',
    'version_command': ['flatpak', '--version']
}
```

### System Tool without Version Check
```python
{
    'name': 'AppImage Tool',
    'command': 'appimagetool',
    'package': 'appimagetool',
    'min_version': None,
    'version_command': None
}
```

### Python Package with Version Range
```python
'requests>=2.25.0,<3.0.0'
```

### Python Package without Version
```python
'lxml'
```

## Troubleshooting

### Plugin Not Showing Up
- Check plugin file is in `src/controllers/plugins/`
- Ensure filename ends with `_plugin.py`
- Verify class inherits from `BasePackageController`
- Check logs for discovery errors

### Plugin Shows as Unavailable
- Open Plugins panel to see exact missing dependencies
- Install missing dependencies
- Click Refresh to re-check

### Version Not Detected
- Ensure `version_command` is correct
- Check command output contains version number
- Version must be in format like `1.2.3` or `v1.2.3`

## Files Reference

- **Version Checker**: `src/utils/version_checker.py`
- **Dependency Checker**: `src/utils/dependency_checker.py`
- **Base Controller**: `src/controllers/base_controller.py`
- **Package Manager**: `src/controllers/package_manager.py`
- **Plugins Panel**: `src/views/panels/plugins_panel.py`
- **Test Script**: `test_plugin_dependencies.py`

## More Information

- Full documentation: `docs/features/PLUGIN_DEPENDENCIES.md`
- Implementation plan: `docs/planning/PLUGIN_DEPENDENCIES.md`
- Plugin development rules: `.amazonq/rules/plugin-development.md`
