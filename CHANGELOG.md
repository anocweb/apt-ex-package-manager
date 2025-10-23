# Changelog

## Recent Changes

### Plugin System Enhancements

#### Python Package Name Detection (Latest)
- **Fixed**: Automatic detection of python3- vs python- package naming
  - Checks if `python3-<package>` exists first
  - Falls back to `python-<package>` if not found
  - Defaults to `python3-` if neither found
  - Fixes installation on systems with different naming conventions
- **Files Modified**:
  - `src/widgets/plugin_card.py`
- **Documentation**: `PYTHON_PACKAGE_DETECTION.md`

#### Plugins Button Issue Count
- **Added**: Issue count indicator on Plugins button
  - Shows "🔌 Plugins (n)" when n plugins have issues
  - Updates on application launch
  - Updates when plugins panel refreshed
  - Matches Updates button pattern
- **Files Modified**:
  - `src/views/main_view.py`
- **Documentation**: `PLUGIN_BUTTON_COUNT.md`

#### Plugin Versioning (Latest)
- **Added**: Plugin version tracking
  - `version` property in BasePackageController (default: "1.0.0")
  - Version displayed in Plugins panel UI
  - Version tracked in PackageManager status
- **Files Modified**:
  - `src/controllers/base_controller.py`
  - `src/controllers/plugins/apt_plugin.py`
  - `src/controllers/package_manager.py`
  - `src/widgets/plugin_card.py`
- **Documentation**: `PLUGIN_VERSION_IMPLEMENTATION.md`

#### Plugin Card UI Improvements
- **Changed**: Status label → Context-sensitive action button
  - "Install" - When dependencies missing (functional)
  - "Disable" - When plugin available (TODO)
  - "Enable" - When plugin unavailable (TODO)
- **Added**: Install dependencies functionality
  - Runs `pkexec apt-get install` with GUI password prompt
  - Confirmation dialog before installation
  - Success/error feedback
- **Removed**: 
  - Missing dependencies frame (yellow warning box)
  - Capabilities label display
- **Files Modified**:
  - `src/ui/widgets/plugin_card.ui`
  - `src/widgets/plugin_card.py`

#### Plugin Card Widget Refactoring
- **Created**: Qt Designer UI file for plugin cards
  - `src/ui/widgets/plugin_card.ui`
  - `src/widgets/plugin_card.py`
- **Simplified**: PluginsPanel from ~200 lines to ~60 lines
- **Removed**: 150+ lines of programmatic UI code
- **Documentation**: `PLUGIN_CARD_REFACTOR.md`

#### Plugin Dependencies System
- **Added**: Version-aware dependency management
  - System dependencies with version constraints
  - Python dependencies with pip-style specs
  - Automatic dependency checking during plugin discovery
  - Dedicated Plugins panel (🔌 in sidebar)
- **Created**:
  - `src/utils/version_checker.py` - Version parsing/comparison
  - `src/utils/dependency_checker.py` - Dependency validation
  - `src/ui/panels/plugins_panel.ui` - Plugins panel UI
  - `src/views/panels/plugins_panel.py` - Plugins panel controller
  - `test_plugin_dependencies.py` - Test script
- **Modified**:
  - `src/controllers/base_controller.py` - Added dependency methods
  - `src/controllers/plugins/apt_plugin.py` - Implemented dependencies
  - `src/controllers/package_manager.py` - Enhanced plugin tracking
  - `src/ui/windows/main_window.ui` - Added Plugins button
  - `src/views/main_view.py` - Wired up Plugins panel
- **Documentation**:
  - `docs/planning/PLUGIN_DEPENDENCIES.md`
  - `docs/features/PLUGIN_DEPENDENCIES.md`
  - `docs/PLUGIN_DEPENDENCIES_QUICKSTART.md`
  - `IMPLEMENTATION_SUMMARY.md`

## Summary of Plugin System

### Current State
- ✅ Plugin discovery and registration
- ✅ Dependency declaration (system + Python)
- ✅ Version constraints support
- ✅ Automatic dependency checking
- ✅ Plugin status tracking
- ✅ Plugins UI panel with status display
- ✅ Install dependencies functionality
- ✅ Plugin versioning
- ⬜ Enable/disable plugins (TODO)
- ⬜ Plugin priority ordering (TODO)
- ⬜ Plugin updates (TODO)

### Architecture
```
BasePackageController (Abstract)
├─ Properties: backend_id, display_name, version
├─ Methods: is_available(), get_capabilities()
├─ Dependencies: get_system_dependencies(), get_python_dependencies()
└─ Package Operations: search, install, remove, etc.

PackageManager
├─ Plugin Discovery: Auto-discover from plugins/
├─ Dependency Checking: Validate before registration
├─ Status Tracking: Detailed plugin information
└─ Backend Routing: Route operations to plugins

Plugins Panel
├─ Display: All plugins with status
├─ Dependencies: Show system + Python deps
├─ Actions: Install missing dependencies
└─ Version: Display plugin versions
```

### Files Overview

**Core Plugin System**:
- `src/controllers/base_controller.py` - Plugin interface
- `src/controllers/package_manager.py` - Plugin manager
- `src/controllers/plugins/apt_plugin.py` - APT implementation

**Dependency System**:
- `src/utils/version_checker.py` - Version utilities
- `src/utils/dependency_checker.py` - Dependency validation

**UI Components**:
- `src/ui/panels/plugins_panel.ui` - Plugins panel layout
- `src/views/panels/plugins_panel.py` - Plugins panel controller
- `src/ui/widgets/plugin_card.ui` - Plugin card layout
- `src/widgets/plugin_card.py` - Plugin card widget

**Documentation**:
- `docs/planning/PLUGIN_DEPENDENCIES.md` - Implementation plan
- `docs/features/PLUGIN_DEPENDENCIES.md` - Feature documentation
- `docs/PLUGIN_DEPENDENCIES_QUICKSTART.md` - Quick start guide
- `PLUGIN_VERSION_IMPLEMENTATION.md` - Version feature docs
- `PLUGIN_CARD_REFACTOR.md` - UI refactoring docs
- `IMPLEMENTATION_SUMMARY.md` - Overall summary
- `.amazonq/rules/plugin-development.md` - Development rules

**Tests**:
- `test_plugin_dependencies.py` - Dependency system tests
