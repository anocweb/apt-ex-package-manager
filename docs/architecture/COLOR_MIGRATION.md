# Static Color Migration to UI Files

## Summary
Moved all statically assigned colors from Python code to UI files and QSS stylesheets for better theme consistency and maintainability.

## Changes Made

### 1. Main Window (`main_window.ui`)
**Added styling to UI file:**
- `centralwidget`: Background color using `palette(base)`
- `headerWidget`: Background color using `palette(window)`
- `sidebar`: Complete button styling with hover/pressed/selected states
- `separator1`: Border color using `palette(mid)` instead of hardcoded `#555`

**Removed from Python (`main_view.py`):**
- `apply_sidebar_theme()` method (no longer needed)
- Inline `setStyleSheet()` calls for centralWidget and headerWidget

### 2. Status Bar Widgets (`statusbar.qss`)
**Created new stylesheet file:**
- `db_stats_label`: Padding and font-size styling
- `log_button`: Transparent background with hover effect using `palette(highlight)`

**Updated Python (`main_view.py`):**
- Load stylesheet from external QSS file
- Set object names for proper selector targeting
- Removed inline `setStyleSheet()` calls

### 3. Update List Item (`update_list_item.qss`)
**Created new stylesheet file:**
- Property-based styling for security label: `QLabel#securityLabel[security="true"]`
- Uses hardcoded `#FF6B6B` for security updates (dynamic state)

**Updated UI file (`update_list_item.ui`):**
- Removed hardcoded red color from security label

**Updated Python (`update_list_item.py`):**
- Load stylesheet on initialization
- Set `security` property dynamically for security updates
- Trigger style refresh with `unpolish()`/`polish()`

## Benefits

1. **Theme Consistency**: All static colors now use Qt's palette system
2. **Centralized Styling**: Visual styling lives in UI/QSS files, not Python
3. **Easier Maintenance**: Change colors in one place instead of scattered across Python files
4. **Better KDE Integration**: Automatic adaptation to system theme changes

## Dynamic Colors (Kept in Python)

The following colors remain in Python code because they depend on runtime state:
- Security update icon background (`rgba(255, 107, 107, 0.2)`) - only shown for security updates
- Security label text color - uses property-based selector in QSS

## File Structure

```
src/ui/
├── styles/
│   ├── statusbar.qss          # Status bar widget styles
│   └── update_list_item.qss   # Update item styles
├── windows/
│   └── main_window.ui         # Main window with embedded styles
└── widgets/
    └── update_list_item.ui    # Update item UI
```

## Usage Pattern

For future styling:
1. **Static colors**: Add to UI file or QSS stylesheet using `palette()` colors
2. **Dynamic colors**: Use property-based selectors in QSS + `setProperty()` in Python
3. **Complex logic**: Keep in Python but minimize hardcoded values
