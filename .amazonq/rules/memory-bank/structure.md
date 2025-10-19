# Project Structure

## Directory Organization

```
apt-qt6-manager/
├── src/                    # Application source code
│   ├── cache/             # LMDB caching system
│   ├── config/            # Application configuration
│   ├── controllers/       # Business logic and package management
│   │   └── plugins/       # Backend plugins (APT, Flatpak, etc.)
│   ├── icons/             # Application icons
│   ├── models/            # Data models
│   ├── repositories/      # Data access layer
│   ├── services/          # Shared services (logging, theme, ODRS)
│   ├── settings/          # Settings management
│   ├── ui/                # Qt Designer UI files and generated Python
│   ├── utils/             # Utility functions
│   ├── views/             # View layer (UI controllers)
│   ├── widgets/           # Custom Qt widgets
│   └── main.py            # Application entry point
├── docs/                  # Documentation
│   ├── architecture/      # Architecture documentation
│   ├── developer/         # Developer guides
│   ├── examples/          # Code examples
│   ├── features/          # Feature specifications
│   ├── planning/          # Planning documents
│   └── user-guide/        # User documentation
├── tests/                 # Test files
├── data/                  # Runtime data (LMDB cache)
└── .amazonq/             # Amazon Q AI rules and memory bank
    └── rules/
        └── memory-bank/   # Project memory bank files
```

## Core Components

### Application Layer (`src/`)

#### Entry Point
- **main.py**: Application initialization, Qt setup, main window creation

#### Cache System (`cache/`)
- **lmdb_manager.py**: LMDB database management and operations
- **package_cache.py**: Package data caching with TTL validation
- **category_cache.py**: Category data caching
- **data_structures.py**: Cache data structure definitions

#### Controllers (`controllers/`)
- **application_controller.py**: Main application controller
- **package_manager.py**: Unified package management API, routes to backends
- **apt_controller.py**: Legacy APT controller (now APTPlugin)
- **base_controller.py**: Base controller class
- **plugins/**: Backend plugin implementations
  - Plugin discovery and registration
  - APTPlugin, FlatpakPlugin (stub), etc.

#### Models (`models/`)
- **package_model.py**: Package data model
- **category_model.py**: Category data model
- **package_cache_model.py**: Cache model for packages
- **rating_cache_model.py**: Cache model for ratings

#### Repositories (`repositories/`)
- **repository_manager.py**: Repository management coordinator
- **base_repository.py**: Base repository interface
- **apt_repository.py**: APT repository operations
- **flatpak_repository.py**: Flatpak repository operations
- **appimage_repository.py**: AppImage repository operations

#### Services (`services/`)
- **service_container.py**: Dependency injection container
- **logging_service.py**: Application-wide logging
- **theme_service.py**: Theme and styling management
- **odrs_service.py**: ODRS ratings service integration

#### Views (`views/`)
- **main_view.py**: Main window view controller
- **log_view.py**: Log viewer

#### Widgets (`widgets/`)
- **package_list_item.py**: Package card widget
- **installed_list_item.py**: Installed package item widget
- **update_list_item.py**: Update item widget
- **expandable_item.py**: Expandable UI component
- **virtual_category_container.py**: Virtual scrolling for categories
- **virtual_log_container.py**: Virtual scrolling for logs

#### UI (`ui/`)
- Qt Designer `.ui` files and generated `_ui.py` Python files
- Panels: home, category, installed, updates, settings, about
- List items: package, installed, update

#### Configuration (`config/`, `settings/`)
- **app_config.py**: Application configuration constants
- **app_settings.py**: User settings management (QSettings)

## Architectural Patterns

### MVC Architecture
- **Models**: Data structures and business entities (`models/`)
- **Views**: UI components and user interaction (`views/`, `widgets/`, `ui/`)
- **Controllers**: Business logic and coordination (`controllers/`)

### Repository Pattern
- Abstracts data access from business logic
- Separate repositories for APT, Flatpak, AppImage
- Repository manager coordinates multiple repositories

### Plugin Architecture
- **BasePackageController**: Abstract interface for all backends
- **Plugin Discovery**: Automatic discovery from `plugins/` directory
- **Backend Registration**: Only available backends are registered
- **Capability System**: Plugins declare supported operations
- **Category Mapping**: Plugins map backend categories to standard sidebar categories

### Service Container Pattern
- Centralized dependency injection
- Shared services (logging, theme, ODRS)
- Singleton services accessible throughout application

### Caching Strategy
- **LMDB**: High-performance key-value store
- **TTL Validation**: Time-based cache invalidation
- **Lazy Loading**: Load data on demand
- **Background Updates**: Refresh cache without blocking UI

## Component Relationships

### Data Flow
1. **User Interaction** → Views/Widgets
2. **Views** → Controllers (PackageManager)
3. **PackageManager** → Backend Plugins (APTPlugin, etc.)
4. **Plugins** → Repositories (APTRepository, etc.)
5. **Repositories** → System (APT commands, Flatpak CLI)
6. **Cache Layer** → LMDB (read/write operations)

### Dependency Hierarchy
```
main.py
  └── ApplicationController
      └── MainView
          └── PackageManager
              ├── APTPlugin → APTRepository
              ├── FlatpakPlugin → FlatpakRepository
              └── AppImagePlugin → AppImageRepository
          └── Services (Logging, Theme, ODRS)
          └── Cache (LMDB, PackageCache, CategoryCache)
```

## Key Design Decisions

### Plugin System
- Extensible architecture for multiple package backends
- Plugins inherit from BasePackageController
- Automatic discovery and registration
- Capability-based feature detection

### LMDB Caching
- Chosen for high performance and reliability
- Eliminates slow APT cache parsing on every launch
- TTL-based invalidation ensures fresh data
- Persistent across application restarts

### Qt6 and KDE Integration
- PyQt6 for modern Python Qt bindings
- Native KDE Plasma 6 styling
- Qt Designer for UI layout
- QSettings for cross-platform settings storage

### Context Actions System
- Dynamic header buttons that change per page
- Cleaner interface than static toolbar
- Page-specific operations (Refresh, Update All, etc.)

## Configuration and Data

### Settings Location
- `~/.config/apt-ex-package-manager/` - User settings and configuration

### Cache Location
- `data/cache.lmdb/` - LMDB database files (data.mdb, lock.mdb)

### Log Files
- Configured in logging_service.py
- Console and file logging support
