# LMDB Migration Guide

## Overview
This document describes the migration from SQLite to LMDB for the Apt-Ex Package Manager cache system.

## Why LMDB?

### Performance Benefits
- **Memory-mapped I/O**: Zero-copy reads, OS manages memory
- **No query parsing**: Direct key-value access
- **Concurrent reads**: Multiple readers without locking
- **Minimal overhead**: Lightweight transactions

### SQLite Limitations
- Loads entire result sets into memory
- Query parsing overhead for simple lookups
- Connection pooling complexity
- Index structures consume memory

## Architecture Changes

### Database Location

**Development Mode** (running from source):
```
apt-qt6-manager/data/cache.lmdb/
```

**Production Mode** (installed):
```
~/.local/share/apt-ex-package-manager/cache.lmdb/
```

### Data Structures

All data is stored as JSON-serialized dictionaries:

- **PackageData**: Package metadata with backend-specific fields
- **CategoryData**: Category hierarchy and package counts
- **IndexData**: Search indexes for fast lookups

### Named Databases

LMDB uses multiple named databases within a single environment:

1. `packages_apt` - APT package cache
2. `packages_flatpak` - Flatpak package cache
3. `packages_appimage` - AppImage package cache
4. `categories_apt` - APT categories
5. `categories_flatpak` - Flatpak categories
6. `categories_appimage` - AppImage categories
7. `indexes` - Search indexes
8. `metadata` - Application metadata

## Code Changes

### Old SQLite Pattern
```python
with connection_manager.connection() as conn:
    cursor = conn.execute('SELECT * FROM package_cache WHERE package_id = ?', (pkg_id,))
    row = cursor.fetchone()
```

### New LMDB Pattern
```python
package_data = lmdb_manager.get('packages_apt', package_id)
package = PackageData.from_dict(package_data)
```

### Indexing

**SQLite**: Automatic indexes on columns
**LMDB**: Manual index management in `indexes` database

Index keys: `{type}:{backend}:{value}`
- `section:apt:editors` → list of package IDs
- `installed:apt:1` → list of installed package IDs

## Migration Steps

### 1. Remove SQLite Files
- Delete `src/cache/database.py`
- Delete `src/cache/connection_manager.py`
- Remove old `src/cache/package_cache.py` and `src/cache/category_cache.py`

### 2. Update Imports
Replace:
```python
from cache.database import DatabaseManager
from cache.connection_manager import SQLiteConnectionManager
```

With:
```python
from cache.lmdb_manager import LMDBManager
from cache.package_cache import PackageCacheModel
from cache.category_cache import CategoryCacheModel
```

### 3. Update Initialization
Replace:
```python
db_manager = DatabaseManager(logging_service=logging_service)
connection_manager = db_manager.connection_manager
```

With:
```python
lmdb_manager = LMDBManager(logging_service=logging_service)
```

### 4. Update Model Usage
Replace:
```python
model = PackageCacheModel(connection_manager)
```

With:
```python
model = PackageCacheModel(lmdb_manager, backend='apt')
```

## Testing

### Verify Database Location
```python
lmdb_manager = LMDBManager()
print(f"Database path: {lmdb_manager.db_path}")
```

### Test Basic Operations
```python
# Add package
pkg = PackageData(
    package_id='vim',
    name='vim',
    version='9.0',
    description='Vi IMproved'
)
cache = PackageCacheModel(lmdb_manager, 'apt')
cache.add_package(pkg)

# Retrieve package
retrieved = cache.get_package('vim')
assert retrieved.name == 'vim'
```

## Performance Expectations

### Memory Usage
- LMDB: ~10-20MB for 50,000 packages
- SQLite: ~50-100MB for same dataset

### Query Speed
- LMDB: <1ms for key lookups
- SQLite: 5-10ms for indexed queries

### Startup Time
- LMDB: Instant (memory-mapped)
- SQLite: 100-200ms (connection + schema)

## Rollback Plan

If issues arise, the old SQLite code is preserved in git history:
```bash
git log --all --full-history -- src/cache/database.py
git checkout <commit> -- src/cache/database.py src/cache/connection_manager.py
```

## Future Enhancements

1. **Compression**: Enable LMDB compression for large descriptions
2. **Replication**: Use LMDB's hot backup for cache snapshots
3. **Sharding**: Split large backends into multiple databases
4. **TTL**: Implement automatic expiration for stale entries
