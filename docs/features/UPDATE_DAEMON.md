# Update Daemon - Background Update Notifications

## Overview
The Update Daemon is a background service that automatically checks for package updates and displays a system tray icon when updates are available. It runs independently of the main GUI application.

## Features

### Automatic Update Checking
- Runs in the background as a systemd user service
- Checks for updates at configurable intervals (30 minutes to 24 hours)
- Works with all enabled package backends (APT, Flatpak, etc.)
- Minimal resource usage when idle

### System Tray Notifications
- **Auto-hiding tray icon**: Only appears when updates are available
- **Click to open**: Left-click launches GUI on Updates page
- **Context menu**: Right-click for quick actions
- **Update count**: Tooltip shows number of available updates

### Independent Operation
- Runs separately from main GUI application
- Continues checking even when GUI is closed
- Survives GUI crashes or restarts
- Automatic restart on failure (via systemd)

## Installation

### Per-User Installation (Recommended for Testing)
Install for current user only (no sudo required):

```bash
bash scripts/install-daemon.sh
```

This installs the daemon to:
- `~/.config/systemd/user/apt-ex-update-checker.service`
- `~/.local/share/apt-ex-package-manager/update_daemon.py`

### System-Wide Installation (For All Users)
Install for all users (requires sudo):

```bash
sudo bash scripts/install-daemon-system.sh
```

This installs the daemon to:
- `/usr/lib/systemd/user/apt-ex-update-checker.service`
- `/usr/lib/systemd/user-preset/90-apt-ex.preset`
- `/usr/share/apt-ex-package-manager/update_daemon.py`

All users will have the daemon automatically enabled on login.

### GUI Installation
You can also install the daemon from the Settings panel:
1. Open Apt-Ex Package Manager
2. Navigate to Settings (⚙️ Settings)
3. Scroll to "Update Notifications" section
4. Click "Install for All Users" or "Install for Me"

## Configuration

### Settings Panel
Configure the daemon from Settings → Update Notifications:

- **Enable automatic update checks**: Toggle background checking on/off
- **Check interval**: Choose how often to check (30 min - 24 hours)
- **Daemon status**: View current daemon state (Running/Stopped)
- **Installation type**: See if installed system-wide or per-user
- **Last check**: View when updates were last checked

### Control Buttons
- **Check Now**: Trigger immediate update check
- **Restart Daemon**: Restart the background service
- **Install for All Users**: System-wide installation (requires sudo)
- **Install for Me**: Per-user installation (no sudo)
- **Uninstall Daemon**: Remove the background service

## Usage

### Tray Icon Behavior

**When Updates Available:**
- Tray icon appears automatically
- Tooltip shows update count (e.g., "5 updates available")
- Icon remains visible until updates are installed

**When No Updates:**
- Tray icon is hidden
- Daemon continues running in background
- Will reappear when new updates are found

### Tray Icon Actions

**Left Click:**
- Launches main GUI application
- Navigates directly to Updates page
- Tray icon remains visible

**Right Click Menu:**
```
┌─────────────────────────────────┐
│ 5 updates available             │ (info)
├─────────────────────────────────┤
│ Open Updates                    │ → Launch GUI
│ Check for Updates Now           │ → Immediate check
├─────────────────────────────────┤
│ Quit Update Checker             │ → Stop daemon
└─────────────────────────────────┘
```

## Systemd Management

### Manual Control
Control the daemon using systemctl:

```bash
# Check status
systemctl --user status apt-ex-update-checker

# Start daemon
systemctl --user start apt-ex-update-checker

# Stop daemon
systemctl --user stop apt-ex-update-checker

# Restart daemon
systemctl --user restart apt-ex-update-checker

# Enable on login
systemctl --user enable apt-ex-update-checker

# Disable on login
systemctl --user disable apt-ex-update-checker

# View logs
journalctl --user -u apt-ex-update-checker -f
```

### Automatic Startup
The daemon is configured to start automatically on user login via systemd.

For system-wide installations, the preset file ensures all users have it enabled by default.

## Logs

### Daemon Logs
The daemon writes logs to:
```
~/.local/share/apt-ex-package-manager/daemon.log
```

View logs:
```bash
tail -f ~/.local/share/apt-ex-package-manager/daemon.log
```

### Systemd Journal
View systemd logs:
```bash
journalctl --user -u apt-ex-update-checker -f
```

## D-Bus Interface

The daemon exposes a D-Bus interface for communication with the GUI:

**Service Name:** `org.aptex.UpdateChecker`  
**Object Path:** `/org/aptex/UpdateChecker`

### Methods
- `CheckNow()` - Trigger immediate update check
- `GetUpdateCount()` - Get current update count
- `GetLastCheckTime()` - Get last check timestamp
- `SetCheckInterval(minutes)` - Change check interval

### Signals
- `UpdatesAvailable(count)` - Emitted when updates found
- `CheckCompleted()` - Emitted when check finishes

## Troubleshooting

### Daemon Not Starting
1. Check if installed:
   ```bash
   systemctl --user list-unit-files | grep apt-ex
   ```

2. Check for errors:
   ```bash
   systemctl --user status apt-ex-update-checker
   journalctl --user -u apt-ex-update-checker -n 50
   ```

3. Verify dependencies:
   ```bash
   python3 -c "import dbus; import PyQt6"
   ```

### Tray Icon Not Appearing
1. Verify updates are available:
   ```bash
   apt list --upgradable
   ```

2. Check daemon is running:
   ```bash
   systemctl --user is-active apt-ex-update-checker
   ```

3. Trigger manual check from Settings panel

### D-Bus Connection Failed
1. Ensure D-Bus session bus is running:
   ```bash
   echo $DBUS_SESSION_BUS_ADDRESS
   ```

2. Check if daemon registered on D-Bus:
   ```bash
   dbus-send --session --print-reply \
     --dest=org.aptex.UpdateChecker \
     /org/aptex/UpdateChecker \
     org.aptex.UpdateChecker.GetUpdateCount
   ```

## Uninstallation

### From GUI
1. Open Settings → Update Notifications
2. Click "Uninstall Daemon"

### From Command Line
```bash
# Stop and disable
systemctl --user stop apt-ex-update-checker
systemctl --user disable apt-ex-update-checker

# Remove user files
rm ~/.config/systemd/user/apt-ex-update-checker.service
rm -rf ~/.local/share/apt-ex-package-manager/

# For system-wide installation (requires sudo)
sudo rm /usr/lib/systemd/user/apt-ex-update-checker.service
sudo rm /usr/lib/systemd/user-preset/90-apt-ex.preset
sudo rm -rf /usr/share/apt-ex-package-manager/

# Reload systemd
systemctl --user daemon-reload
```

## Technical Details

### Resource Usage
- **Idle**: ~20-30 MB RAM
- **During check**: ~50-100 MB RAM (temporary)
- **CPU**: Minimal when idle, brief spike during checks
- **Network**: Only during update checks

### Security
- Runs as user (not root)
- No elevated privileges required
- Package operations still require sudo (via GUI)
- D-Bus session bus only (not system bus)

### Dependencies
- Python 3.8+
- PyQt6
- dbus-python
- systemd (user services)
- python3-apt (for APT backend)

## See Also
- [Implementation Plan](../planning/UPDATE_DAEMON_IMPLEMENTATION.md) - Technical implementation details
- [Settings Documentation](SETTINGS.md) - General settings information
- [Architecture Documentation](../architecture/DATABASE_ARCHITECTURE.md) - System architecture
