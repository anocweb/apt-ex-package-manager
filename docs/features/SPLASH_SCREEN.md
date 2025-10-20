# Splash Screen Feature

## Overview
The application displays a splash screen during startup to provide visual feedback during the cache population process, which can take 5-30 seconds.

## Design

### Visual Layout
```
┌─────────────────────────────────────┐
│                                     │
│         [App Icon 64x64]            │
│                                     │
│      Apt-Ex Package Manager         │
│                                     │
│    [=========>          ] 45%       │
│                                     │
│   Caching packages...               │
│   Cached 2,500 / 5,500 packages     │
│                                     │
└─────────────────────────────────────┘
```

### Specifications
- **Size**: 500x300 pixels
- **Position**: Centered on screen
- **Background**: Dark gray (#2d2d2d) to match KDE Plasma dark theme
- **Always on top**: Stays visible during startup

### Components
1. **App Icon** - 64x64 pixel logo at top
2. **Title** - "Apt-Ex Package Manager" in bold, 16pt
3. **Progress Bar** - Determinate (0-100%), blue theme (#3daee9)
4. **Status Label** - Current operation (e.g., "Caching packages...")
5. **Detail Label** - Additional info (e.g., "Cached X / Y packages")

## Progress Stages

| Progress | Status Message | Detail Message |
|----------|----------------|----------------|
| 0-5% | Starting up... | |
| 5-10% | Initializing services... | |
| 10-15% | Checking cache status... | |
| 15% | Loading package database... | |
| 15-85% | Caching packages... | Cached X / Y packages |
| 90% | Updating installed status... | |
| 98% | Loading user interface... | |
| 100% | Ready | Loaded X packages |

## Implementation

### File: `src/views/splash_screen.py`

**Class**: `SplashScreen(QSplashScreen)`

**Key Methods**:
- `__init__()` - Creates splash with custom layout
- `update_progress(value, status, detail)` - Updates progress and messages
- `set_status(message)` - Updates status message only

**Features**:
- Custom widget layout with QVBoxLayout
- Styled progress bar with KDE blue theme
- Automatic event processing to keep UI responsive
- Graceful fallback if app icon not found

### Integration: `src/controllers/application_controller.py`

**Lifecycle**:
1. `_show_splash()` - Display splash at start of `initialize()`
2. Update progress during each initialization step
3. `_hide_splash()` - Close splash after main view created

**Progress Updates**:
- Theme setup: "Setting up theme..."
- Services: "Initializing services..."
- Plugins: "Discovering plugins..."
- Cache: Real-time progress with package counts
- UI: "Loading user interface..."

## User Experience

### Benefits
- **Immediate feedback** - User knows app is loading
- **Progress visibility** - Real progress bar, not fake animation
- **Status updates** - Clear messages about what's happening
- **Professional appearance** - Polished startup experience

### Behavior
- Appears immediately on launch
- Shows real-time progress during cache population
- Automatically closes when main window appears
- Smooth transition to main application

## Testing

### Manual Test
```bash
python test_splash.py
```

This simulates the startup sequence with delays to verify:
- Splash screen displays correctly
- Progress bar updates smoothly
- Status messages change appropriately
- Detail messages appear
- Splash closes properly

### Integration Test
```bash
python src/main.py
```

Verify:
- Splash appears on startup
- Progress updates during actual cache loading
- Package counts are accurate
- Splash closes when main window shows

## Technical Details

### Qt Components Used
- `QSplashScreen` - Base splash screen class
- `QWidget` - Container for custom layout
- `QVBoxLayout` - Vertical layout for components
- `QLabel` - Text labels for title, status, detail
- `QProgressBar` - Determinate progress indicator
- `QPixmap` - Background and icon images

### Styling
- CSS-like stylesheets for progress bar
- Color scheme matches KDE Plasma
- Font sizes: Title 16pt, Status 12pt, Detail 11pt
- Responsive layout with proper spacing

### Performance
- Calls `QApplication.processEvents()` to keep responsive
- Forces `repaint()` after each update
- Minimal overhead during cache loading
- No separate thread needed (runs on main thread)

## Future Enhancements

### Potential Improvements
- [ ] Animated logo/icon
- [ ] Fade in/out transitions
- [ ] Theme-aware colors (light/dark)
- [ ] Configurable via settings
- [ ] Skip splash option (--no-splash flag)
- [ ] Show backend being loaded (APT/Flatpak)
- [ ] Display version number
- [ ] Show tips/hints during loading

### Accessibility
- [ ] Screen reader announcements
- [ ] High contrast mode support
- [ ] Keyboard shortcut to skip (Esc)
- [ ] Configurable timeout

## Related Documentation
- [Startup Workflow](../architecture/STARTUP_WORKFLOW.md) - Complete initialization sequence
- [Design Guidelines](DESIGN_GUIDELINES.md) - UI design standards
- [Features](FEATURES.md) - All application features
