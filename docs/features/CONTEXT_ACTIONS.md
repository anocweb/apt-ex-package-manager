# Context Actions System

## Overview
The context actions system provides a dynamic header area where each page can display relevant action buttons. This creates a clean, context-sensitive interface that adapts to the current page's functionality.

## Architecture

### Header Layout
```
[Page Title]                    [Context Actions Area]
```

- **Left**: Page title (left-aligned)
- **Right**: Dynamic action buttons (right-aligned)
- **Automatic**: Actions clear when switching pages

## Implementation

### Core Methods

#### `clear_context_actions()`
Removes all existing context action buttons from the header.

```python
def clear_context_actions(self):
    """Clear all context action buttons"""
    layout = self.contextActions.layout()
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
```

#### `add_context_action(text, callback)`
Adds a new action button to the header area.

```python
def add_context_action(self, text: str, callback):
    """Add a context action button"""
    button = QPushButton(text)
    button.clicked.connect(callback)
    self.contextActions.layout().addWidget(button)
    return button
```

## Usage Pattern

### Page-Specific Actions
Each page should define its context actions in the `select_page()` method:

```python
def select_page(self, page_key, page_index):
    # Clear previous actions
    self.clear_context_actions()
    
    # Add page-specific actions
    if page_key == 'updates':
        self.setup_updates_context_actions()
    elif page_key == 'installed':
        self.setup_installed_context_actions()

def setup_updates_context_actions(self):
    """Setup context actions for updates page"""
    self.add_context_action("🔄 Refresh", self.refresh_updates)
    self.add_context_action("⬆️ Update All", self.update_all_packages)

def setup_installed_context_actions(self):
    """Setup context actions for installed page"""
    self.add_context_action("🗑️ Remove Selected", self.remove_selected)
    self.add_context_action("📋 Export List", self.export_package_list)
```

## Examples

### Updates Page
- **🔄 Refresh**: Refresh available updates list
- **⬆️ Update All**: Update all available packages

### Installed Page
- **🗑️ Remove Selected**: Remove selected packages
- **📋 Export List**: Export installed packages list

### Settings Page
- **💾 Export Settings**: Export application settings
- **🔄 Reset to Defaults**: Reset all settings

### Home Page
- **🔍 Advanced Search**: Open advanced search dialog
- **⭐ Show Favorites**: Filter to favorite packages

## Best Practices

### Button Design
- **Icons**: Use emoji or Unicode symbols for visual clarity
- **Text**: Keep button text concise (2-3 words max)
- **Actions**: Use action verbs (Refresh, Update, Export, etc.)

### Action Grouping
- **Primary Actions**: Most important actions first (left to right)
- **Destructive Actions**: Place removal/deletion actions last
- **Limit Count**: Maximum 3-4 buttons to avoid crowding

### Callback Implementation
```python
def refresh_updates(self):
    """Refresh available updates"""
    self.statusbar.showMessage("Refreshing updates...", 2000)
    # Implement refresh logic
    
def update_all_packages(self):
    """Update all available packages"""
    self.statusbar.showMessage("Updating all packages...", 3000)
    # Implement update logic
```

## Integration with Panels

### Panel-Specific Actions
Each panel can define its own context actions by implementing setup methods:

```python
# In main_view.py
def setup_category_context_actions(self):
    """Setup actions for category browsing"""
    self.add_context_action("🔄 Refresh Category", self.refresh_category)
    self.add_context_action("⚙️ Category Settings", self.category_settings)
```

### Dynamic Button States
Buttons can be enabled/disabled based on current state:

```python
def setup_installed_context_actions(self):
    remove_btn = self.add_context_action("🗑️ Remove", self.remove_selected)
    # Disable if no packages selected
    remove_btn.setEnabled(self.has_selected_packages())
```

## UI Guidelines

### Visual Consistency
- **Spacing**: 5px between buttons
- **Height**: Buttons fit within 55px header height
- **Alignment**: Right-aligned in header area

### Responsive Design
- **Overflow**: Consider button overflow on small screens
- **Priority**: Most important actions should appear first
- **Fallback**: Provide menu alternatives for hidden actions

## Future Enhancements

### Planned Features
- **Keyboard Shortcuts**: Assign shortcuts to context actions
- **Tooltips**: Add helpful tooltips to action buttons
- **Button Groups**: Visual grouping of related actions
- **Overflow Menu**: Handle too many actions gracefully