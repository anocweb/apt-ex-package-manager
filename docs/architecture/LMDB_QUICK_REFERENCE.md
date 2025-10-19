# LMDB Quick Reference

## Initialization

```python
from cache import LMDBManager, CacheManager

# Initialize LMDB
lmdb = LMDBManager(logging_service=logging_service)

# Create cache manager
cache_mgr = CacheManager(lmdb)
```

## Package Operations

```python
from cache.data_structures import PackageData

# Get package cache
pkg_cache = cache_mgr.get_package_cache('apt')

# Add/Update package
pkg = PackageData(
    package_id='vim',
    name='vim',
    version='9.0.1234',
    description='Vi IMproved',
    section='editors',
    is_installed=True
)
pkg_cache.add_package(pkg)

# Get package
pkg = pkg_cache.get_package('vim')

# Search packages
results = pkg_cache.search_packages('editor')

# Get by section
editors = pkg_cache.get_packages_by_section('editors')

# Get installed
installed = pkg_cache.get_installed_packages()

# Get all with pagination
packages = pkg_cache.get_all_packages(limit=100, offset=0)

# Update install status
pkg_cache.update_installed_status('vim', True)

# Delete package
pkg_cache.delete_package('vim')

# Clear cache
pkg_cache.clear_cache()

# Check validity
if pkg_cache.is_cache_valid(max_age_hours=24):
    # Use cache
    pass
```

## Category Operations

```python
from cache.data_structures import CategoryData

# Get category cache
cat_cache = cache_mgr.get_category_cache('apt')

# Add/Update category
cat = CategoryData(
    name='editors',
    parent=None,
    package_count=42,
    subcategories=['text', 'code']
)
cat_cache.add_category(cat)

# Get category
cat = cat_cache.get_category('editors')

# Get all categories
all_cats = cat_cache.get_all_categories()

# Get root categories
roots = cat_cache.get_root_categories()

# Get subcategories
subcats = cat_cache.get_subcategories('editors')

# Update package count
cat_cache.update_package_count('editors', 45)

# Delete category
cat_cache.delete_category('editors')

# Clear cache
cat_cache.clear_cache()
```

## Direct LMDB Operations

```python
# Put data
lmdb.put('packages_apt', 'vim', {'name': 'vim', 'version': '9.0'})

# Get data
data = lmdb.get('packages_apt', 'vim')

# Delete data
lmdb.delete('packages_apt', 'vim')

# Scan with prefix
results = lmdb.scan('packages_apt', prefix='vim')

# Clear database
lmdb.clear_db('packages_apt')

# Transaction
with lmdb.transaction(write=True) as txn:
    db = lmdb.get_db('packages_apt')
    txn.put(b'key', b'value', db=db)

# Close
lmdb.close()
```

## Data Structures

### PackageData
```python
PackageData(
    package_id: str,           # Required
    name: str,                 # Required
    version: str,              # Required
    description: str,          # Required
    summary: Optional[str],
    section: Optional[str],
    architecture: Optional[str],
    size: Optional[int],
    installed_size: Optional[int],
    maintainer: Optional[str],
    homepage: Optional[str],
    license: Optional[str],
    source_url: Optional[str],
    icon_url: Optional[str],
    is_installed: bool = False,
    metadata: Optional[Dict[str, Any]],
    last_updated: Optional[str]
)
```

### CategoryData
```python
CategoryData(
    name: str,                      # Required
    parent: Optional[str],
    package_count: int = 0,
    subcategories: Optional[List[str]],
    last_updated: Optional[str]
)
```

## Database Paths

### Development
```
apt-qt6-manager/data/cache.lmdb/
```

### Production
```
~/.local/share/apt-ex-package-manager/cache.lmdb/
```

## Named Databases

- `packages_apt` - APT packages
- `packages_flatpak` - Flatpak packages
- `packages_appimage` - AppImage packages
- `categories_apt` - APT categories
- `categories_flatpak` - Flatpak categories
- `categories_appimage` - AppImage categories
- `indexes` - Search indexes
- `metadata` - App metadata

## Index Keys

```
section:{backend}:{section}     # e.g., section:apt:editors
installed:{backend}:1           # e.g., installed:apt:1
```

## Common Patterns

### Bulk Insert
```python
with lmdb.transaction(write=True) as txn:
    db = lmdb.get_db('packages_apt')
    for pkg in packages:
        data = pkg.to_dict()
        txn.put(pkg.package_id.encode(), json.dumps(data).encode(), db=db)
```

### Cursor Iteration
```python
db = lmdb.get_db('packages_apt')
with lmdb.transaction() as txn:
    cursor = txn.cursor(db=db)
    for key, value in cursor:
        pkg_data = json.loads(value.decode())
        # Process package
```

### Prefix Scan
```python
db = lmdb.get_db('packages_apt')
with lmdb.transaction() as txn:
    cursor = txn.cursor(db=db)
    prefix = b'vim'
    if cursor.set_range(prefix):
        for key, value in cursor:
            if not key.startswith(prefix):
                break
            # Process matching packages
```

## Error Handling

```python
try:
    pkg = pkg_cache.get_package('vim')
    if pkg is None:
        # Package not found
        pass
except Exception as e:
    # Handle error
    pass
```

## Performance Tips

1. Use transactions for bulk operations
2. Use indexes for filtered queries
3. Use prefix scans for range queries
4. Close LMDB when done
5. Increase map_size if database grows large

## Cleanup

```python
# Clear all caches
cache_mgr.clear_all_caches()

# Close LMDB
lmdb.close()
```
