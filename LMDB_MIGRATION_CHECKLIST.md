# LMDB Migration Checklist

## ✅ Completed

- [x] Create LMDB manager (src/cache/lmdb_manager.py)
- [x] Create data structures (src/cache/data_structures.py)
- [x] Create package cache model (src/cache/package_cache.py)
- [x] Create category cache model (src/cache/category_cache.py)
- [x] Create unified cache manager (src/cache/cache_manager.py)
- [x] Update requirements.txt with lmdb dependency
- [x] Create test script (test_lmdb.py)
- [x] Verify LMDB implementation works
- [x] Update cache __init__.py exports
- [x] Create migration documentation
- [x] Update DATABASE_ARCHITECTURE.md

## 🔄 Next Steps

### 1. Remove Old SQLite Files
```bash
rm src/cache/database.py
rm src/cache/connection_manager.py
```

### 2. Update src/main.py
Replace:
```python
from cache.database import DatabaseManager

db_manager = DatabaseManager(logging_service=logging_service)
package_manager = PackageManager(db_manager.connection_manager, logging_service)
main_view = MainView(package_manager, db_manager.connection_manager, ...)
```

With:
```python
from cache import LMDBManager, CacheManager

lmdb_manager = LMDBManager(logging_service=logging_service)
cache_manager = CacheManager(lmdb_manager)
package_manager = PackageManager(cache_manager, logging_service)
main_view = MainView(package_manager, cache_manager, ...)
```

### 3. Update src/controllers/package_manager.py
Replace:
```python
from cache.connection_manager import SQLiteConnectionManager

def __init__(self, connection_manager: SQLiteConnectionManager, logging_service=None):
    self.connection_manager = connection_manager
    self.apt_controller = APTController(connection_manager, logging_service)
```

With:
```python
from cache import CacheManager

def __init__(self, cache_manager: CacheManager, logging_service=None):
    self.cache_manager = cache_manager
    self.apt_controller = APTController(cache_manager, logging_service)
```

### 4. Update src/controllers/apt_controller.py
Replace:
```python
def __init__(self, connection_manager=None, logging_service=None):
    self.connection_manager = connection_manager

def get_installed_packages_list(self, connection_manager, limit: int = None, offset: int = 0):
    model = PackageCacheModel(connection_manager)
```

With:
```python
def __init__(self, cache_manager=None, logging_service=None):
    self.cache_manager = cache_manager

def get_installed_packages_list(self, cache_manager, limit: int = None, offset: int = 0):
    model = cache_manager.get_package_cache('apt')
```

### 5. Update src/models/category_model.py
Replace:
```python
from cache.connection_manager import SQLiteConnectionManager

def __init__(self, connection_manager: SQLiteConnectionManager):
    self.conn_mgr = connection_manager
```

With:
```python
from cache import CategoryCacheModel, LMDBManager

def __init__(self, lmdb_manager: LMDBManager, backend: str = 'apt'):
    self.cache = CategoryCacheModel(lmdb_manager, backend)
```

Then update all methods to use `self.cache` instead of SQL queries.

### 6. Update src/models/package_cache_model.py
This file should be removed or renamed since we now have src/cache/package_cache.py.
If it contains additional logic, merge it into the new package_cache.py.

### 7. Update src/models/rating_cache_model.py
Replace:
```python
from cache.database import DatabaseManager

def __init__(self, connection_manager, logging_service=None):
    self.connection_manager = connection_manager
```

With:
```python
from cache import LMDBManager

def __init__(self, lmdb_manager: LMDBManager, logging_service=None):
    self.lmdb = lmdb_manager
```

Then update methods to use LMDB operations instead of SQL.

### 8. Update src/views/main_view.py
Replace any references to:
```python
db_manager.connection_manager
```

With:
```python
cache_manager
```

### 9. Test Integration
```bash
# Run the application
python src/main.py

# Verify:
# - Package list loads
# - Search works
# - Categories display
# - Install/remove operations work
# - Cache persists between runs
```

### 10. Update Documentation
- Update .amazonq/rules/memory-bank/tech.md
- Update .amazonq/rules/memory-bank/structure.md
- Update .amazonq/rules/memory-bank/guidelines.md

## 📝 Migration Notes

### Key Differences

**SQLite Pattern:**
```python
with connection_manager.connection() as conn:
    cursor = conn.execute('SELECT * FROM package_cache WHERE package_id = ?', (pkg_id,))
    row = cursor.fetchone()
```

**LMDB Pattern:**
```python
cache = cache_manager.get_package_cache('apt')
package = cache.get_package(pkg_id)
```

### Data Structure Changes

**Old (SQLite rows):**
```python
row = (id, backend, package_id, name, version, ...)
```

**New (PackageData objects):**
```python
package = PackageData(
    package_id='vim',
    name='vim',
    version='9.0',
    ...
)
```

### Index Management

**SQLite:** Automatic indexes on columns
**LMDB:** Manual index updates via `_update_indexes()` and `_remove_from_indexes()`

Indexes are automatically maintained when adding/removing packages.

## 🧪 Testing Checklist

After migration, verify:

- [ ] Application starts without errors
- [ ] Package list displays correctly
- [ ] Search functionality works
- [ ] Category browsing works
- [ ] Package details display
- [ ] Install/remove operations work
- [ ] Cache persists between restarts
- [ ] Database location is correct (data/ for dev)
- [ ] No SQLite references remain in code
- [ ] Memory usage is reasonable
- [ ] Performance is acceptable

## 🔧 Troubleshooting

### Database Path Issues
Check: `lmdb_manager.db_path` should be:
- Development: `apt-qt6-manager/data/cache.lmdb`
- Production: `~/.local/share/apt-ex-package-manager/cache.lmdb`

### Import Errors
Ensure lmdb is installed:
```bash
pip install lmdb
```

### Data Not Persisting
Check file permissions on data/ directory and cache.lmdb/ files.

### Performance Issues
Increase map_size in lmdb_manager.py if database grows large:
```python
self.env = lmdb.open(
    self.db_path,
    max_dbs=8,
    map_size=2048 * 1024 * 1024,  # 2GB instead of 1GB
    ...
)
```

## 📚 Reference Documentation

- [LMDB Implementation Summary](docs/architecture/LMDB_IMPLEMENTATION.md)
- [LMDB Migration Guide](docs/architecture/LMDB_MIGRATION.md)
- [Database Architecture](docs/architecture/DATABASE_ARCHITECTURE.md)
