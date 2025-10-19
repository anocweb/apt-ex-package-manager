# Database Architecture for Apt-Ex Package Manager

> **Status**: ACTIVELY IMPLEMENTING - Replacing SQLite with LMDB
> **Current**: SQLite implementation in src/cache/
> **Migration**: In progress

## LMDB Database Structure

### Multi-Database Layout
```
~/.cache/apt-ex-package-manager/
└── cache.lmdb/
    ├── packages_apt       # APT package metadata
    ├── packages_flatpak   # Flatpak package metadata
    ├── packages_appimage  # AppImage package metadata
    ├── categories_apt     # APT categories
    ├── categories_flatpak # Flatpak categories
    ├── categories_appimage# AppImage categories
    ├── indexes            # Search indexes
    └── metadata           # App metadata (cache version, etc)
```

## Key Naming Conventions

### Package Keys
```
Format: {package_id}
Examples:
  - "vim"                           (APT)
  - "org.gimp.GIMP"                 (Flatpak)
  - "firefox-123.appimage"          (AppImage)
```

### Category Keys
```
Format: {category_name}[:{subcategory}]
Examples:
  - "editors"
  - "games:action"
  - "Development"
```

### Index Keys
```
Format: {index_type}:{value}
Examples:
  - "name:vim"          -> ["vim", "vim-gtk3"]
  - "section:editors"   -> ["vim", "nano", "emacs"]
  - "installed:1"       -> ["vim", "git", "curl"]
```

## Data Serialization

### Package Value Format (JSON)
```json
{
  "name": "vim",
  "version": "9.0.1234",
  "description": "Vi IMproved - enhanced vi editor",
  "summary": "Enhanced vi editor",
  "section": "editors",
  "architecture": "amd64",
  "size": 3145728,
  "installed_size": 12582912,
  "maintainer": "Debian Vim Maintainers",
  "homepage": "https://www.vim.org/",
  "license": "GPL-2",
  "is_installed": true,
  "metadata": {
    "depends": "libc6, libncurses5",
    "priority": "optional"
  }
}
```

### Category Value Format (JSON)
```json
{
  "name": "editors",
  "parent": null,
  "package_count": 42,
  "subcategories": ["text", "code", "hex"]
}
```

### Index Value Format (JSON Array)
```json
["vim", "vim-gtk3", "vim-tiny"]
```

## Operations Mapping

### SQLite → LMDB Translation

#### Create Package
```python
# SQLite
cursor.execute('INSERT INTO package_cache VALUES (?, ?, ...)', data)

# LMDB
with env.begin(write=True, db=packages_apt) as txn:
    txn.put(b'vim', json.dumps(package_data).encode())
```

#### Read Package
```python
# SQLite
cursor.execute('SELECT * FROM package_cache WHERE package_id = ?', (pkg_id,))

# LMDB
with env.begin(db=packages_apt) as txn:
    data = json.loads(txn.get(b'vim').decode())
```

#### Update Package
```python
# SQLite
cursor.execute('UPDATE package_cache SET version = ? WHERE package_id = ?', ...)

# LMDB
with env.begin(write=True, db=packages_apt) as txn:
    data = json.loads(txn.get(b'vim').decode())
    data['version'] = '9.1.0'
    txn.put(b'vim', json.dumps(data).encode())
```

#### Delete Package
```python
# SQLite
cursor.execute('DELETE FROM package_cache WHERE package_id = ?', (pkg_id,))

# LMDB
with env.begin(write=True, db=packages_apt) as txn:
    txn.delete(b'vim')
```

#### Search Packages
```python
# SQLite
cursor.execute('SELECT * FROM package_cache WHERE name LIKE ?', (f'%{query}%',))

# LMDB (using cursor iteration)
results = []
with env.begin(db=packages_apt) as txn:
    cursor = txn.cursor()
    for key, value in cursor:
        pkg = json.loads(value.decode())
        if query.lower() in pkg['name'].lower():
            results.append(pkg)
```

#### Get Packages by Section
```python
# SQLite
cursor.execute('SELECT * FROM package_cache WHERE section = ?', (section,))

# LMDB (using index)
with env.begin(db=indexes) as txn:
    index_key = f'section:{section}'.encode()
    package_ids = json.loads(txn.get(index_key).decode())

with env.begin(db=packages_apt) as txn:
    packages = [json.loads(txn.get(pid.encode()).decode()) for pid in package_ids]
```

## Index Management

### Maintaining Search Indexes

When adding/updating a package, update relevant indexes:

```python
def add_package_with_indexes(env, backend_db, indexes_db, package_id, package_data):
    with env.begin(write=True) as txn:
        # Store package
        txn.put(package_id.encode(), json.dumps(package_data).encode(), db=backend_db)
        
        # Update section index
        section_key = f'section:{package_data["section"]}'.encode()
        section_index = json.loads(txn.get(section_key, db=indexes_db) or b'[]')
        if package_id not in section_index:
            section_index.append(package_id)
            txn.put(section_key, json.dumps(section_index).encode(), db=indexes_db)
        
        # Update installed index
        if package_data.get('is_installed'):
            installed_key = b'installed:1'
            installed_index = json.loads(txn.get(installed_key, db=indexes_db) or b'[]')
            if package_id not in installed_index:
                installed_index.append(package_id)
                txn.put(installed_key, json.dumps(installed_index).encode(), db=indexes_db)
```

## Performance Optimizations

### 1. Prefix Scanning for Categories
```python
# Get all subcategories of "games"
with env.begin(db=categories_apt) as txn:
    cursor = txn.cursor()
    cursor.set_range(b'games')
    categories = []
    for key, value in cursor:
        if not key.decode().startswith('games'):
            break
        categories.append(json.loads(value.decode()))
```

### 2. Batch Operations
```python
# Bulk insert packages
with env.begin(write=True, db=packages_apt) as txn:
    for pkg_id, pkg_data in packages:
        txn.put(pkg_id.encode(), json.dumps(pkg_data).encode())
```

### 3. Read-Only Transactions
```python
# Multiple concurrent reads (no locking)
with env.begin(db=packages_apt, write=False) as txn:
    pkg1 = txn.get(b'vim')
    pkg2 = txn.get(b'emacs')
```

## Migration Strategy

### Phase 1: Parallel Implementation
- Keep SQLite code
- Add LMDB implementation
- Feature flag to switch between them

### Phase 2: Data Migration
```python
def migrate_sqlite_to_lmdb():
    # Read from SQLite
    conn = sqlite3.connect('cache.db')
    cursor = conn.execute('SELECT * FROM package_cache WHERE backend = ?', ('apt',))
    
    # Write to LMDB
    env = lmdb.open('cache.lmdb', max_dbs=10)
    packages_apt = env.open_db(b'packages_apt')
    
    with env.begin(write=True, db=packages_apt) as txn:
        for row in cursor:
            pkg_data = {
                'name': row[3],
                'version': row[4],
                # ... map all fields
            }
            txn.put(row[2].encode(), json.dumps(pkg_data).encode())
    
    conn.close()
    env.close()
```

### Phase 3: Remove SQLite
- Delete SQLite code
- Remove sqlite3 dependency
- Update documentation

## Memory Advantages

### SQLite Issues
- Loads entire result sets into memory
- Query parsing overhead
- Connection pooling overhead
- Index structures in memory

### LMDB Benefits
- Memory-mapped (OS manages memory)
- Zero-copy reads
- No query parsing
- Minimal overhead per transaction
- Automatic memory management

## Backup and Maintenance

### Backup
```python
# LMDB supports hot backups
env.copy('/backup/cache.lmdb')
```

### Compact Database
```python
# LMDB auto-compacts, but can force:
env.copy('/tmp/cache_compact.lmdb', compact=True)
```

### Clear Cache
```python
# Clear specific backend
with env.begin(write=True, db=packages_apt) as txn:
    txn.drop(delete=False)  # Clear all entries, keep database

# Or delete and recreate
with env.begin(write=True) as txn:
    txn.drop(packages_apt, delete=True)
packages_apt = env.open_db(b'packages_apt')
```
