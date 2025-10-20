# APT Lock Management

## Overview
The APT lock mechanism prevents concurrent package operations that could corrupt the package database or cause conflicts with other package managers.

## Implementation

### Lock File
- **Location**: `/var/lib/dpkg/lock-frontend`
- **Method**: File-based locking using `fcntl.flock()`
- **Scope**: System-wide (prevents all APT operations)

### APTLock Class
Located in `src/utils/apt_lock.py`, provides:

- **Context Manager**: Automatic lock acquisition/release
- **Timeout**: Configurable wait time (default 30s)
- **Non-blocking**: Uses `LOCK_NB` flag to avoid indefinite blocking
- **Logging**: Optional logger integration for debugging

## Usage

### Basic Usage
```python
from utils.apt_lock import APTLock

# Context manager (recommended)
with APTLock(logger=self.logger) as lock:
    if lock.is_locked():
        # Perform APT operation
        apt_cache.commit()
```

### Manual Lock Management
```python
lock = APTLock(timeout=30, logger=self.logger)
if lock.acquire():
    try:
        # Perform operation
        pass
    finally:
        lock.release()
```

### Plugin Integration
The APT plugin automatically uses locks for:
- `install_package()` - Package installation
- `remove_package()` - Package removal
- Future: `update_package()`, `upgrade_all()`

## Behavior

### Lock Acquisition
1. Attempts to open lock file
2. Tries to acquire exclusive lock (non-blocking)
3. If locked by another process, waits 0.5s and retries
4. Continues until timeout or success
5. Returns `True` on success, `False` on timeout

### Lock Release
- Automatically released when context exits
- Releases file lock and closes file descriptor
- Safe to call multiple times

### Concurrent Operations
- Only one process can hold the lock at a time
- Other processes wait or timeout
- Prevents conflicts with:
  - apt/apt-get commands
  - Other package managers (synaptic, aptitude)
  - System updates

## Error Handling

### Permission Errors
Lock file requires write access. Operations may need:
- `sudo` for system-wide operations
- `pkexec` for GUI privilege escalation

### Timeout Errors
If lock cannot be acquired within timeout:
- Returns `False` from `acquire()`
- Logs error message
- Operation should be aborted

### Example Error Handling
```python
with APTLock(timeout=10, logger=self.logger) as lock:
    if not lock.is_locked():
        self.logger.error("Could not acquire APT lock")
        return False
    
    # Safe to proceed
    result = perform_apt_operation()
    return result
```

## Testing

Run the test suite:
```bash
sudo python test_apt_lock.py
```

Tests verify:
- Basic lock acquisition/release
- Context manager functionality
- Concurrent lock blocking

## Security Considerations

- Lock file is system-wide and requires appropriate permissions
- Always use context manager to ensure lock release
- Set reasonable timeouts to avoid indefinite waiting
- Log lock operations for debugging

## Future Enhancements

- [ ] Support for multiple lock files (dpkg, apt archives)
- [ ] Lock status monitoring in UI
- [ ] User notification when waiting for lock
- [ ] Graceful handling of stale locks
