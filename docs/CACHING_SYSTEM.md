# Caching System

## Overview
The caching system provides fast access to package data and categories by storing frequently accessed information in a local SQLite database.

## Cache Components

### CategoryCache
- **Purpose**: Cache package categories and hierarchies
- **Backend Support**: APT sections, Flatpak categories, AppImage classifications
- **Hierarchy**: Supports parent-child relationships for nested categories

### PackageCache (Future)
- **Purpose**: Cache package metadata and details
- **Metadata**: Flexible key-value storage for backend-specific data
- **Search**: Indexed search by name, description, section

## Cache Lifecycle

### Initialization
1. Database created on first startup
2. Tables created with proper schema
3. Indexes established for performance

### Data Flow
```
UI Request → Cache Check → Fresh Data (if needed) → Cache Store → UI Response
```

### Cache Validation
- **TTL**: 24-hour default expiration
- **Timestamp**: Last updated tracking
- **Invalidation**: Manual refresh available

## Usage Patterns

### Category Browsing
```python
cache = CategoryCache()
categories = cache.get_categories('apt')
if categories is None:
    # Cache miss - fetch fresh data
    controller = APTController()
    categories = controller.get_section_details()
    cache.set_categories('apt', categories)
```

### Cache Management
```python
# Clear specific backend
cache.clear_cache('apt')

# Check cache validity
is_valid = cache.is_cache_valid('apt', max_age_hours=12)

# Force refresh
categories = cache.get_categories('apt')  # Returns None if expired
```

## Backend Integration

### APT Caching
- **Categories**: APT sections with hierarchical parsing
- **Data Source**: `apt.Cache()` and package records
- **Refresh**: On repository updates or manual refresh

### Flatpak Caching (Future)
- **Categories**: Flatpak categories and app classifications
- **Data Source**: Flatpak remotes and app metadata
- **Refresh**: On remote updates

### AppImage Caching (Future)
- **Categories**: AppImage Hub classifications
- **Data Source**: AppImageHub API and local files
- **Refresh**: Periodic or on-demand

## Performance Benefits

### Speed Improvements
- **Database Access**: ~1ms vs ~100ms for fresh data
- **UI Responsiveness**: Instant category display
- **Reduced Load**: Fewer system calls to package managers

### Resource Efficiency
- **Memory**: Minimal RAM usage with SQLite
- **Disk**: Compressed storage with indexing
- **Network**: Reduced API calls to remote sources

## Cache Maintenance

### Automatic Cleanup
- **Expired Data**: Automatic TTL-based expiration
- **Cascade Deletes**: Child records removed with parents
- **Integrity**: Foreign key constraints maintained

### Manual Operations
- **Clear Cache**: Remove all or specific backend data
- **Refresh**: Force update from fresh sources
- **Validate**: Check cache health and consistency