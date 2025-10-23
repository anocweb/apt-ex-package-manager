#!/usr/bin/env python3
"""Test plugin dependency system"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from controllers.package_manager import PackageManager
from cache import LMDBManager
from services.logging_service import LoggingService

def test_plugin_dependencies():
    """Test plugin dependency checking"""
    print("Testing Plugin Dependency System")
    print("=" * 50)
    
    # Setup
    logging_service = LoggingService(stdout_log_level='INFO')
    lmdb_manager = LMDBManager()
    package_manager = PackageManager(lmdb_manager, logging_service)
    
    # Get plugin status
    plugin_status = package_manager.get_plugin_status()
    
    print(f"\nDiscovered {len(plugin_status)} plugin(s):\n")
    
    for backend_id, status in plugin_status.items():
        print(f"Plugin: {status['display_name']} ({backend_id})")
        print(f"  Status: {'✓ Available' if status['available'] else '✗ Unavailable'}")
        print(f"  Capabilities: {', '.join(sorted(status['capabilities']))}")
        
        print(f"  System Dependencies:")
        for dep in status['dependencies']['system']:
            status_icon = '✓' if dep['satisfied'] else '✗'
            version_info = f" v{dep['installed_version']}" if dep['installed_version'] else ""
            print(f"    {status_icon} {dep['name']} ({dep['command']}){version_info}")
        
        print(f"  Python Dependencies:")
        for dep in status['dependencies']['python']:
            status_icon = '✓' if dep['satisfied'] else '✗'
            version_info = f" v{dep['installed_version']}" if dep['installed_version'] else ""
            print(f"    {status_icon} {dep['package']}{version_info}")
        
        if status['missing_dependencies']:
            print(f"  Missing: {', '.join(status['missing_dependencies'])}")
        
        print()
    
    # Test refresh
    print("Testing plugin refresh...")
    package_manager.refresh_plugin_status()
    refreshed_status = package_manager.get_plugin_status()
    print(f"✓ Refreshed, found {len(refreshed_status)} plugin(s)")
    
    print("\n" + "=" * 50)
    print("✓ All plugin dependency tests passed!")

if __name__ == '__main__':
    try:
        test_plugin_dependencies()
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
