# Plugin Settings Integration Plan

## Overview
Integrate the plugin architecture with the settings panel to support dynamic backend configuration, priority management, and extensible settings.

## Goals
1. Remove hardcoded backend sections from settings panel
2. Support both schema-based and custom widget settings
3. Implement backend priority list (reorderable)
4. Allow plugins to manage their own repositories and settings
5. Maintain backward compatibility

## Architecture

### Backend Priority System
- Ordered list of backend IDs stored in AppSettings
- Used by PackageManager for:
  - Default backend selection (highest priority)
  - Multi-backend search result ordering
  - Package conflict resolution
- User can reorder via drag-drop or up/down buttons

### Plugin Settings Methods
Plugins can provide settings via two approaches:

**Option 1: Schema-based (auto-generated UI)**
```python
def get_settings_schema(self) -> Dict:
    return {
        'auto_update': {
            'type': 'boolean',
            'label': 'Automatically check for updates',
            'default': True
        },
        'cache_ttl': {
            'type': 'integer',
            'label': 'Cache refresh interval (hours)',
            'default': 24,
            'min': 1,
            'max': 168
        }
    }
```

**Option 2: Custom Widget**
```python
def get_settings_widget(self, parent=None) -> QWidget:
    # Return fully custom QWidget
    pass
```

**Settings Change Callback**
```python
def on_settings_changed(self, setting_key: str, value):
    # Handle setting changes
    pass
```

### Settings Storage
- Backend priority: `backend_priority` (list)
- Backend-specific settings: `backends.{backend_id}.{setting_key}`
- Example: `backends.apt.auto_update`, `backends.flatpak.default_remote`

## Implementation Phases

### Phase 1: Foundation (AppSettings & Utilities)

#### Step 1.1: Update AppSettings
**File**: `src/settings/app_settings.py`

Add methods:
- `get_backend_priority() -> List[str]`
- `set_backend_priority(backends: List[str])`
- `get_backend_setting(backend_id: str, key: str, default=None)`
- `set_backend_setting(backend_id: str, key: str, value)`

#### Step 1.2: Create SettingsWidgetFactory
**File**: `src/utils/settings_widget_factory.py` (new)

Utility class to auto-generate Qt widgets from schema:
- Map schema types to Qt widgets
- Support types: boolean, integer, string, choice, repository_list
- Generate labels, tooltips, validators
- Connect value changes to callbacks

#### Step 1.3: Create BackendPriorityWidget
**File**: `src/widgets/backend_priority_widget.py` (new)

Reorderable list widget:
- Display backend display names
- Drag-drop reordering
- Up/Down arrow buttons
- Emit signal on order change

### Phase 2: Settings Panel Restructure

#### Step 2.1: Update Settings Panel UI
**File**: `src/ui/panels/settings_panel.ui`

Changes:
- Remove hardcoded backend sections (Flatpak, APT, AppImage)
- Add general settings section with:
  - Backend priority widget
  - ODRS settings (keep existing)
- Add dynamic backend container: `backendSettingsContainer` (QVBoxLayout)

#### Step 2.2: Update SettingsPanel Controller
**File**: `src/views/panels/settings_panel.py`

Major refactor:
- Remove hardcoded backend logic
- Add `load_backend_sections()` method
- For each available backend:
  - Create collapsible section widget
  - Check for custom widget first, then schema
  - Add repository management UI
  - Show priority position in header
- Connect priority widget to AppSettings
- Handle backend settings changes

### Phase 3: Plugin Implementation

#### Step 3.1: Update APT Plugin Settings
**File**: `src/controllers/plugins/apt_plugin.py`

Implement:
- `get_settings_schema()` - Define APT-specific settings
- `get_repository_sources()` - Return list of APT sources
- `on_settings_changed()` - Handle setting updates

#### Step 3.2: Update Flatpak Plugin Settings (stub)
**File**: `src/controllers/plugins/flatpak_plugin.py`

Add placeholder implementations for future development

### Phase 4: PackageManager Integration

#### Step 4.1: Update PackageManager
**File**: `src/controllers/package_manager.py`

Changes:
- Load backend priority from AppSettings
- Add `get_backends_by_priority() -> List[BasePackageController]`
- Update `search_packages()` to respect priority
- Update `install_package()` to use highest priority backend by default
- Add `set_backend_priority()` method

### Phase 5: Testing & Documentation

#### Step 5.1: Testing
- Test with single backend (APT only)
- Test with multiple backends
- Test priority reordering
- Test schema-based settings
- Test custom widget settings
- Test settings persistence

#### Step 5.2: Documentation
- Update plugin development guide
- Document settings schema format
- Add examples for both approaches
- Update architecture documentation

## Schema Type Specifications

### Supported Types

**boolean**
```python
{
    'type': 'boolean',
    'label': 'Enable feature',
    'default': True,
    'tooltip': 'Optional tooltip text'
}
```
Widget: QCheckBox

**integer**
```python
{
    'type': 'integer',
    'label': 'Cache TTL',
    'default': 24,
    'min': 1,
    'max': 168,
    'suffix': ' hours'
}
```
Widget: QSpinBox

**string**
```python
{
    'type': 'string',
    'label': 'API Key',
    'default': '',
    'placeholder': 'Enter API key',
    'password': False
}
```
Widget: QLineEdit

**choice**
```python
{
    'type': 'choice',
    'label': 'Update frequency',
    'choices': ['daily', 'weekly', 'monthly'],
    'default': 'weekly'
}
```
Widget: QComboBox

**repository_list**
```python
{
    'type': 'repository_list',
    'label': 'Sources',
    'editable': True,
    'actions': ['add', 'remove', 'edit']
}
```
Widget: QTreeWidget with action buttons

## UI Layout

```
Settings Panel
├── General Settings
│   ├── Backend Priority
│   │   ┌─────────────────────────┐
│   │   │ ≡ APT Packages      ↑↓  │
│   │   │ ≡ Flatpak           ↑↓  │
│   │   └─────────────────────────┘
│   └── Ratings & Reviews
│       └── [✓] Enable ODRS
│
├── APT Settings (#1 Priority)
│   ├── Repository Sources
│   │   └── [Tree widget with sources]
│   └── Backend Settings
│       └── [Schema-generated or custom widget]
│
├── Flatpak Settings (#2 Priority)
│   ├── Repository Sources
│   └── Backend Settings
│
└── AppImage Settings (#3 Priority)
    └── [Custom widget or "Not available"]
```

## Migration Strategy

1. **Phase 1**: Implement foundation without breaking existing code
2. **Phase 2**: Add new dynamic sections alongside hardcoded ones
3. **Phase 3**: Migrate APT to use new system
4. **Phase 4**: Remove hardcoded sections
5. **Phase 5**: Test and document

## Backward Compatibility

- Existing settings remain functional during migration
- Default backend priority: order of plugin discovery
- If priority not set, use 'apt' as default (current behavior)
- Existing ODRS and other settings unchanged

## Future Enhancements

- Import/export backend configurations
- Per-backend enable/disable toggles
- Backend-specific keyboard shortcuts
- Settings search/filter
- Settings profiles (power user, minimal, etc.)

## Success Criteria

- ✅ No hardcoded backend UI in settings panel
- ✅ Plugins can register settings via schema or custom widget
- ✅ Backend priority is user-configurable
- ✅ Settings persist across application restarts
- ✅ APT plugin fully migrated to new system
- ✅ Easy to add new backends without modifying settings panel
- ✅ All existing functionality preserved
