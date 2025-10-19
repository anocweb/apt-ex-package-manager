#!/usr/bin/env python3
"""Test script for LMDB implementation"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from cache.lmdb_manager import LMDBManager
from cache.package_cache import PackageCacheModel
from cache.category_cache import CategoryCacheModel
from cache.data_structures import PackageData, CategoryData

def test_lmdb():
    print("Testing LMDB implementation...")
    
    # Initialize LMDB
    lmdb = LMDBManager()
    print(f"✓ LMDB initialized at: {lmdb.db_path}")
    
    # Test package cache
    pkg_cache = PackageCacheModel(lmdb, 'apt')
    
    # Add test package
    test_pkg = PackageData(
        package_id='test-vim',
        name='vim',
        version='9.0.1234',
        description='Vi IMproved - enhanced vi editor',
        section='editors',
        is_installed=True
    )
    
    success = pkg_cache.add_package(test_pkg)
    print(f"✓ Package added: {success}")
    
    # Retrieve package
    retrieved = pkg_cache.get_package('test-vim')
    print(f"✓ Package retrieved: {retrieved.name} v{retrieved.version}")
    
    # Search packages
    results = pkg_cache.search_packages('vim')
    print(f"✓ Search found {len(results)} package(s)")
    
    # Test category cache
    cat_cache = CategoryCacheModel(lmdb, 'apt')
    
    # Add test category
    test_cat = CategoryData(
        name='editors',
        package_count=42
    )
    
    success = cat_cache.add_category(test_cat)
    print(f"✓ Category added: {success}")
    
    # Retrieve category
    retrieved_cat = cat_cache.get_category('editors')
    print(f"✓ Category retrieved: {retrieved_cat.name} ({retrieved_cat.package_count} packages)")
    
    # Cleanup
    pkg_cache.clear_cache()
    cat_cache.clear_cache()
    print("✓ Cache cleared")
    
    lmdb.close()
    print("✓ LMDB closed")
    
    print("\n✅ All tests passed!")

if __name__ == '__main__':
    try:
        test_lmdb()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
