# Plugins Button Issue Count

## Summary
Added issue count indicator to the Plugins button in the sidebar, showing the number of plugins with problems.

## Implementation

### Changes Made

**File: `src/views/main_view.py`**

1. **Added `update_plugins_button()` method:**
```python
def update_plugins_button(self):
    """Update the plugins button text with issue count"""
    plugin_status = self.package_manager.get_plugin_status()
    issue_count = sum(1 for status in plugin_status.values() if not status['available'])
    
    if issue_count > 0:
        self.pluginsBtn.setText(f"🔌 Plugins ({issue_count})")
    else:
        self.pluginsBtn.setText("🔌 Plugins")
```

2. **Called on application startup:**
```python
# In __init__ after setup_sidebar()
self.update_plugins_button()
```

3. **Connected to plugins panel refresh:**
```python
# In connect_panel_signals()
elif panel_name == 'plugins':
    panel.refresh_requested.connect(self.update_plugins_button)
```

## Behavior

### Display States

**No Issues:**
```
🔌 Plugins
```

**With Issues:**
```
🔌 Plugins (1)
🔌 Plugins (2)
```

### When Updated

1. **Application Launch** - Checks plugin status on startup
2. **Plugin Refresh** - Updates when user clicks refresh in Plugins panel
3. **After Dependency Install** - Updates when dependencies are installed

## Issue Detection

A plugin is considered to have an issue when:
- `status['available'] == False`

This happens when:
- System dependencies are missing
- Python dependencies are missing
- Backend is not available on the system
- Version constraints are not satisfied

## Example Scenarios

### Scenario 1: All Plugins Working
```
Plugins discovered: 2
  ✓ APT Packages
  ✓ Flatpak Applications

Button: "🔌 Plugins"
```

### Scenario 2: One Plugin Missing Dependencies
```
Plugins discovered: 2
  ✗ APT Packages (missing: Python: apt)
  ✓ Flatpak Applications

Button: "🔌 Plugins (1)"
```

### Scenario 3: Multiple Issues
```
Plugins discovered: 3
  ✗ APT Packages (missing: Python: apt)
  ✗ Flatpak Applications (missing: flatpak command)
  ✓ AppImage Manager

Button: "🔌 Plugins (2)"
```

## User Experience

### Benefits
1. **Immediate Visibility** - Users see issues at a glance
2. **Proactive Notification** - No need to open Plugins panel to check
3. **Consistent Pattern** - Matches Updates button behavior
4. **Non-Intrusive** - Doesn't block workflow

### User Flow
1. User launches app
2. Sees "🔌 Plugins (1)" in sidebar
3. Clicks to investigate
4. Views plugin details and missing dependencies
5. Installs dependencies
6. Clicks refresh
7. Button updates to "🔌 Plugins" (no count)

## Technical Details

### Count Calculation
```python
plugin_status = self.package_manager.get_plugin_status()
issue_count = sum(1 for status in plugin_status.values() if not status['available'])
```

### Status Structure
```python
{
    'apt': {
        'available': False,  # ← Used for counting
        'missing_dependencies': ['Python: apt'],
        ...
    }
}
```

## Testing

Test the implementation:
```bash
.venv/bin/python3 -c "
import sys
sys.path.insert(0, 'src')
from controllers.package_manager import PackageManager
from cache import LMDBManager
from services.logging_service import LoggingService

pm = PackageManager(LMDBManager(), LoggingService(stdout_log_level='ERROR'))
status = pm.get_plugin_status()
issues = sum(1 for s in status.values() if not s['available'])
print(f'Plugins with issues: {issues}')
"
```

## Future Enhancements

Possible improvements:
- Click count badge to jump directly to problematic plugins
- Different colors for different issue types
- Tooltip showing which plugins have issues
- Auto-refresh after dependency installation
- Notification when new issues detected

## Related Features

- **Updates Button** - Similar pattern: "⬆️ Updates (5)"
- **Plugin Dependencies** - Issue detection system
- **Plugins Panel** - Detailed issue display
- **Plugin Status Tracking** - Data source for count

## Files Modified

- `src/views/main_view.py` - Added update_plugins_button() method and integration
