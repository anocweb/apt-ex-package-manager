# APT Section to Category Mapping

## Overview
Apt-Ex Package Manager maps APT package sections to user-friendly sidebar categories to provide an intuitive browsing experience. This document explains how APT sections are organized and mapped to the application's category system.

## APT Section Structure

### Section Format Variations

APT packages use different section naming formats:

#### 1. Simple Sections
Basic category names:
- `games`
- `graphics`
- `net`
- `admin`
- `utils`

#### 2. Repository Component Prefixes
Sections prefixed with repository component (main/universe/multiverse/restricted):
- `universe/games`
- `multiverse/graphics`
- `universe/net`
- `multiverse/admin`

#### 3. Hierarchical Sections
Sections with subcategories:
- `games/action`
- `games/strategy`
- `devel/python`
- `doc/html`

#### 4. Combined Format
Repository component with hierarchical subcategory:
- `universe/games/action`
- `multiverse/devel/python`

## Sidebar Category Mapping

The application maps multiple APT sections to each sidebar category for better organization:

| Sidebar Category | APT Sections | Notes |
|-----------------|--------------|-------|
| **Games** | `games` | |
| **Graphics** | `graphics` | |
| **Internet** | `net`, `web`, `mail` | |
| **Multimedia** | `sound`, `video` | |
| **Office** | `editors`, `text`, `doc` | |
| **Development** | `devel`, `libdevel`, `python`, `perl` | |
| **System** | `admin`, `base`, `kernel`, `shells` | |
| **Utilities** | `utils`, `misc`, `otherosfs` | |
| **Education** | `education`, `science` | |
| **Accessibility** | (none) | No dedicated APT section exists |
| **All** | (all sections) | Special case: all packages |

## Implementation

### Section Discovery
The `get_categories_from_sections()` method scans all packages in the APT cache and collects unique section names:

```python
def get_categories_from_sections(self) -> List[str]:
    """Collect categories from APT sections"""
    cache = apt.Cache()
    sections = set()
    
    for package in cache:
        if hasattr(package.candidate, 'section') and package.candidate.section:
            sections.add(package.candidate.section)
    
    return sorted(list(sections))
```

### Mapping Configuration
The `get_section_to_sidebar_mapping()` method defines the mapping dictionary:

```python
def get_section_to_sidebar_mapping(self) -> dict:
    """Map APT sections to sidebar categories"""
    return {
        'games': ['games'],
        'graphics': ['graphics'],
        'internet': ['net', 'web', 'mail'],
        'multimedia': ['sound', 'video'],
        'office': ['editors', 'text', 'doc'],
        'development': ['devel', 'libdevel', 'python', 'perl'],
        'system': ['admin', 'base', 'kernel', 'shells'],
        'utilities': ['utils', 'misc', 'otherosfs'],
        'education': ['education', 'science'],
        'accessibility': ['accessibility'],
        'all': []  # Special case for all packages
    }
```

### Package Retrieval by Category
The `get_packages_by_sidebar_category()` method retrieves packages for a given sidebar category:

```python
def get_packages_by_sidebar_category(self, sidebar_category: str) -> List[Package]:
    """Get packages for a sidebar category by mapping to APT sections"""
    mapping = self.get_section_to_sidebar_mapping()
    apt_sections = mapping.get(sidebar_category, [])
    
    if sidebar_category == 'all':
        return self.get_installed_packages()
    
    all_packages = []
    for section in apt_sections:
        packages = self.get_packages_by_section(section)
        all_packages.extend(packages)
    
    return all_packages
```

### Hierarchical Section Matching

#### APT Controller Level
The `get_packages_by_section()` method matches both exact sections and hierarchical subsections:

```python
def get_packages_by_section(self, section: str) -> List[Package]:
    """Get packages that belong to a specific APT section (including subsections)"""
    for package in cache:
        if hasattr(package.candidate, 'section') and package.candidate.section:
            pkg_section = package.candidate.section
            # Match exact section or hierarchical subsections
            # e.g., "games" matches both "games" and "games/action"
            if pkg_section == section or pkg_section.startswith(section + '/'):
                packages.append(package)
```

#### Database Cache Level
The package cache model implements comprehensive matching for all section format variations:

```python
def get_counts_by_sections(self, backend: str, sections: List[str]) -> Dict[str, int]:
    """Get package counts including all section format variations"""
    for section in sections:
        cursor = conn.execute('''
            SELECT COUNT(*) FROM package_cache 
            WHERE backend = ? AND (
                section = ? OR           -- Exact: 'games'
                section LIKE ? OR        -- Hierarchical: 'games/action'
                section LIKE ? OR        -- Repository prefix: 'universe/games'
                section LIKE ?           -- Combined: 'universe/games/action'
            )
        ''', (backend, section, f'{section}/%', f'%/{section}', f'%/{section}/%'))
```

```python
def get_summary_by_sections(self, backend: str, sections: List[str]) -> List[PackageSummary]:
    """Get package summaries with comprehensive section matching"""
    for section in sections:
        conditions.append('(p.section = ? OR p.section LIKE ? OR p.section LIKE ? OR p.section LIKE ?)')
        params.extend([section, f'{section}/%', f'%/{section}', f'%/{section}/%'])
```

**Key Behavior**: When searching for section `games`, both methods will match:
- `games` (exact match)
- `games/action` (hierarchical subsection)
- `universe/games` (repository component prefix)
- `multiverse/games` (repository component prefix)
- `universe/games/action` (combined format)

This ensures that all packages in a category appear in the sidebar regardless of repository component or subcategory, and counts are accurate across all Ubuntu repositories (main, universe, multiverse, restricted).

### Section Details with Hierarchy
The `get_section_details()` method parses hierarchical sections:

```python
def get_section_details(self) -> dict:
    """Get section information parsed into hierarchical categories"""
    cache = apt.Cache()
    section_details = {}
    
    for package in cache:
        if hasattr(package.candidate, 'section') and package.candidate.section:
            section = package.candidate.section
            
            if '/' in section:
                # Parse hierarchical sections like "games/action"
                parts = section.split('/', 1)
                main_category = parts[0]
                subcategory = parts[1]
                
                if main_category not in section_details:
                    section_details[main_category] = {}
                if subcategory not in section_details[main_category]:
                    section_details[main_category][subcategory] = 0
                section_details[main_category][subcategory] += 1
            else:
                # Flat section
                if section not in section_details:
                    section_details[section] = 0
                section_details[section] += 1
    
    return section_details
```

## Common APT Sections

### Standard Debian/Ubuntu Sections
- `admin` - System administration utilities
- `base` - Base system packages
- `comm` - Communication programs
- `devel` - Development tools and libraries
- `doc` - Documentation
- `editors` - Text editors
- `electronics` - Electronics applications
- `embedded` - Embedded system packages
- `games` - Games and entertainment
- `gnome` - GNOME desktop environment
- `graphics` - Graphics applications
- `hamradio` - Amateur radio applications
- `interpreters` - Script interpreters
- `kde` - KDE desktop environment
- `kernel` - Linux kernel and modules
- `libdevel` - Development libraries
- `libs` - Runtime libraries
- `mail` - Email clients and servers
- `math` - Mathematics applications
- `misc` - Miscellaneous packages
- `net` - Network applications
- `news` - Newsreaders and servers
- `oldlibs` - Obsolete libraries
- `otherosfs` - Other operating system filesystems
- `perl` - Perl programming language
- `python` - Python programming language
- `science` - Scientific applications
- `shells` - Command shells
- `sound` - Audio applications
- `tex` - TeX typesetting system
- `text` - Text processing utilities
- `utils` - System utilities
- `video` - Video applications
- `web` - Web browsers and servers
- `x11` - X Window System

## Extending the Mapping

### Adding New Categories
To add a new sidebar category:

1. Update the mapping in `get_section_to_sidebar_mapping()`
2. Add the category to the UI sidebar
3. Update this documentation

Example:
```python
'science': ['science', 'math', 'electronics'],
```

### Special Cases

### Accessibility Category
Unlike other categories, APT does not have a dedicated "accessibility" section. Accessibility packages are distributed across multiple sections:
- `admin` - Screen readers (brltty, espeakup)
- `sound` - Speech synthesis (espeak, espeak-ng)
- `misc` - Accessibility tools (at-spi2, a11y-profile-manager)
- `gnome` - GNOME accessibility features

Accessibility packages are typically identified by:
- Package names containing: `a11y`, `accessibility`, `brltty`, `orca`, `espeak`, `speech`, `screen-reader`, `magnifier`, `at-spi`
- Descriptions mentioning: "accessibility", "screen reader", "assistive technology", "speech synthesis"

**Current Implementation**: The accessibility category maps to an empty section list `[]`, resulting in 0 packages shown. A future enhancement could implement keyword-based filtering to populate this category.

### Handling Unmapped Sections
Packages with sections not in the mapping will not appear in category-specific views but will still be available in:
- Search results
- "All" category
- Installed packages view

## Hierarchical Section Behavior

### Automatic Subsection Inclusion
When a sidebar category maps to an APT section, it automatically includes all subsections:

- Mapping `games` includes: `games`, `games/action`, `games/strategy`, `games/arcade`, etc.
- Mapping `devel` includes: `devel`, `devel/python`, `devel/java`, etc.

This hierarchical matching ensures comprehensive category coverage without explicitly listing every subsection.

### Section Prefix Matching
The matching algorithm uses prefix matching with `/` delimiter:
- `games` matches `games` and `games/*`
- `games` does NOT match `gameserver` (requires exact match or `/` separator)

## Best Practices

1. **Keep mappings logical**: Group related APT sections under intuitive sidebar categories
2. **Avoid overlap**: Each APT section should map to only one sidebar category
3. **Consider user expectations**: Use category names familiar to end users
4. **Document changes**: Update this file when modifying the mapping
5. **Test thoroughly**: Verify packages appear in expected categories after changes
6. **Use base sections**: Map to base section names (e.g., `games`) to automatically include all subsections

## Cache Refresh and Updates

### Manual Cache Refresh
Users can manually trigger a cache refresh to update package counts and category data:

1. **From Home Page**: Click the "🔄 Refresh Cache" button in the header context actions
2. **From Category Pages**: Click the "🔄 Refresh Cache" button while browsing any category

The refresh process:
- Clears existing cache data
- Fetches fresh package information from APT
- Updates section counts
- Refreshes category button counts in the sidebar

### Automatic Cache Updates
The cache automatically updates on application startup if:
- Cache is empty (first run)
- Cache has expired (default: 24 hours)
- Cache data is stale

### Implementation

```python
def refresh_cache(self):
    """Force refresh of package cache and category counts"""
    # Force cache refresh
    self.cache_manager.force_refresh('apt')
    
    # Trigger cache update (runs in background thread)
    self.populate_caches_on_startup()
```

The refresh runs asynchronously to prevent UI freezing, with progress indicators showing:
- "Updating package data..."
- "Cached X/Y packages..."
- "Updating section counts..."

After completion, category counts are automatically updated via `update_category_counts()`.

## Future Enhancements

- **Keyword-based category filtering**: Implement accessibility category using package name/description keywords instead of section mapping
- **Dynamic category generation**: Auto-generate categories based on available sections
- **User-customizable mappings**: Allow users to define custom category-to-section mappings
- **Multi-backend unification**: Unified categories across APT + Flatpak + AppImage
- **Subcategory support**: Display hierarchical sections as expandable subcategories in UI
- **Category metadata**: Add icons and descriptions for each category
- **Scheduled cache updates**: Automatic background cache refresh on schedule
- **Section statistics**: Show package distribution across sections in settings
