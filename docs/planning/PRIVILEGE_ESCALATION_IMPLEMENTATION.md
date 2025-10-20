# Privilege Escalation Implementation Plan

> **Status**: PLANNED  
> **Priority**: HIGH  
> **Estimated Effort**: 2-3 weeks  
> **Dependencies**: Plugin architecture (existing)

## Problem Statement

Currently, each package operation (install/remove/update) requires separate privilege escalation via `pkexec`, forcing users to authenticate multiple times for batch operations. This creates poor UX when:
- Installing multiple packages sequentially
- Updating multiple packages
- Performing install → remove → update operations in succession

## Solution Overview

Implement **PolicyKit-based privilege helper daemons** that maintain elevated privileges across operations while keeping the main application unprivileged. Each backend plugin manages its own privilege helper.

### Architecture

```
Main Application (Unprivileged)
    ↓
PackageManager
    ↓
Backend Plugins (Unprivileged)
    ↓
Privilege Helpers (D-Bus Services, Root)
    ↓
System Package Managers (apt-get, flatpak, etc.)
```

## Implementation Phases

### Phase 1: Privilege Helper Infrastructure (Week 1)

#### 1.1 Create Base Helper Interface

**File**: `src/services/privilege/base_helper.py`

```python
from abc import ABC, abstractmethod
from typing import Optional

class BasePrivilegeHelper(ABC):
    """Abstract interface for privilege escalation helpers"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if helper is available and running"""
        pass
    
    @abstractmethod
    def install_package(self, package_id: str) -> tuple[bool, str]:
        """Install package, returns (success, message)"""
        pass
    
    @abstractmethod
    def remove_package(self, package_id: str) -> tuple[bool, str]:
        """Remove package, returns (success, message)"""
        pass
    
    @abstractmethod
    def update_package(self, package_id: str) -> tuple[bool, str]:
        """Update package, returns (success, message)"""
        pass
    
    @abstractmethod
    def update_all_packages(self) -> tuple[bool, str]:
        """Update all packages, returns (success, message)"""
        pass
```

#### 1.2 Create Directory Structure

```bash
mkdir -p src/services/privilege
touch src/services/privilege/__init__.py
touch src/services/privilege/base_helper.py
```

#### 1.3 Update BasePackageController

**File**: `src/controllers/base_controller.py`

Add optional methods:

```python
def get_privilege_helper(self) -> Optional[BasePrivilegeHelper]:
    """Return privilege helper client for this backend (optional)"""
    return None

def requires_elevation(self, operation: str) -> bool:
    """Check if operation requires privilege elevation"""
    return False
```

**Deliverables:**
- [ ] `base_helper.py` created with interface
- [ ] Directory structure created
- [ ] `BasePackageController` updated with helper methods
- [ ] Unit tests for base interface

---

### Phase 2: APT Privilege Helper (Week 1-2)

#### 2.1 Create APT Helper Daemon (D-Bus Service)

**File**: `src/services/privilege/apt_helper_daemon.py`

```python
#!/usr/bin/env python3
"""APT privilege helper daemon - runs as root via PolicyKit"""

import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import subprocess

class APTHelperService(dbus.service.Object):
    """D-Bus service for privileged APT operations"""
    
    DBUS_NAME = 'org.aptex.APTHelper'
    DBUS_PATH = '/org/aptex/APTHelper'
    
    def __init__(self):
        bus = dbus.SystemBus()
        bus_name = dbus.service.BusName(self.DBUS_NAME, bus)
        super().__init__(bus_name, self.DBUS_PATH)
    
    @dbus.service.method('org.aptex.APTHelper', in_signature='s', out_signature='bs')
    def InstallPackage(self, package_name):
        """Install package via apt-get"""
        try:
            result = subprocess.run(
                ['apt-get', 'install', '-y', package_name],
                capture_output=True, text=True, timeout=300
            )
            return (result.returncode == 0, result.stdout + result.stderr)
        except Exception as e:
            return (False, str(e))
    
    @dbus.service.method('org.aptex.APTHelper', in_signature='s', out_signature='bs')
    def RemovePackage(self, package_name):
        """Remove package via apt-get"""
        try:
            result = subprocess.run(
                ['apt-get', 'remove', '-y', package_name],
                capture_output=True, text=True, timeout=300
            )
            return (result.returncode == 0, result.stdout + result.stderr)
        except Exception as e:
            return (False, str(e))
    
    @dbus.service.method('org.aptex.APTHelper', in_signature='s', out_signature='bs')
    def UpdatePackage(self, package_name):
        """Update package via apt-get"""
        try:
            result = subprocess.run(
                ['apt-get', 'install', '--only-upgrade', '-y', package_name],
                capture_output=True, text=True, timeout=300
            )
            return (result.returncode == 0, result.stdout + result.stderr)
        except Exception as e:
            return (False, str(e))
    
    @dbus.service.method('org.aptex.APTHelper', in_signature='', out_signature='bs')
    def UpdateAllPackages(self):
        """Update all packages via apt-get"""
        try:
            result = subprocess.run(
                ['apt-get', 'upgrade', '-y'],
                capture_output=True, text=True, timeout=600
            )
            return (result.returncode == 0, result.stdout + result.stderr)
        except Exception as e:
            return (False, str(e))

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    service = APTHelperService()
    loop = GLib.MainLoop()
    loop.run()
```

#### 2.2 Create PolicyKit Policy File

**File**: `polkit/org.aptex.APTHelper.policy`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
 "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig>
  <vendor>Apt-Ex Package Manager</vendor>
  <vendor_url>https://github.com/anocweb/apt-ex-package-manager</vendor_url>
  
  <action id="org.aptex.APTHelper.install">
    <description>Install packages</description>
    <message>Authentication is required to install packages</message>
    <defaults>
      <allow_any>auth_admin</allow_any>
      <allow_inactive>auth_admin</allow_inactive>
      <allow_active>auth_admin_keep</allow_active>
    </defaults>
    <annotate key="org.freedesktop.policykit.exec.path">/usr/libexec/apt-ex-apt-helper</annotate>
  </action>
  
  <action id="org.aptex.APTHelper.remove">
    <description>Remove packages</description>
    <message>Authentication is required to remove packages</message>
    <defaults>
      <allow_any>auth_admin</allow_any>
      <allow_inactive>auth_admin</allow_inactive>
      <allow_active>auth_admin_keep</allow_active>
    </defaults>
  </action>
  
  <action id="org.aptex.APTHelper.update">
    <description>Update packages</description>
    <message>Authentication is required to update packages</message>
    <defaults>
      <allow_any>auth_admin</allow_any>
      <allow_inactive>auth_admin</allow_inactive>
      <allow_active>auth_admin_keep</allow_active>
    </defaults>
  </action>
</policyconfig>
```

**Key**: `auth_admin_keep` enables credential caching (default 5 minutes)

#### 2.3 Create D-Bus Service Configuration

**File**: `dbus/org.aptex.APTHelper.service`

```ini
[D-BUS Service]
Name=org.aptex.APTHelper
Exec=/usr/libexec/apt-ex-apt-helper
User=root
SystemdService=apt-ex-apt-helper.service
```

#### 2.4 Create Systemd Service

**File**: `systemd/apt-ex-apt-helper.service`

```ini
[Unit]
Description=Apt-Ex APT Privilege Helper
Documentation=https://github.com/anocweb/apt-ex-package-manager

[Service]
Type=dbus
BusName=org.aptex.APTHelper
ExecStart=/usr/libexec/apt-ex-apt-helper
Restart=on-failure
```

#### 2.5 Create APT Helper Client

**File**: `src/services/privilege/apt_helper_client.py`

```python
"""APT privilege helper client - D-Bus client for main application"""

import dbus
from .base_helper import BasePrivilegeHelper
from typing import Optional

class APTPrivilegeHelper(BasePrivilegeHelper):
    """D-Bus client for APT privilege helper"""
    
    DBUS_NAME = 'org.aptex.APTHelper'
    DBUS_PATH = '/org/aptex/APTHelper'
    DBUS_INTERFACE = 'org.aptex.APTHelper'
    
    def __init__(self, logging_service=None):
        self.logger = logging_service.get_logger('apt_helper') if logging_service else None
        self._bus = None
        self._proxy = None
        self._connect()
    
    def _connect(self):
        """Connect to D-Bus service"""
        try:
            self._bus = dbus.SystemBus()
            self._proxy = self._bus.get_object(self.DBUS_NAME, self.DBUS_PATH)
        except dbus.exceptions.DBusException as e:
            if self.logger:
                self.logger.warning(f"APT helper not available: {e}")
            self._proxy = None
    
    def is_available(self) -> bool:
        """Check if helper is available"""
        return self._proxy is not None
    
    def install_package(self, package_id: str) -> tuple[bool, str]:
        """Install package via helper"""
        if not self.is_available():
            return (False, "Helper not available")
        
        try:
            interface = dbus.Interface(self._proxy, self.DBUS_INTERFACE)
            success, message = interface.InstallPackage(package_id)
            return (bool(success), str(message))
        except dbus.exceptions.DBusException as e:
            return (False, f"D-Bus error: {e}")
    
    def remove_package(self, package_id: str) -> tuple[bool, str]:
        """Remove package via helper"""
        if not self.is_available():
            return (False, "Helper not available")
        
        try:
            interface = dbus.Interface(self._proxy, self.DBUS_INTERFACE)
            success, message = interface.RemovePackage(package_id)
            return (bool(success), str(message))
        except dbus.exceptions.DBusException as e:
            return (False, f"D-Bus error: {e}")
    
    def update_package(self, package_id: str) -> tuple[bool, str]:
        """Update package via helper"""
        if not self.is_available():
            return (False, "Helper not available")
        
        try:
            interface = dbus.Interface(self._proxy, self.DBUS_INTERFACE)
            success, message = interface.UpdatePackage(package_id)
            return (bool(success), str(message))
        except dbus.exceptions.DBusException as e:
            return (False, f"D-Bus error: {e}")
    
    def update_all_packages(self) -> tuple[bool, str]:
        """Update all packages via helper"""
        if not self.is_available():
            return (False, "Helper not available")
        
        try:
            interface = dbus.Interface(self._proxy, self.DBUS_INTERFACE)
            success, message = interface.UpdateAllPackages()
            return (bool(success), str(message))
        except dbus.exceptions.DBusException as e:
            return (False, f"D-Bus error: {e}")
```

#### 2.6 Update APTPlugin

**File**: `src/controllers/plugins/apt_plugin.py`

```python
from services.privilege.apt_helper_client import APTPrivilegeHelper

class APTPlugin(BasePackageController):
    def __init__(self, lmdb_manager=None, logging_service=None):
        # ... existing init ...
        self._privilege_helper = APTPrivilegeHelper(logging_service)
    
    def get_privilege_helper(self):
        return self._privilege_helper
    
    def requires_elevation(self, operation: str) -> bool:
        return operation in ['install', 'remove', 'update', 'update_all']
    
    def install_package(self, package_name):
        # Try helper first, fallback to pkexec
        if self._privilege_helper.is_available():
            success, message = self._privilege_helper.install_package(package_name)
            if success:
                self._update_cache(package_name, True)
            return success
        
        # Fallback to existing pkexec method
        return self._install_via_pkexec(package_name)
    
    def _install_via_pkexec(self, package_name):
        """Existing pkexec implementation as fallback"""
        # ... existing code ...
```

**Deliverables:**
- [ ] APT helper daemon created
- [ ] PolicyKit policy file created
- [ ] D-Bus service configuration created
- [ ] Systemd service file created
- [ ] APT helper client created
- [ ] APTPlugin updated to use helper
- [ ] Fallback to pkexec maintained
- [ ] Integration tests

---

### Phase 3: Installation & Packaging (Week 2)

#### 3.1 Update Installation Script

**File**: `install.sh` (create if doesn't exist)

```bash
#!/bin/bash
set -e

# Install PolicyKit policy
sudo install -Dm644 polkit/org.aptex.APTHelper.policy \
    /usr/share/polkit-1/actions/org.aptex.APTHelper.policy

# Install D-Bus service
sudo install -Dm644 dbus/org.aptex.APTHelper.service \
    /usr/share/dbus-1/system-services/org.aptex.APTHelper.service

# Install systemd service
sudo install -Dm644 systemd/apt-ex-apt-helper.service \
    /usr/lib/systemd/system/apt-ex-apt-helper.service

# Install helper daemon
sudo install -Dm755 src/services/privilege/apt_helper_daemon.py \
    /usr/libexec/apt-ex-apt-helper

# Reload systemd
sudo systemctl daemon-reload

echo "Privilege helper installed successfully"
echo "The helper will start automatically when needed"
```

#### 3.2 Update requirements.txt

```
PyQt6
apt
lmdb
dbus-python
PyGObject
```

#### 3.3 Create Uninstall Script

**File**: `uninstall.sh`

```bash
#!/bin/bash
set -e

# Stop service if running
sudo systemctl stop apt-ex-apt-helper.service 2>/dev/null || true

# Remove files
sudo rm -f /usr/share/polkit-1/actions/org.aptex.APTHelper.policy
sudo rm -f /usr/share/dbus-1/system-services/org.aptex.APTHelper.service
sudo rm -f /usr/lib/systemd/system/apt-ex-apt-helper.service
sudo rm -f /usr/libexec/apt-ex-apt-helper

# Reload systemd
sudo systemctl daemon-reload

echo "Privilege helper uninstalled successfully"
```

**Deliverables:**
- [ ] Installation script created
- [ ] Uninstall script created
- [ ] requirements.txt updated
- [ ] Installation tested on clean system
- [ ] Uninstallation tested

---

### Phase 4: Testing & Documentation (Week 3)

#### 4.1 Create Test Suite

**File**: `tests/test_privilege_helper.py`

```python
#!/usr/bin/env python3
"""Test privilege helper functionality"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.privilege.apt_helper_client import APTPrivilegeHelper

class TestPrivilegeHelper(unittest.TestCase):
    def setUp(self):
        self.helper = APTPrivilegeHelper()
    
    def test_helper_available(self):
        """Test helper availability"""
        # Should be available if daemon is running
        available = self.helper.is_available()
        self.assertIsInstance(available, bool)
    
    def test_install_package(self):
        """Test package installation"""
        if not self.helper.is_available():
            self.skipTest("Helper not available")
        
        # Test with small package
        success, message = self.helper.install_package('cowsay')
        self.assertTrue(success, f"Installation failed: {message}")
    
    def test_remove_package(self):
        """Test package removal"""
        if not self.helper.is_available():
            self.skipTest("Helper not available")
        
        success, message = self.helper.remove_package('cowsay')
        self.assertTrue(success, f"Removal failed: {message}")

if __name__ == '__main__':
    unittest.main()
```

#### 4.2 Update Documentation

Update the following files:
- `docs/architecture/PLUGIN_ARCHITECTURE.md` - Add privilege helper section
- `docs/plugins/apt/README.md` - Document APT helper
- `README.md` - Update installation instructions
- `docs/developer/DEVELOPMENT.md` - Add helper development guide

**Deliverables:**
- [ ] Test suite created
- [ ] All tests passing
- [ ] Documentation updated
- [ ] User guide updated with installation steps

---

### Phase 5: Future Backends (Optional)

#### 5.1 Flatpak Helper (If Needed)

Flatpak supports user-level installations, so privilege helper may not be needed. If system-level installations are required:

**File**: `src/services/privilege/flatpak_helper_daemon.py`

Similar structure to APT helper, but for Flatpak operations.

#### 5.2 Generic Helper Template

Create template for future backends:

**File**: `docs/developer/PRIVILEGE_HELPER_TEMPLATE.md`

Template and guide for creating privilege helpers for new backends.

---

## Security Considerations

### PolicyKit Security
- **auth_admin_keep**: Caches credentials for 5 minutes (PolicyKit default)
- **Fine-grained permissions**: Separate actions for install/remove/update
- **Audit trail**: All operations logged by PolicyKit
- **User confirmation**: PolicyKit shows GUI prompt on first operation

### D-Bus Security
- **System bus**: Uses system D-Bus (more secure than session bus)
- **PolicyKit integration**: All methods protected by PolicyKit
- **No password storage**: Application never handles passwords
- **Process isolation**: Helper runs as separate root process

### Fallback Security
- **Graceful degradation**: Falls back to pkexec if helper unavailable
- **No privilege escalation**: Main app remains unprivileged
- **Timeout protection**: Operations have timeouts to prevent hanging

## Testing Strategy

### Unit Tests
- Helper availability detection
- D-Bus communication
- Error handling
- Fallback behavior

### Integration Tests
- Install → Remove → Update sequence
- Multiple operations without re-authentication
- Credential cache expiration
- Fallback to pkexec

### Manual Tests
- First operation (authentication prompt)
- Second operation within 5 minutes (no prompt)
- Operation after 5 minutes (new prompt)
- Helper daemon crash recovery
- System without PolicyKit

## Rollout Plan

### Phase 1: Development (Week 1-2)
- Implement helper infrastructure
- Create APT helper
- Test on development machine

### Phase 2: Testing (Week 2-3)
- Internal testing
- Test on multiple distributions
- Test edge cases

### Phase 3: Documentation (Week 3)
- Update all documentation
- Create installation guide
- Create troubleshooting guide

### Phase 4: Release (Week 3+)
- Release as optional feature
- Gather user feedback
- Fix issues
- Make default in future release

## Success Criteria

- [ ] User authenticates once for multiple operations
- [ ] Credential cache works for 5 minutes
- [ ] Fallback to pkexec works when helper unavailable
- [ ] No security regressions
- [ ] Installation documented and tested
- [ ] Works on Ubuntu, Debian, KDE Neon
- [ ] Helper daemon stable (no crashes)
- [ ] Performance equivalent to pkexec

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PolicyKit not available | High | Fallback to pkexec |
| D-Bus communication failure | Medium | Retry logic, fallback |
| Helper daemon crashes | Medium | Systemd auto-restart |
| Security vulnerability | High | Code review, minimal permissions |
| Distribution compatibility | Medium | Test on multiple distros |
| User confusion | Low | Clear documentation |

## Future Enhancements

- **Progress reporting**: Stream operation progress via D-Bus signals
- **Batch operations**: Single method for multiple packages
- **Transaction support**: Rollback on failure
- **Notification integration**: Desktop notifications for operations
- **Settings integration**: Configure cache timeout
- **Multiple helpers**: Support alternative privilege escalation methods

## References

- [PolicyKit Documentation](https://www.freedesktop.org/software/polkit/docs/latest/)
- [D-Bus Tutorial](https://dbus.freedesktop.org/doc/dbus-tutorial.html)
- [KDE Discover Implementation](https://invent.kde.org/plasma/discover)
- [GNOME Software Implementation](https://gitlab.gnome.org/GNOME/gnome-software)
