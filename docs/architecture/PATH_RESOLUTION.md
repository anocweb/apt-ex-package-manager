# Resource Path Resolution System

## Overview
The application now uses a centralized `PathResolver` utility to locate resources (UI files, icons, stylesheets, plugins) in both development and system-wide installation environments.

## Implementation

### PathResolver (`src/utils/path_resolver.py`)
Centralized utility that searches for resources in this order:
1. **User config**: `~/.config/apt-ex-package-manager/`
2. **System install**: `/usr/share/apt-ex-package-manager/`
3. **Development**: `src/` (relative to project root)

### Methods
- `get_ui_path(relative_path)` - Find UI files (panels/*, widgets/*, windows/*)
- `get_icon_path(relative_path)` - Find icon files
- `get_stylesheet_path(relative_path)` - Find stylesheet files (in ui/styles/)
- `get_plugin_paths()` - Get list of plugin directories

## Updated Files

### Core Files
- `src/utils/path_resolver.py` - **NEW** - Centralized path resolution
- `src/controllers/package_manager.py` - Plugin discovery
- `src/views/main_view.py` - Main window and all panels
- `src/views/panels/base_panel.py` - Base panel class
- `src/views/splash_screen.py` - Splash screen
- `src/widgets/base_list_item.py` - Base list item widget
- `src/widgets/plugin_card.py` - Plugin card widget
- `src/services/theme_service.py` - Icon loading

### Usage Examples

```python
from utils.path_resolver import PathResolver

# Load UI file
uic.loadUi(PathResolver.get_ui_path('windows/main_window.ui'), self)

# Load icon
icon_path = PathResolver.get_icon_path('app-icon.svg')

# Load stylesheet
style_path = PathResolver.get_stylesheet_path('statusbar.qss')

# Get plugin directories
plugin_paths = PathResolver.get_plugin_paths()
```

## Benefits

1. **Works in Development**: Finds resources in `src/` directory
2. **Works When Installed**: Finds resources in `/usr/share/apt-ex-package-manager/`
3. **User Overrides**: Allows users to override resources in `~/.config/`
4. **Consistent**: Single source of truth for all resource paths
5. **Maintainable**: Easy to update search paths in one place

## Testing

The PathResolver has been tested and correctly resolves:
- ✓ UI files from system or development paths
- ✓ Icons from system or development paths
- ✓ Stylesheets from development paths
- ✓ Plugin directories (multiple locations)

## Debian Package Compatibility

The application now correctly handles installation via `.deb` package:
- UI files installed to: `/usr/share/apt-ex-package-manager/ui/`
- Icons installed to: `/usr/share/apt-ex-package-manager/icons/`
- Plugins installed to: `/usr/share/apt-ex-package-manager/plugins/`
- Python code installed to: `/usr/lib/python3/dist-packages/`

## Future Enhancements

Potential improvements:
- Add caching to avoid repeated filesystem checks
- Add logging for path resolution debugging
- Support XDG_DATA_DIRS for multi-directory search
- Add resource validation on startup
