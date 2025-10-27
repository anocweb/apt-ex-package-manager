# Update Daemon Implementation Plan

## Overview
Independent background daemon that checks for package updates periodically and displays a persistent system tray icon when updates are available.

## Architecture

### Core Components

#### 1. Update Daemon (`src/update_daemon.py`)
- Standalone Python process running independently of GUI
- Uses `QApplication` (not `QCoreApplication`) to support tray icon
- Manages persistent system tray icon (visible only when updates available)
- Performs periodic update checks via QTimer
- Exposes D-Bus interface for GUI communication
- Runs as systemd user service

#### 2. D-Bus Interface
- **Service Name**: `org.aptex.UpdateChecker`
- **Object Path**: `/org/aptex/UpdateChecker`

**Methods**:
- `CheckNow()` - Trigger immediate update check
- `GetUpdateCount() -> int` - Return current update count
- `GetLastCheckTime() -> str` - Return ISO timestamp
- `SetCheckInterval(minutes: int)` - Change check interval

**Signals**:
- `UpdatesAvailable(count: int)` - Emitted when updates found
- `CheckCompleted()` - Check finished

#### 3. D-Bus Client (`src/services/update_daemon_client.py`)
- GUI-side client for daemon communication
- Wraps D-Bus calls in Python API
- Converts D-Bus signals to Qt signals
- Handles daemon unavailable gracefully

#### 4. Daemon Manager (`src/utils/daemon_manager.py`)
- Installation/uninstallation logic
- Start/stop/restart control
- Status checking
- Supports both system-wide and per-user installation

#### 5. System Integration
- **Systemd User Service**: Proper daemon lifecycle management
- **Systemd Preset**: Auto-enable for all users (system-wide install)
- **Per-User Fallback**: Manual installation without sudo

## Installation Modes

### System-Wide Installation (Default for All Users)
**Files**:
```
/usr/lib/systemd/user/apt-ex-update-checker.service
/usr/lib/systemd/user-preset/90-apt-ex.preset
```

**Characteristics**:
- Requires sudo/root for installation
- Automatically enabled for all users (existing + new)
- Each user gets their own daemon instance
- Used by package managers (deb/rpm)

**Installation**:
```bash
sudo bash scripts/install-daemon-system.sh
```

### Per-User Installation (Development/Manual)
**Files**:
```
~/.config/systemd/user/apt-ex-update-checker.service
```

**Characteristics**:
- No sudo required
- Current user only
- Manual enable required
- Development/testing use

**Installation**:
```bash
bash scripts/install-daemon.sh
```

## Tray Icon Behavior

### Visibility
- **Hidden** when no updates available (default state)
- **Visible** when updates found
- **Persists** while updates remain available
- **Disappears** after updates installed

### Icon States
- **Updates Available**: `system-software-update-available` icon
- Tooltip: "X updates available"

### User Interactions

**Left Click**:
- Launch main GUI application
- Navigate directly to Updates page
- Tray icon remains visible (updates still available)

**Right Click** - Context Menu:
```
┌─────────────────────────────────┐
│ 5 updates available             │ (disabled, info only)
├─────────────────────────────────┤
│ Open Updates                    │ → Launch GUI on Updates page
│ Check for Updates Now           │ → Trigger immediate check
├─────────────────────────────────┤
│ Quit Update Checker             │ → Stop daemon
└─────────────────────────────────┘
```

## User Experience Flows

### Scenario 1: Fresh Boot
1. Systemd starts daemon on user login
2. Tray icon hidden (no updates yet)
3. Daemon performs initial check
4. Finds 5 updates
5. Tray icon appears with "5 updates available"

### Scenario 2: User Installs Updates
1. User clicks tray icon
2. GUI launches on Updates page
3. Tray icon remains visible
4. User installs updates
5. GUI signals daemon: `UpdatesInstalled()`
6. Daemon rechecks, finds 0 updates
7. Tray icon disappears

### Scenario 3: GUI Closed
1. User closes main GUI window
2. GUI process exits
3. Tray icon remains visible (daemon independent)
4. Daemon continues periodic checks
5. User can reopen GUI by clicking tray icon

### Scenario 4: Periodic Check
1. Daemon timer triggers (every 4 hours)
2. Checks all enabled backends for updates
3. Finds new updates
4. Tray icon appears
5. Emits D-Bus signal: `UpdatesAvailable(count)`
6. If GUI running, it receives signal and updates UI

## File Structure

### New Files
```
src/
├── update_daemon.py                    # Daemon with tray (~250 lines)
├── services/
│   └── update_daemon_client.py         # D-Bus client (~100 lines)
└── utils/
    └── daemon_manager.py               # Install/control (~200 lines)

scripts/
├── install-daemon.sh                   # Per-user install (~40 lines)
└── install-daemon-system.sh            # System-wide install (~60 lines)

systemd/
├── apt-ex-update-checker.service       # Service unit file
└── 90-apt-ex.preset                    # Systemd preset

docs/
├── planning/
│   └── UPDATE_DAEMON_IMPLEMENTATION.md # This file
└── features/
    └── UPDATE_DAEMON.md                # User documentation
```

### Modified Files
- `src/main.py` - Handle `--show-updates` flag (~10 lines)
- `src/settings/app_settings.py` - Daemon settings (~40 lines)
- `src/ui/settings_panel.ui` - Daemon controls (Qt Designer)
- `src/views/main_view.py` - Optional daemon client integration (~60 lines)

## Settings Management

### AppSettings Methods
```python
# Daemon control
get_update_check_enabled() -> bool
set_update_check_enabled(enabled: bool)

get_update_check_interval() -> int  # minutes
set_update_check_interval(minutes: int)

get_last_update_check() -> str  # ISO timestamp
set_last_update_check(timestamp: str)

# Tray icon
get_show_tray_icon() -> bool
set_show_tray_icon(show: bool)
```

### Settings Panel UI
```
┌─ Update Notifications ──────────────────────┐
│ ☑ Enable automatic update checks            │
│ Check interval: [Every 4 hours ▼]           │
│                                              │
│ Daemon Status: ● Running                     │
│ Installation: System-wide (all users)        │
│ Last check: 2 hours ago                      │
│                                              │
│ [Check Now] [Restart Daemon]                 │
│                                              │
│ Installation:                                │
│ [Install for All Users] [Install for Me]    │
│ [Uninstall Daemon]                           │
└──────────────────────────────────────────────┘
```

## Technical Implementation Details

### Daemon Structure
```python
class UpdateDaemon(QObject):
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Stay running
        
        self.setup_tray_icon()
        self.setup_dbus()
        self.setup_update_timer()
        self.setup_logging()
    
    def setup_tray_icon(self):
        """Create system tray icon (initially hidden)"""
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon.fromTheme('system-software-update-available'))
        self.tray_icon.activated.connect(self.on_tray_clicked)
        # Don't show yet - only when updates found
    
    def update_tray_icon(self, update_count: int):
        """Show/hide tray based on updates"""
        if update_count > 0:
            self.tray_icon.setToolTip(f'{update_count} updates available')
            self.tray_icon.show()
        else:
            self.tray_icon.hide()
    
    def on_tray_clicked(self, reason):
        """Launch GUI on click"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            subprocess.Popen(['python', 'src/main.py', '--show-updates'])
    
    def check_for_updates(self):
        """Check all backends for updates"""
        # Run in background thread
        worker = UpdateCheckWorker(self.package_manager)
        worker.finished.connect(self.on_check_complete)
        worker.start()
```

### Systemd Service File
```ini
[Unit]
Description=Apt-Ex Package Manager Update Checker
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/share/apt-ex-package-manager/update_daemon.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

### Systemd Preset File
```ini
# /usr/lib/systemd/user-preset/90-apt-ex.preset
# Enable Apt-Ex update checker by default for all users
enable apt-ex-update-checker.service
```

### D-Bus Service Definition
```python
class UpdateCheckerDBus(dbus.service.Object):
    def __init__(self, daemon):
        bus_name = dbus.service.BusName(
            'org.aptex.UpdateChecker',
            bus=dbus.SessionBus()
        )
        super().__init__(bus_name, '/org/aptex/UpdateChecker')
        self.daemon = daemon
    
    @dbus.service.method('org.aptex.UpdateChecker')
    def CheckNow(self):
        """Trigger immediate update check"""
        self.daemon.check_for_updates()
    
    @dbus.service.method('org.aptex.UpdateChecker', out_signature='i')
    def GetUpdateCount(self):
        """Return current update count"""
        return self.daemon.update_count
    
    @dbus.service.signal('org.aptex.UpdateChecker', signature='i')
    def UpdatesAvailable(self, count):
        """Signal emitted when updates found"""
        pass
```

## Dependencies

### Python Packages
- `PyQt6` - GUI framework (already required)
- `dbus-python` - D-Bus bindings (new)
- `python3-apt` - APT integration (already required)
- `lmdb` - Caching (already required)

### System Packages
- `systemd` - User service management
- `dbus` - Message bus
- `python3-dbus` - D-Bus Python bindings

### Installation
```bash
# Python dependencies
pip install dbus-python

# System dependencies (Debian/Ubuntu)
sudo apt install python3-dbus systemd dbus
```

## Security Considerations

### Privilege Separation
- Daemon runs as user (not root)
- No elevated privileges required
- Package operations still require sudo (via GUI)

### D-Bus Security
- Session bus only (not system bus)
- User can only control their own daemon
- No cross-user communication

### Input Validation
- Validate all D-Bus method parameters
- Sanitize check intervals (min: 30 minutes, max: 24 hours)
- Prevent command injection in subprocess calls

## Error Handling

### Daemon Failures
- Systemd auto-restart on crash (`Restart=on-failure`)
- Log errors to `~/.local/share/apt-ex-package-manager/daemon.log`
- Graceful degradation if backends unavailable

### GUI Integration
- GUI works without daemon (just no background checks)
- Show "Daemon not running" in Settings if unavailable
- Offer to install/start daemon from Settings

### D-Bus Communication
- Handle daemon not responding (timeout: 5 seconds)
- Retry failed checks with exponential backoff
- Log D-Bus errors for debugging

## Testing Strategy

### Unit Tests
- Test daemon starts/stops correctly
- Test tray icon show/hide logic
- Test D-Bus method calls
- Test update check logic
- Mock PackageManager for isolation

### Integration Tests
- Test systemd service installation
- Test daemon survives GUI restart
- Test D-Bus signal delivery
- Test multiple backends
- Test preset auto-enable

### Manual Testing
- Install system-wide, verify all users get daemon
- Kill daemon, verify systemd restarts it
- Install updates, verify tray icon disappears
- Test with no updates available
- Test check interval changes

## Performance Considerations

### Resource Usage
- Daemon idle: ~20-30 MB RAM
- During check: ~50-100 MB RAM (temporary)
- CPU: Minimal when idle, brief spike during checks
- Network: Only during update checks

### Optimization
- Cache update results (avoid redundant checks)
- Use incremental checks when possible
- Throttle checks if system busy
- Batch D-Bus signals (avoid spam)

## Future Enhancements

### Potential Features
- Desktop notifications (in addition to tray icon)
- Automatic update installation (with user consent)
- Update scheduling (install at specific times)
- Bandwidth throttling for checks
- Update categories (security vs regular)
- Update history tracking

### Multi-Backend Support
- Check all enabled backends (APT, Flatpak, AppImage)
- Show backend-specific update counts
- Per-backend check intervals
- Unified update notifications

## Implementation Estimate

### Code Complexity
- **Daemon**: Medium-High (~250 lines)
- **D-Bus Client**: Medium (~100 lines)
- **Daemon Manager**: Medium (~200 lines)
- **GUI Integration**: Low-Medium (~60 lines)
- **Scripts**: Low (~100 lines)
- **Service Files**: Low (~20 lines)
- **Total**: ~730 lines + documentation

### Development Time
- Daemon core: 4-6 hours
- D-Bus integration: 3-4 hours
- Systemd integration: 2-3 hours
- GUI integration: 2-3 hours
- Testing: 3-4 hours
- Documentation: 2-3 hours
- **Total**: 16-23 hours

## References

### Documentation
- [systemd user services](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [systemd presets](https://www.freedesktop.org/software/systemd/man/systemd.preset.html)
- [D-Bus specification](https://dbus.freedesktop.org/doc/dbus-specification.html)
- [PyQt6 QSystemTrayIcon](https://doc.qt.io/qt-6/qsystemtrayicon.html)

### Similar Implementations
- KDE Discover update notifier
- GNOME Software background service
- Ubuntu update-notifier
- dnfdragora update checker
