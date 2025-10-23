# Plugin Card UI Refactoring

## Summary
Refactored plugin card generation from programmatic code to Qt Designer UI file with dedicated widget class.

## Changes Made

### New Files Created
1. **`src/ui/widgets/plugin_card.ui`** - Qt Designer UI file
   - Defines card layout structure
   - Includes all sections: header, status, capabilities, dependencies, missing deps
   - Styled with inline CSS

2. **`src/widgets/plugin_card.py`** - PluginCard widget class
   - Loads UI from .ui file
   - Populates data from plugin status dict
   - Handles copy-to-clipboard functionality
   - Self-contained logic for card display

### Modified Files
1. **`src/views/panels/plugins_panel.py`**
   - Simplified from ~200 lines to ~60 lines
   - Removed `create_plugin_card()` method (150+ lines)
   - Removed `get_install_command()` method
   - Removed `copy_to_clipboard()` method
   - Now simply creates `PluginCard(status)` instances

## Before vs After

### Before (Programmatic)
```python
def create_plugin_card(self, status):
    card = QFrame()
    card.setFrameShape(QFrame.Shape.StyledPanel)
    card.setStyleSheet("""...""")
    
    layout = QVBoxLayout(card)
    
    # Header
    header = QHBoxLayout()
    status_icon = "✅" if status['available'] else "❌"
    name_label = QLabel(f"{status_icon} {status['display_name']}")
    name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
    header.addWidget(name_label)
    # ... 100+ more lines of layout code
    
    return card
```

### After (UI File + Widget)
```python
# In plugins_panel.py
card = PluginCard(status)
layout.addWidget(card)

# In plugin_card.py
class PluginCard(QFrame):
    def __init__(self, status, parent=None):
        super().__init__(parent)
        uic.loadUi('src/ui/widgets/plugin_card.ui', self)
        self.status = status
        self.populate()
```

## Benefits

### 1. Separation of Concerns
- **UI Structure**: Defined in .ui file (visual design)
- **Data Population**: Handled in widget class (logic)
- **Panel Logic**: Simplified to data fetching only

### 2. Maintainability
- UI changes can be made in Qt Designer
- No need to modify Python code for layout tweaks
- Widget class is reusable

### 3. Code Reduction
- PluginsPanel: 200 lines → 60 lines (70% reduction)
- Removed complex nested layout code
- Cleaner, more readable code

### 4. Consistency
- Follows project pattern (UI files + controllers)
- Matches other widgets (PackageListItem, InstalledListItem, etc.)
- Standard Qt Designer workflow

### 5. Testability
- Widget can be tested independently
- Mock status data easily injected
- UI structure validated separately from logic

## Architecture

```
PluginsPanel
    ├─ Queries PackageManager.get_plugin_status()
    ├─ Creates PluginCard for each plugin
    └─ Adds cards to layout

PluginCard (Widget)
    ├─ Loads plugin_card.ui
    ├─ Populates with status data
    ├─ Handles dependencies display
    ├─ Manages missing deps warning
    └─ Provides copy-to-clipboard

plugin_card.ui (Qt Designer)
    ├─ Defines card structure
    ├─ Sets up layouts
    ├─ Applies styling
    └─ Names widgets for access
```

## UI Structure (plugin_card.ui)

```
QFrame (PluginCard)
├─ nameLabel (header with icon)
├─ backendIdLabel (badge)
├─ statusLabel
├─ capabilitiesLabel
├─ dependenciesFrame
│   └─ depsContainer (dynamic labels added)
└─ missingFrame (conditional)
    ├─ missingContainer (dynamic labels added)
    ├─ installLabel (command)
    └─ copyBtn
```

## Widget Lifecycle

1. **Creation**: `card = PluginCard(status)`
2. **UI Load**: `uic.loadUi('plugin_card.ui', self)`
3. **Population**: `self.populate()`
   - Set header labels
   - Populate dependencies
   - Show/hide missing section
4. **Display**: Added to parent layout
5. **Interaction**: Copy button click → clipboard

## Testing

```bash
.venv/bin/python3 -c "
from widgets.plugin_card import PluginCard
status = {...}  # Mock status
card = PluginCard(status)
# Card ready to display
"
```

## Future Enhancements

Possible improvements now that card is a widget:
- Add expand/collapse for dependencies
- Plugin enable/disable toggle
- Direct install button (with pkexec)
- Plugin settings access
- Version update notifications
- Drag-and-drop priority ordering

## Files Summary

**New Files (2):**
- src/ui/widgets/plugin_card.ui
- src/widgets/plugin_card.py

**Modified Files (1):**
- src/views/panels/plugins_panel.py

**Lines Changed:**
- Removed: ~150 lines (programmatic UI code)
- Added: ~120 lines (widget class + UI file)
- Net: -30 lines, much cleaner structure

## Conclusion

The refactoring successfully:
- ✅ Separates UI structure from logic
- ✅ Reduces code complexity
- ✅ Improves maintainability
- ✅ Follows Qt best practices
- ✅ Makes cards reusable
- ✅ Maintains all functionality
