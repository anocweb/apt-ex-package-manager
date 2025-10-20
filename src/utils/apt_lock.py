"""APT lock management to prevent concurrent package operations"""

import fcntl
import os
import time
from typing import Optional

class APTLock:
    """Context manager for APT lock file"""
    
    LOCK_FILE = "/var/lib/dpkg/lock-frontend"
    LOCK_TIMEOUT = 30  # seconds
    
    def __init__(self, timeout: int = LOCK_TIMEOUT, logger=None):
        self.timeout = timeout
        self.logger = logger
        self.lock_fd: Optional[int] = None
        self._locked = False
    
    def __enter__(self):
        """Acquire APT lock"""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release APT lock"""
        self.release()
        return False
    
    def acquire(self) -> bool:
        """Acquire the APT lock with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < self.timeout:
            try:
                self.lock_fd = os.open(self.LOCK_FILE, os.O_RDWR | os.O_CREAT, 0o640)
                fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self._locked = True
                
                if self.logger:
                    self.logger.debug("APT lock acquired")
                return True
                
            except (IOError, OSError) as e:
                if self.lock_fd is not None:
                    os.close(self.lock_fd)
                    self.lock_fd = None
                
                if self.logger:
                    self.logger.debug(f"Waiting for APT lock... ({e})")
                time.sleep(0.5)
        
        if self.logger:
            self.logger.error(f"Failed to acquire APT lock after {self.timeout}s")
        return False
    
    def release(self):
        """Release the APT lock"""
        if self._locked and self.lock_fd is not None:
            try:
                fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                os.close(self.lock_fd)
                self._locked = False
                self.lock_fd = None
                
                if self.logger:
                    self.logger.debug("APT lock released")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error releasing APT lock: {e}")
    
    def is_locked(self) -> bool:
        """Check if we currently hold the lock"""
        return self._locked
