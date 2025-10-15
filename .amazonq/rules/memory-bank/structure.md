# Apt-Ex Package Manager - Project Structure

## Directory Organization

### Root Structure
```
apt-qt6-manager/
├── src/                    # Application source code
├── docs/                   # Project documentation
├── .amazonq/rules/         # Amazon Q development rules
├── requirements.txt        # Python dependencies
└── README.md              # Project overview
```

### Source Code Architecture (`src/`)
```
src/
├── main.py                 # Application entry point
├── controllers/            # Business logic and package operations
│   ├── package_manager.py  # Unified package management interface
│   ├── apt_controller.py   # APT backend implementation
│   ├── flatpak_controller.py # Flatpak backend implementation
│   └── appimage_controller.py # AppImage backend implementation
├── models/                 # Data structures and state management
│   ├── package_model.py    # Unified package data representation
│   ├── category_model.py   # Category CRUD operations
│   └── package_cache_model.py # Package cache CRUD operations
├── cache/                  # SQLite-based caching system
│   ├── database.py         # Database manager and schema
│   └── category_cache.py   # Category caching interface
├── repositories/           # Repository management
│   ├── base_repository.py  # Repository interface
│   ├── apt_repository.py   # APT repository implementation
│   ├── flatpak_repository.py # Flatpak repository implementation
│   ├── appimage_repository.py # AppImage repository implementation
│   └── repository_manager.py # Multi-repository coordinator
├── settings/               # Application settings
│   └── app_settings.py     # Settings management
├── views/                  # UI display and user interactions
│   └── main_view.py        # Main window (Discover-style)
└── ui/                     # Qt Designer UI files
    ├── main_window.ui      # Main window layout
    ├── category_panel.ui   # Category browsing panel
    ├── category_list_panel.ui # Category tree panel
    └── [other panels].ui   # Additional UI panels
```

### Documentation Structure (`docs/`)
```
docs/
├── FEATURES.md             # Feature requirements and specifications
├── DESIGN_GUIDELINES.md    # KDE Plasma 6 integration guidelines
├── CONTEXT_ACTIONS.md      # Context actions system documentation
├── DATABASE_ARCHITECTURE.md # SQLite database schema and design
├── CACHING_SYSTEM.md       # Caching strategy and implementation
└── REPOSITORY_IMPLEMENTATION.md # Repository management system
```

### Configuration Structure (`.amazonq/rules/`)
```
.amazonq/rules/
├── memory-bank/            # Generated project documentation
├── coding-standards.md     # Python and Qt6 coding standards
├── documentation-standards.md  # Documentation requirements
└── project-guidelines.md   # Development and UI guidelines
```

## Architectural Patterns

### Model-View-Controller (MVC)
- **Models**: Define data structures for packages and system state
- **Views**: Manage UI display and user interactions
- **Controllers**: Handle APT operations and business logic

### Component Relationships
- **Entry Point**: `main.py` initializes the application and main window
- **UI Layer**: Views provide Discover-style interface with cards and overlays
- **Management Layer**: `package_manager.py` coordinates between backends
- **Backend Layer**: Individual controllers handle APT, Flatpak, and AppImage operations
- **Data Layer**: Models provide unified package representation across backends

### Key Design Principles
- Separation of concerns between UI, business logic, and data
- Asynchronous operations to prevent UI blocking
- Secure privilege escalation for system operations
- Efficient caching and state management

## Core Components

### Application Bootstrap
- `main.py`: Application initialization and window creation
- Qt6 application setup and theme integration
- Main event loop and application lifecycle

### User Interface
- `main_view.py`: Primary window implementation
- `main_window.ui`: Qt Designer layout definition
- KDE Plasma 6 theme integration and styling

### Package Management
- `package_manager.py`: Unified interface coordinating all backends
- `apt_controller.py`: APT command execution and section-based categorization
- `flatpak_controller.py`: Flatpak operations and remote management
- `appimage_controller.py`: AppImage integration and file management
- `package_model.py`: Unified package data structures

### Data Management
- `database.py`: SQLite database manager with schema initialization
- `category_model.py`: CRUD operations for category cache
- `package_cache_model.py`: CRUD operations for package cache
- `category_cache.py`: High-level caching interface for categories

### Repository System
- `repository_manager.py`: Multi-backend repository coordinator
- `base_repository.py`: Abstract repository interface
- `apt_repository.py`: APT repository and source management
- `flatpak_repository.py`: Flatpak remote management
- `appimage_repository.py`: AppImage source management

### Configuration Management
- Settings stored in `~/.config/apt-ex-package-manager/`
- Cache database in `~/.cache/apt-ex-package-manager/cache.db`
- Qt6 QSettings for preference management
- System theme and accessibility integration
- SQLite database for persistent caching