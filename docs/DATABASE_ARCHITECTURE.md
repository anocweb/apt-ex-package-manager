# Database Architecture

## Overview
Apt-Ex Package Manager uses SQLite for robust caching of package data and categories across multiple backends (APT, Flatpak, AppImage).

## Database Location
- **Path**: `~/.cache/apt-ex-package-manager/cache.db`
- **Auto-creation**: Database and tables created on first startup
- **Permissions**: User-only access (600)

## Schema Design

### Category Cache Table
```sql
CREATE TABLE category_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backend TEXT NOT NULL,              -- 'apt', 'flatpak', 'appimage'
    name TEXT NOT NULL,                 -- category name
    parent_id INTEGER,                  -- self-referencing for hierarchy
    package_count INTEGER DEFAULT 0,   -- number of packages in category
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES category_cache (id),
    UNIQUE(backend, name, parent_id)
);
```

### Package Cache Table
```sql
CREATE TABLE package_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backend TEXT NOT NULL,              -- package system
    package_id TEXT NOT NULL,           -- unique within backend
    name TEXT NOT NULL,                 -- display name
    version TEXT,                       -- version string
    description TEXT,                   -- full description
    summary TEXT,                       -- short description
    section TEXT,                       -- category/section
    architecture TEXT,                  -- target architecture
    size INTEGER,                       -- download size in bytes
    installed_size INTEGER,             -- installed size in bytes
    maintainer TEXT,                    -- package maintainer
    homepage TEXT,                      -- project homepage
    license TEXT,                       -- software license
    source_url TEXT,                    -- download URL
    icon_url TEXT,                      -- icon/logo URL
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(backend, package_id)
);
```

### Package Metadata Table
```sql
CREATE TABLE package_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_cache_id INTEGER NOT NULL,
    key TEXT NOT NULL,                  -- metadata key
    value TEXT,                         -- metadata value
    FOREIGN KEY (package_cache_id) REFERENCES package_cache (id) ON DELETE CASCADE,
    UNIQUE(package_cache_id, key)
);
```

## Caching Strategy

### Cache Validation
- **Default TTL**: 24 hours for categories and packages
- **Validation**: Automatic timestamp checking
- **Fallback**: Stale data used if fresh fetch fails

### Cache Hierarchy
```
CategoryCache → CategoryModel → DatabaseManager → SQLite
PackageCache → PackageCacheModel → DatabaseManager → SQLite
```

### Cache Operations
- **Cache Hit**: Return cached data if valid
- **Cache Miss**: Fetch fresh data, store in cache
- **Cache Invalidation**: Manual refresh or TTL expiration

## Backend-Specific Data

### APT Metadata Examples
```
depends → "libc6, python3"
conflicts → "old-package"
priority → "optional"
```

### Flatpak Metadata Examples
```
app_id → "org.example.App"
runtime → "org.freedesktop.Platform"
permissions → "network,filesystem"
```

### AppImage Metadata Examples
```
desktop_file → "/path/to/app.desktop"
appstream_url → "https://..."
zsync_url → "https://..."
```

## Performance Considerations

### Indexing
- Primary keys on all tables
- Unique constraints for data integrity
- Foreign key indexes for joins

### Query Optimization
- Prepared statements for repeated queries
- Batch operations for bulk inserts
- Connection pooling via context managers

### Storage Efficiency
- Normalized schema reduces redundancy
- Metadata table handles variable fields
- Cascade deletes maintain referential integrity