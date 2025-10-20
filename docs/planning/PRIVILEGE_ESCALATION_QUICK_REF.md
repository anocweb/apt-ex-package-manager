# Privilege Escalation Quick Reference

## Overview

Privilege escalation system using PolicyKit + D-Bus helpers to maintain elevated privileges across operations while keeping main application unprivileged.

## Architecture

```
Application (unprivileged) → Plugin → Helper Client → D-Bus → Helper Daemon (root) → System
```

## Key Components

### 1. Base Helper Interface
**Location**: `src/services/privilege/base_helper.py`

```python
class BasePrivilegeHelper(ABC):
    def is_available(self) -> bool
    def install_package(self, package_id: str) -> tuple[bool, str]
    def remove_package(self, package_id: str) -> tuple[bool, str]
    def update_package(self, package_id: str) -> tuple[bool, str]
    def update_all_packages(self) -> tuple[bool, str]
```

### 2. Plugin Integration
**Location**: `src/controllers/base_controller.py`

```python
class BasePackageController(ABC):
    def get_privilege_helper(self) -> Optional[BasePrivilegeHelper]
    def requires_elevation(self, operation: str) -> bool
```

### 3. APT Helper Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Daemon | `/usr/libexec/apt-ex-apt-helper` | Root D-Bus service |
| Client | `src/services/privilege/apt_helper_client.py` | D-Bus client |
| Policy | `/usr/share/polkit-1/actions/org.aptex.APTHelper.policy` | PolicyKit rules |
| D-Bus Config | `/usr/share/dbus-1/system-services/org.aptex.APTHelper.service` | D-Bus registration |
| Systemd | `/usr/lib/systemd/system/apt-ex-apt-helper.service` | Service management |

## Installation

```bash
# Install helper system
./install.sh

# Verify installation
systemctl status apt-ex-apt-helper.service
```

## Usage in Plugins

```python
class APTPlugin(BasePackageController):
    def __init__(self, lmdb_manager=None, logging_service=None):
        self._privilege_helper = APTPrivilegeHelper(logging_service)
    
    def install_package(self, package_name):
        if self._privilege_helper.is_available():
            success, message = self._privilege_helper.install_package(package_name)
            return success
        # Fallback to pkexec
        return self._install_via_pkexec(package_name)
```

## Credential Caching

- **Duration**: 5 minutes (PolicyKit default)
- **Scope**: Per-helper (APT operations share cache)
- **Trigger**: First operation prompts for password
- **Subsequent**: No prompt within cache period

## Fallback Behavior

1. Try privilege helper (D-Bus)
2. If unavailable, fall back to pkexec
3. If pkexec fails, return error

## Security Model

- Main application: **Unprivileged**
- Helper daemon: **Root** (via PolicyKit)
- Communication: **D-Bus** (system bus)
- Authorization: **PolicyKit** (GUI prompts)
- Audit: **PolicyKit logs** all operations

## Testing

```bash
# Unit tests
python tests/test_privilege_helper.py

# Manual test
python -c "
from services.privilege.apt_helper_client import APTPrivilegeHelper
helper = APTPrivilegeHelper()
print('Available:', helper.is_available())
"
```

## Troubleshooting

### Helper not available
```bash
# Check daemon status
systemctl status apt-ex-apt-helper.service

# Check D-Bus registration
dbus-send --system --print-reply \
  --dest=org.freedesktop.DBus \
  /org/freedesktop/DBus \
  org.freedesktop.DBus.ListNames | grep aptex

# Restart daemon
sudo systemctl restart apt-ex-apt-helper.service
```

### Authentication fails
```bash
# Check PolicyKit policy
pkaction --action-id org.aptex.APTHelper.install --verbose

# Test PolicyKit
pkexec /usr/libexec/apt-ex-apt-helper
```

### D-Bus errors
```bash
# Monitor D-Bus
dbus-monitor --system "interface='org.aptex.APTHelper'"

# Check permissions
ls -l /usr/libexec/apt-ex-apt-helper
```

## Backend Comparison

| Backend | Needs Helper | Reason |
|---------|--------------|--------|
| APT | Yes | System packages require root |
| Flatpak | No | Supports user-level installs |
| AppImage | No | No installation required |

## Files Created

```
src/services/privilege/
├── __init__.py
├── base_helper.py
├── apt_helper_daemon.py
└── apt_helper_client.py

polkit/
└── org.aptex.APTHelper.policy

dbus/
└── org.aptex.APTHelper.service

systemd/
└── apt-ex-apt-helper.service

install.sh
uninstall.sh
```

## Dependencies

```
dbus-python
PyGObject
```

## References

- [Full Implementation Plan](PRIVILEGE_ESCALATION_IMPLEMENTATION.md)
- [Plugin Architecture](../architecture/PLUGIN_ARCHITECTURE.md)
- [PolicyKit Documentation](https://www.freedesktop.org/software/polkit/docs/latest/)
