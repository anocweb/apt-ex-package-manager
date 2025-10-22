# Plugin Settings Integration - Implementation Summary

## Overview
Successfully implemented dynamic plugin settings integration with backend priority management system.

## Completed Changes

### Phase 1: Foundation

#### 1. AppSettings Updates (`src/settings/app_settings.py`)
**Added Methods:**
- `get_backend_priority() -> List[str]` - Get ordered list of backend IDs
- `set_backend_priority(backends: List[str])` - Set backend priority order
- `get_backend_setting(backend_id, key, default)` - Get backend-specific setting
- `set_backend_setting(backend_id, key, value)` - Set backend-specific setting

**Added Default:**
- `backend_priority`: Empty list (populated on first use)

#### 2. SettingsWidgetFactory (`src/utils/settings_widget_factory.py`)
**New utility class for auto-generating Qt widgets from schema:**
- Supports types: boolean, integer, string, choice
- Emits `setting_changed` signal on value changes
- Maps schema definitions to appropriate Qt widgets:
  - boolean → QCheckBox
  - integer → QSpinBox (with min/max/suffix)
  - string → QLineEdit (with placeholder/password mode)
  - choice → QComboBox

#### 3. BackendPriorityWidget (`src/widgets/backend_priority_widget.py`)
**New reorderable list widget:**
- Drag-drop reordering support
- Up/Down arrow buttons
- Displays backend display names with "≡" handle
- Emits `priority_changed` signal with ordered backend IDs
- Stores backend_id in item data for tracking

### Phase 2: Settings Panel Restructure

#### 1. New Settings Panel UI (`src/ui/panels/settings_panel_new.ui`)
**Simplified structure:**
- General Settings section with:
  - Backend Priority container (dynamic widget insertion)
  - ODRS settings (preserved from original)
- Dynamic backend settings container (`backendSettingsContainer`)
- Removed all hardcoded backend sections

#### 2. New Settings Panel Controller (`src/views/panels/settings_panel_new.py`)
**Complete rewrite with dynamic backend integration:**

**Key Methods:**
- `load_backend_priority()` - Load and display backend priority from settings
- `on_priority_changed()` - Handle priority reordering, save to settings
- `load_backend_sections()` - Dynamically create sections for each backend
- `create_backend_section()` - Create settings UI for a backend
- `create_repository_section()` - Create repository management UI
- `on_backend_setting_changed()` - Handle setting changes, notify backend

**Features:**
- Shows priority number in each backend section header (e.g., "#1 Priority")
- Checks for custom widget first, falls back to schema-based generation
- Supports repository management for backends with 'repositories' capability
- Preserves ODRS settings from original panel

### Phase 3: Plugin Implementation

#### APT Plugin Updates (`src/controllers/plugins/apt_plugin.py`)
**Added Methods:**
- `get_settings_schema()` - Returns schema with 3 settings:
  - `auto_update_cache`: Boolean for automatic cache updates
  - `cache_ttl`: Integer (1-168 hours) for cache refresh interval
  - `show_technical_packages`: Boolean to show/hide technical packages
- `on_settings_changed()` - Handles setting change notifications

### Phase 4: PackageManager Integration

#### PackageManager Updates (`src/controllers/package_manager.py`)
**Constructor Changes:**
- Added `app_settings` parameter
- Calls `_load_backend_priority()` after plugin discovery

**New Methods:**
- `get_backends_by_priority()` - Returns backends ordered by priority
- `_load_backend_priority()` - Loads priority from settings, sets default backend
- `set_backend_priority()` - Updates priority in settings and default backend

**Updated Methods:**
- `search_packages()` - Now respects priority order when searching all backends

#### ApplicationController Updates (`src/controllers/application_controller.py`)
**Service Initialization:**
- Creates and registers AppSettings service
- Passes app_settings to PackageManager constructor

#### MainView Updates (`src/views/main_view.py`)
**Panel Loading:**
- Changed settings panel to use new UI file: `settings_panel_new.ui`
- Changed import to use new controller: `settings_panel_new.py`

## Architecture Benefits

### 1. Extensibility
- New backends automatically appear in settings
- No code changes needed to settings panel for new backends
- Plugins self-describe their settings

### 2. Flexibility
- Plugins can provide custom widgets OR use schema
- Schema-based settings auto-generate appropriate UI
- Backend priority affects search order and default selection

### 3. Maintainability
- No hardcoded backend UI in settings
- Settings storage is centralized in AppSettings
- Clear separation between UI and business logic

### 4. User Experience
- Visual priority management with drag-drop
- Clear indication of backend priority in section headers
- Consistent settings UI across all backends

## Settings Storage Structure

```
QSettings Storage:
├── backend_priority: ['apt', 'flatpak', 'appimage']
└── plugin_settings:
    ├── apt:
    │   ├── auto_update_cache: true
    │   ├── cache_ttl: 24
    │   └── show_technical_packages: false
    ├── flatpak:
    │   └── [future settings]
    └── appimage:
        └── [future settings]
```

## Usage Example

### For Plugin Developers

**Option 1: Schema-based Settings**
```python
def get_settings_schema(self) -> Dict:
    return {
        'my_setting': {
            'type': 'boolean',
            'label': 'Enable Feature',
            'default': True,
            'tooltip': 'Enable this awesome feature'
        }
    }

def on_settings_changed(self, setting_key: str, value):
    if setting_key == 'my_setting':
        # Handle setting change
        pass
```

**Option 2: Custom Widget**
```python
def get_settings_widget(self, parent=None) -> QWidget:
    widget = QWidget(parent)
    layout = QVBoxLayout(widget)
    # Build custom UI
    return widget
```

### For Users

1. Open Settings panel
2. Reorder backends in priority list (drag or use arrows)
3. Configure backend-specific settings in each section
4. Changes save automatically

## Testing Checklist

- [x] Backend priority widget displays available backends
- [x] Drag-drop reordering works
- [x] Up/Down buttons work
- [x] Priority changes save to settings
- [x] Backend sections show correct priority numbers
- [x] APT settings schema generates correct widgets
- [x] Setting changes trigger callbacks
- [x] Settings persist across app restarts
- [x] ODRS settings still work
- [x] PackageManager respects priority order

## Future Enhancements

1. **Repository Management**
   - Implement full repository CRUD operations
   - Backend-specific repository UI

2. **Additional Schema Types**
   - `repository_list` type with tree widget
   - `file_path` type with file picker
   - `color` type with color picker

3. **Settings Import/Export**
   - Export all settings to JSON
   - Import settings from file
   - Settings profiles (minimal, power user, etc.)

4. **Per-Backend Enable/Disable**
   - Toggle backends on/off without uninstalling
   - Disabled backends don't appear in priority list

5. **Settings Search**
   - Search/filter settings by keyword
   - Quick navigation to specific settings

## Migration Notes

### Old Settings Panel
- File: `src/ui/panels/settings_panel.ui`
- Controller: `src/views/panels/settings_panel.py`
- Status: **Preserved** (not deleted for reference)

### New Settings Panel
- File: `src/ui/panels/settings_panel_new.ui`
- Controller: `src/views/panels/settings_panel_new.py`
- Status: **Active** (loaded by MainView)

### Backward Compatibility
- Existing ODRS settings preserved
- Default backend falls back to 'apt' if priority not set
- Plugin settings stored in same location as before
- No breaking changes to existing functionality

## Documentation Updates Needed

1. Update plugin development guide with settings examples
2. Document settings schema format specification
3. Add user guide for backend priority management
4. Update architecture documentation with settings flow

## Success Criteria Met

✅ No hardcoded backend UI in settings panel  
✅ Plugins can register settings via schema or custom widget  
✅ Backend priority is user-configurable  
✅ Settings persist across application restarts  
✅ APT plugin fully migrated to new system  
✅ Easy to add new backends without modifying settings panel  
✅ All existing functionality preserved  

## Files Created

1. `/docs/planning/PLUGIN_SETTINGS_INTEGRATION.md` - Planning document
2. `/src/utils/settings_widget_factory.py` - Widget factory utility
3. `/src/widgets/backend_priority_widget.py` - Priority list widget
4. `/src/ui/panels/settings_panel_new.ui` - New settings UI
5. `/src/views/panels/settings_panel_new.py` - New settings controller
6. `/docs/planning/PLUGIN_SETTINGS_IMPLEMENTATION_SUMMARY.md` - This file

## Files Modified

1. `/src/settings/app_settings.py` - Added priority and backend setting methods
2. `/src/controllers/plugins/apt_plugin.py` - Added settings schema
3. `/src/controllers/package_manager.py` - Added priority support
4. `/src/controllers/application_controller.py` - Pass app_settings to PackageManager
5. `/src/views/main_view.py` - Use new settings panel
