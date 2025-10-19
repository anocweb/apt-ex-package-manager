#!/usr/bin/env python3
"""
Test script for plugin architecture implementation
Run from project root: python test_plugins.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from controllers.package_manager import PackageManager
from cache import LMDBManager

def test_plugin_discovery():
    """Test that plugins are discovered and registered"""
    print("=" * 60)
    print("Testing Plugin Discovery")
    print("=" * 60)
    
    lmdb = LMDBManager()
    pm = PackageManager(lmdb)
    
    backends = pm.get_available_backends()
    print(f"\n✓ Discovered {len(backends)} backend(s): {backends}")
    
    for backend_id in backends:
        backend = pm.get_backend(backend_id)
        print(f"\n  Backend: {backend.display_name} ({backend_id})")
        print(f"  Available: {backend.is_available()}")
        print(f"  Capabilities: {backend.get_capabilities()}")
    
    return pm

def test_backend_operations(pm):
    """Test basic operations through plugin system"""
    print("\n" + "=" * 60)
    print("Testing Backend Operations")
    print("=" * 60)
    
    # Test search
    print("\n1. Testing search_packages()...")
    results = pm.search_packages("test")
    print(f"   ✓ Found {len(results)} packages")
    if results:
        print(f"   Sample: {results[0].name} ({results[0].backend})")
    
    # Test installed packages
    print("\n2. Testing get_installed_packages()...")
    installed = pm.get_installed_packages()
    print(f"   ✓ Found {len(installed)} installed packages")
    if installed:
        print(f"   Sample: {installed[0].name} ({installed[0].backend})")
    
    # Test backend-specific search
    print("\n3. Testing backend-specific search...")
    apt_results = pm.search_packages("test", backend='apt')
    print(f"   ✓ APT search returned {len(apt_results)} packages")

def test_backward_compatibility(pm):
    """Test that old API still works"""
    print("\n" + "=" * 60)
    print("Testing Backward Compatibility")
    print("=" * 60)
    
    print("\n1. Testing old apt_controller access...")
    if hasattr(pm, 'apt_controller'):
        results = pm.apt_controller.search_packages("test")
        print(f"   ✓ Old API works: {len(results)} packages found")
    else:
        print("   ✗ apt_controller not available")

def test_plugin_capabilities():
    """Test capability checking"""
    print("\n" + "=" * 60)
    print("Testing Plugin Capabilities")
    print("=" * 60)
    
    lmdb = LMDBManager()
    pm = PackageManager(lmdb)
    
    for backend_id in pm.get_available_backends():
        backend = pm.get_backend(backend_id)
        caps = backend.get_capabilities()
        
        print(f"\n{backend.display_name}:")
        print(f"  Can search: {'search' in caps}")
        print(f"  Can install: {'install' in caps}")
        print(f"  Can remove: {'remove' in caps}")
        print(f"  Can list installed: {'list_installed' in caps}")
        print(f"  Can list updates: {'list_updates' in caps}")
        print(f"  Has categories: {'categories' in caps}")

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Plugin Architecture Test Suite")
    print("=" * 60)
    
    try:
        pm = test_plugin_discovery()
        test_backend_operations(pm)
        test_backward_compatibility(pm)
        test_plugin_capabilities()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
