# Widget Standardization Summary

## Overview
Standardized all list item widgets to use a common base class with consistent styling, dimensions, and behavior.

## Changes Made

### New Base Class
**File**: `src/widgets/base_list_item.py`

**Features**:
- Standard dimensions (height: 125px, icon: 64px, button: 80x32px)
- Standard colors (security red: #FF6B6B)
- Automatic dev outline detection and application
- Consistent frame styling with hover effects
- Transparent label mouse events
- Reusable styling methods

### Refactored Widgets

All three list item widgets now inherit from `BaseListItem`:

1. **PackageListItem** - Browse/search results
2. **InstalledListItem** - Installed packages
3. **UpdateListItem** - Available updates

### Benefits

**Code Reduction**:
- Removed ~40 lines of duplicate styling code per widget
- Centralized styling logic in one place

**Consistency**:
- All widgets use same height (125px)
- All widgets use same icon size (64px)
- All widgets use same button dimensions (80x32px)
- All widgets use same border radius (8px)
- All widgets use same padding/margins

**Maintainability**:
- Change styling in one place affects all widgets
- Easy to add new list item types
- Consistent behavior across all widgets

## Standard Dimensions

```python
ITEM_HEIGHT = 125      # Widget height
ICON_SIZE = 64         # Icon width/height
BUTTON_WIDTH = 80      # Action button width
BUTTON_HEIGHT = 32     # Action button height
```

## Standard Colors

```python
COLOR_SECURITY = "#FF6B6B"                    # Security update border
COLOR_SECURITY_BG = "rgba(255, 107, 107, 0.1)" # Security update hover
```

## Usage Pattern

```python
from widgets.base_list_item import BaseListItem

class MyListItem(BaseListItem):
    def __init__(self, data, parent=None):
        self.data = data
        super().__init__('src/ui/widgets/my_item.ui', parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Set widget-specific data
        self.nameLabel.setText(self.data['name'])
        
        # Apply dev outline to widgets
        self._apply_dev_outline(self.nameLabel, self.button)
        
        # Optional: Override frame style for special cases
        if self.data.get('special'):
            self._set_frame_style("red", "rgba(255,0,0,0.1)")
```

## UI File Requirements

All list item UI files should follow this structure:

- **Root**: QFrame with Box shape
- **Main Layout**: QHBoxLayout with 12px spacing
- **Icon**: 64x64 QLabel with emoji/icon
- **Content**: QVBoxLayout with name, description, info labels
- **Right Side**: QVBoxLayout with badge, spacer, action button

## Testing

All widgets maintain backward compatibility. No changes to public API or signals.
