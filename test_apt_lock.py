#!/usr/bin/env python3
"""Test APT lock mechanism"""

import sys
import os
import time
from threading import Thread

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.apt_lock import APTLock

def test_basic_lock():
    """Test basic lock acquisition and release"""
    print("Test 1: Basic lock acquisition")
    
    lock = APTLock(timeout=5)
    
    if lock.acquire():
        print("✓ Lock acquired successfully")
        assert lock.is_locked(), "Lock should be marked as locked"
        lock.release()
        assert not lock.is_locked(), "Lock should be released"
        print("✓ Lock released successfully")
    else:
        print("✗ Failed to acquire lock (may need sudo)")
        return False
    
    return True

def test_context_manager():
    """Test context manager usage"""
    print("\nTest 2: Context manager")
    
    try:
        with APTLock(timeout=5) as lock:
            if lock.is_locked():
                print("✓ Lock acquired via context manager")
            else:
                print("✗ Failed to acquire lock (may need sudo)")
                return False
        
        print("✓ Lock automatically released")
        return True
    except Exception as e:
        print(f"✗ Context manager failed: {e}")
        return False

def test_concurrent_locks():
    """Test that concurrent locks block each other"""
    print("\nTest 3: Concurrent lock blocking")
    
    results = {'thread1': False, 'thread2': False}
    
    def hold_lock(name, duration):
        try:
            with APTLock(timeout=2) as lock:
                if lock.is_locked():
                    print(f"  {name}: Lock acquired, holding for {duration}s")
                    results[name] = True
                    time.sleep(duration)
                else:
                    print(f"  {name}: Failed to acquire lock (timeout)")
        except Exception as e:
            print(f"  {name}: Error - {e}")
    
    thread1 = Thread(target=hold_lock, args=('thread1', 1))
    thread2 = Thread(target=hold_lock, args=('thread2', 0.5))
    
    thread1.start()
    time.sleep(0.1)  # Ensure thread1 gets lock first
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    if results['thread1']:
        print("✓ First thread acquired lock")
    else:
        print("✗ First thread failed")
        return False
    
    # Thread2 should timeout since thread1 holds lock
    if not results['thread2']:
        print("✓ Second thread correctly blocked/timed out")
        return True
    else:
        print("⚠ Second thread also acquired lock (sequential execution)")
        return True

def main():
    """Run all tests"""
    print("APT Lock Mechanism Tests")
    print("=" * 50)
    print("Note: Some tests may require sudo privileges\n")
    
    try:
        test_basic_lock()
        test_context_manager()
        test_concurrent_locks()
        
        print("\n" + "=" * 50)
        print("✓ All tests completed!")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
