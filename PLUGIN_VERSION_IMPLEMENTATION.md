# Plugin Version Implementation

## Summary
Added version tracking for plugins to identify plugin releases and track compatibility.

## Changes Made

### 1. BasePackageController (`src/controllers/base_controller.py`)
Added `version` property with default implementation:

```python
@property
def version(self) -> str:
    """Plugin version (e.g., '1.0.0')"""
    return "1.0.0"
```

**Design Decision:** Made it a regular property (not abstract) with default value so existing plugins don't break.

### 2. APTPlugin (`src/controllers/plugins/apt_plugin.py`)
Implemented version property:

```python
@property
def version(self) -> str:
    return '1.0.0'
```

### 3. PackageManager (`src/controllers/package_manager.py`)
Added version to plugin status tracking:

```python
status_info = {
    'backend_id': controller.backend_id,
    'display_name': controller.display_name,
    'version': controller.version,  # Added
    'available': controller.is_available() and dep_status['all_satisfied'],
    ...
}
```

### 4. PluginCard (`src/widgets/plugin_card.py`)
Display version in card header:

```python
version = status.get('version', '1.0.0')
self.nameLabel.setText(f"{status_icon} {status['display_name']} v{version}")
```

## Usage

### For Plugin Developers
Override the version property in your plugin:

```python
class MyPlugin(BasePackageController):
    @property
    def version(self) -> str:
        return '2.1.3'
```

### Version Format
Recommended: Semantic Versioning (semver)
- Format: `MAJOR.MINOR.PATCH`
- Example: `1.0.0`, `2.3.1`, `0.9.0-beta`

### Display
Versions appear in the Plugins panel:
```
✅ APT Packages v1.0.0
✅ Flatpak Applications v1.0.0
```

## Benefits

1. **Tracking**: Know which plugin version is installed
2. **Debugging**: Identify version-specific issues
3. **Compatibility**: Check plugin compatibility with app version
4. **Updates**: Track when plugins need updating
5. **Documentation**: Reference specific plugin versions in docs

## Future Enhancements

Possible additions:
- Version compatibility checking
- Plugin update notifications
- Minimum required app version
- Changelog per version
- Automatic version detection from git tags
- Version comparison utilities

## Testing

Run test:
```bash
.venv/bin/python3 -c "
import sys
sys.path.insert(0, 'src')
from controllers.plugins.apt_plugin import APTPlugin
from cache import LMDBManager
from services.logging_service import LoggingService

apt = APTPlugin(LMDBManager(), LoggingService(stdout_log_level='ERROR'))
print(f'APT Plugin version: {apt.version}')
"
```

Expected output:
```
APT Plugin version: 1.0.0
```

## Files Modified

1. `src/controllers/base_controller.py` - Added version property
2. `src/controllers/plugins/apt_plugin.py` - Implemented version
3. `src/controllers/package_manager.py` - Track version in status
4. `src/widgets/plugin_card.py` - Display version in UI

## Backward Compatibility

✅ Fully backward compatible
- Default version provided in base class
- Existing plugins work without changes
- Optional override for custom versions
