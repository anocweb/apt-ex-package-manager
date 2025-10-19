# View Architecture

## Overview
This document describes the refactored view architecture with panel controllers and worker threads.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          MainView                                │
│  (Coordinator - ~400 lines)                                      │
│                                                                   │
│  Responsibilities:                                                │
│  • Load and coordinate panels                                    │
│  • Manage sidebar navigation                                     │
│  • Route signals between panels and controllers                  │
│  • Display context actions                                       │
│  • Manage application-level state                                │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  HomePanel   │ │InstalledPanel│ │UpdatesPanel  │
│              │ │              │ │              │
│ • Search     │ │ • List pkgs  │ │ • Show       │
│ • Featured   │ │ • Remove     │ │   updates    │
│ • Backend    │ │   action     │ │ • Update     │
│   selector   │ │              │ │   actions    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │                │                │
       ▼                ▼                ▼
┌──────────────────────────────────────────────┐
│            BasePanel                          │
│  (Common functionality)                       │
│                                               │
│  • setup_ui()                                 │
│  • connect_signals()                          │
│  • on_show()                                  │
│  • get_context_actions()                      │
│  • get_title()                                │
│                                               │
│  Shared dependencies:                         │
│  • package_manager                            │
│  • lmdb_manager                               │
│  • logging_service                            │
│  • app_settings                               │
└───────────────────┬───────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│CategoryPanel │ │SettingsPanel │ │ AboutPanel   │
│              │ │              │ │              │
│ • Browse by  │ │ • Repos      │ │ • Info       │
│   category   │ │ • Defaults   │ │              │
│ • Virtual    │ │ • ODRS       │ │              │
│   scrolling  │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Worker Thread Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Panel Controllers                         │
│  (HomePanel, InstalledPanel, UpdatesPanel, etc.)                │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Creates and starts workers
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│CacheUpdate   │ │InstalledPkgs │ │UpdateCheck   │
│Worker        │ │Worker        │ │Worker        │
│              │ │              │ │              │
│ • Update     │ │ • Load       │ │ • Check for  │
│   categories │ │   installed  │ │   updates    │
│ • Update     │ │   packages   │ │ • Sort by    │
│   packages   │ │ • Batch      │ │   security   │
│ • Update     │ │   loading    │ │              │
│   installed  │ │              │ │              │
│   status     │ │              │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │ Signals        │ Signals        │ Signals
       │                │                │
       ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Panel Controllers                             │
│  (Receive results via signals and update UI)                    │
└─────────────────────────────────────────────────────────────────┘
```

## Service Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                          Services                                │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │ LoggingService   │  │ StatusService    │  │ ODRSService   │ │
│  │                  │  │                  │  │               │ │
│  │ • App-wide       │  │ • Status bar     │  │ • Ratings     │ │
│  │   logging        │  │   messages       │  │ • Reviews     │ │
│  │ • Named loggers  │  │ • Animations     │  │               │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │ ThemeService     │  │ ServiceContainer │                     │
│  │                  │  │                  │                     │
│  │ • Theme mgmt     │  │ • DI container   │                     │
│  └──────────────────┘  └──────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

## UI File Organization

```
src/ui/
├── windows/              # Main application windows
│   ├── main_window.ui
│   └── main_window_ui.py
│
├── panels/               # Panel layouts
│   ├── home_panel.ui
│   ├── installed_panel.ui
│   ├── updates_panel.ui
│   ├── category_panel.ui
│   ├── category_list_panel.ui
│   ├── settings_panel.ui
│   └── about_panel.ui
│
└── widgets/              # Reusable widget layouts
    ├── package_list_item.ui
    ├── installed_list_item.ui
    └── update_list_item.ui
```

## Data Flow

### User Action Flow
```
User clicks button
       │
       ▼
Sidebar button (MainView)
       │
       ▼
select_page(page_key)
       │
       ▼
Panel.on_show()
       │
       ▼
Panel loads data (possibly via Worker)
       │
       ▼
Panel updates UI
```

### Signal Flow
```
User action in Panel
       │
       ▼
Panel emits signal (e.g., install_requested)
       │
       ▼
MainView receives signal
       │
       ▼
MainView calls PackageManager
       │
       ▼
PackageManager routes to Backend Plugin
       │
       ▼
Backend performs operation
       │
       ▼
Status message shown
```

### Worker Flow
```
Panel needs data
       │
       ▼
Panel creates Worker
       │
       ▼
Panel connects signals
       │
       ▼
Panel starts Worker
       │
       ▼
Worker runs in background
       │
       ├─► progress_signal (optional)
       │
       ├─► finished_signal (success)
       │   └─► Panel.on_data_loaded()
       │
       └─► error_signal (failure)
           └─► Panel.on_error()
```

## Key Design Principles

### 1. Separation of Concerns
- **MainView**: Coordination only
- **Panels**: UI logic and data display
- **Workers**: Background operations
- **Services**: Shared functionality

### 2. Signal-Based Communication
- Panels emit signals for actions
- MainView connects signals to handlers
- Loose coupling between components

### 3. Lifecycle Management
- Panels have clear lifecycle (setup → show → hide)
- Workers are created per operation
- Resources cleaned up properly

### 4. Dependency Injection
- All dependencies passed to panels
- No global state
- Easy to test and mock

### 5. Consistent Patterns
- All panels inherit from BasePanel
- All workers follow same signal pattern
- All UI files organized by type

## Benefits of This Architecture

### Maintainability
- Small, focused files
- Clear responsibilities
- Easy to find code

### Testability
- Panels can be tested independently
- Workers can be tested in isolation
- Mock dependencies easily

### Scalability
- Easy to add new panels
- Easy to add new workers
- Pattern is repeatable

### Readability
- Clear structure
- Consistent patterns
- Self-documenting organization

### Performance
- Workers keep UI responsive
- Lazy loading of panels
- Efficient resource usage

## Migration Path

### Phase 1: Structure (✅ Complete)
- Create directories
- Move UI files
- Create base classes

### Phase 2: Extract (✅ Complete)
- Extract panel controllers
- Extract workers
- Create services

### Phase 3: Refactor (✅ Complete)
- Simplify MainView
- Connect signals
- Update imports

### Phase 4: Test (In Progress)
- Manual testing
- Integration testing
- Fix issues

### Phase 5: Optimize (Future)
- Add unit tests
- Performance tuning
- Documentation updates
