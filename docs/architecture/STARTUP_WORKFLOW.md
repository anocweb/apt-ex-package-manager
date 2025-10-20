# Application Startup Workflow

## Overview
This document describes the complete initialization sequence from application launch to fully operational state.

## Startup Sequence

### 1. Entry Point (`main.py`)
```python
main() → QApplication → ApplicationController → app.exec()
```

**Steps:**
1. Parse command-line arguments via `AppConfig.parse_arguments()`
2. Create Qt application instance (`QApplication`)
3. Apply dev outline stylesheet if `--dev-outline` flag set
4. Create `ApplicationController` with app and config
5. Call `app_controller.initialize()`
6. Call `app_controller.show_main_window()`
7. Start Qt event loop with `app.exec()`
8. Cleanup on exit with `app_controller.cleanup()`

**Command-line Options:**
- `--dev-logging` - Enable debug logging
- `--dev-outline` - Show red borders around all widgets
- `--stdout-log-level` - Set console log level

---

### 2. Application Controller Initialization
**File:** `src/controllers/application_controller.py`

**Method:** `initialize()`

**Sequence:**
```
_show_splash() → _setup_theme() → _initialize_services() → _populate_cache() → _create_main_view() → _setup_dev_mode() → _hide_splash()
```

#### 2.1 Splash Screen Display
**Method:** `_show_splash()`

**Creates and displays splash screen:**
- Custom `QSplashScreen` with progress bar
- App logo/icon at top
- Status label for current operation
- Detail label for package counts
- Progress bar (0-100%)
- Stays on top, centered on screen

#### 2.2 Theme Setup
- Create `ThemeService`
- Set application icon
- Register in service container

#### 2.3 Service Initialization
**Order matters** - services depend on each other:

1. **LoggingService**
   - Configure log levels
   - Set up file and console handlers
   - Register in container as `'logging'`

2. **LMDBManager**
   - Initialize LMDB database connection
   - Create/open cache database
   - Register in container as `'lmdb'`

3. **PackageManager**
   - Receives lmdb_manager and logging_service
   - Discovers and registers backend plugins
   - Register in container as `'package_manager'`

#### 2.4 Cache Population
**Method:** `_populate_cache()`

**Synchronous cache update before UI loads:**
1. Check if cache is empty
2. Load all packages from APT
3. Cache packages in batches (100 at a time)
4. Update installed package status
5. Log progress to console

**Why before main view:**
- Ensures data is ready when UI loads
- Prevents empty UI on first launch
- Makes splash screen more valuable (shows during actual work)
- User sees fully populated app immediately

#### 2.5 Main View Creation
- Create `MainView` with injected dependencies:
  - package_manager
  - lmdb_manager
  - logging_service
  - dev_logging flag
  - stdout_log_level

#### 2.6 Dev Mode Setup
- If `--dev-logging` flag set, enable debug features

---

### 3. Package Manager Initialization
**File:** `src/controllers/package_manager.py`

**Constructor:** `__init__(lmdb_manager, logging_service)`

**Sequence:**
1. Store dependencies (lmdb_manager, logging_service)
2. Initialize empty backends dict
3. Set default backend to `'apt'`
4. Create legacy `APTController` for backward compatibility
5. Call `_discover_plugins()`

#### 3.1 Plugin Discovery
**Method:** `_discover_plugins()`

**Plugin Search Paths (in order):**
1. `~/.config/apt-ex-package-manager/plugins/` - User plugins
2. `/usr/share/apt-ex-package-manager/plugins/` - System plugins
3. `src/controllers/plugins/` - Built-in plugins

**For each plugin directory:**
1. Check if directory exists
2. Add to sys.path
3. Scan for `*_plugin.py` files
4. Load module dynamically with `importlib`
5. Find classes inheriting from `BasePackageController`
6. Instantiate plugin with (lmdb_manager, logging_service)
7. Call `register_backend(plugin)`

#### 3.2 Backend Registration
**Method:** `register_backend(controller)`

**Steps:**
1. Call `controller.is_available()` to check system compatibility
2. If available:
   - Add to `backends` dict with `backend_id` as key
   - Log registration success
3. If not available:
   - Log that backend is unavailable
   - Skip registration

**Example:** APTPlugin only registers if `python-apt` is installed.

---

### 4. Main View Initialization
**File:** `src/views/main_view.py`

**Constructor:** `__init__(package_manager, lmdb_manager, logging_service, ...)`

**Sequence:**
```
Store dependencies → Load UI → Setup logging → Load panels → 
Setup navigation → Setup signals → Populate cache → Select home page
```

#### 4.1 Dependency Storage
- Store package_manager, lmdb_manager, logging_service
- Initialize panel dict
- Set dev_logging flag

#### 4.2 UI Loading
- Load `main_window.ui` with `uic.loadUi()`
- Qt Designer file defines window structure
- All UI elements become attributes

#### 4.3 Logging Setup
- Get logger from logging_service
- Pre-register component loggers (odrs, rating_cache, etc.)

#### 4.4 Panel Loading
**Method:** `load_panels()`

**For each panel:**
1. Create `QWidget` instance
2. Load `.ui` file from `src/ui/panels/`
3. Store in `self.panels` dict
4. Add to `contentStack` (QStackedWidget)

**Panels loaded:**
- home
- category
- installed
- updates
- settings
- about

#### 4.5 Navigation Setup
**Method:** `setup_navigation()`

Connect sidebar buttons to page selection:
```python
self.homeBtn.clicked.connect(lambda: self.select_page('home'))
self.installedBtn.clicked.connect(lambda: self.select_page('installed'))
# ... etc
```

#### 4.6 Signal Connections
**Method:** `setup_signals()`

Connect panel-specific signals:
- Search input changes
- Package selection
- Install/remove requests
- Settings changes

#### 4.7 Initial Page Selection
- Call `select_page('home')`
- Display home panel
- Set page title
- Clear context actions

---

### 5. Panel Controller Initialization
**Example:** `HomePanel` (`src/views/panels/home_panel.py`)

**When panel is first accessed:**
1. Panel controller receives dependencies
2. Connects to UI elements in loaded panel widget
3. Sets up panel-specific signals
4. Loads initial data (if needed)

**Panel controllers inherit from `BasePanel`:**
- Standardized initialization
- Common signal patterns
- Shared utility methods

---

### 6. Worker Thread Initialization
**Example:** `CacheUpdateWorker`

**When started:**
1. Create worker instance with parameters
2. Connect signals (finished, error, progress)
3. Call `worker.start()`
4. Worker runs in background thread
5. Emits signals to update UI
6. UI remains responsive

---

#### 2.7 Splash Screen Cleanup
**Method:** `_hide_splash()`

**Closes splash screen:**
- Calls `splash.finish(main_view)`
- Waits for main window to appear
- Smooth transition from splash to main window

---

## Initialization Timeline

```
0ms    main.py entry
       └─ Parse arguments
       └─ Create QApplication

10ms   Show splash screen
       └─ Display with "Starting up..." message
       └─ Progress: 0%

20ms   ApplicationController.initialize()
       └─ ThemeService setup (splash: "Setting up theme...")
       └─ LoggingService init (splash: "Initializing services...")
       └─ LMDBManager init

50ms   PackageManager init
       └─ Discover plugins (splash: "Discovering plugins...")
       └─ Load plugin modules
       └─ Register available backends
       └─ Progress: 5%

100ms  Cache population (BLOCKING - 5-30 seconds)
       └─ Check cache (splash: "Checking cache status...", 10%)
       └─ Load APT packages (splash: "Loading package database...", 15%)
       └─ Cache in batches (splash: "Caching packages...", 15-85%)
       │  └─ Updates: "Cached X / Y packages"
       └─ Update installed status (splash: "Updating installed status...", 90%)
       └─ Progress: 95%

5-30s  MainView init (after cache is ready)
       └─ Load main_window.ui (splash: "Loading user interface...", 98%)
       └─ Load panel UI files
       └─ Setup navigation
       └─ Connect signals
       └─ Progress: 100%

5-30s  Show main window
       └─ Hide splash screen
       └─ Display home panel
       └─ Application ready with full data
```

## Dependency Graph

```
main.py
  └─ ApplicationController
      ├─ ThemeService
      ├─ LoggingService
      ├─ LMDBManager (depends on LoggingService)
      ├─ PackageManager (depends on LMDBManager, LoggingService)
      │   └─ Backend Plugins (APTPlugin, FlatpakPlugin, etc.)
      │       └─ Repositories (APTRepository, etc.)
      └─ MainView (depends on all above)
          ├─ Panel Controllers (HomePanel, InstalledPanel, etc.)
          │   └─ Worker Threads
          └─ Custom Widgets
```

## Critical Initialization Points

### 1. Service Container
All services registered in `ServiceContainer` for dependency injection:
- `'theme'` - ThemeService
- `'logging'` - LoggingService
- `'lmdb'` - LMDBManager
- `'package_manager'` - PackageManager

### 2. Plugin Registration
Only available backends are registered:
- APTPlugin requires `python-apt`
- FlatpakPlugin requires `flatpak` command
- Unavailable backends are skipped

### 3. Cache Updates
Cache is refreshed:
- On every application startup
- When user manually requests refresh
- No TTL - cache persists between sessions

### 4. UI Loading
All UI loaded from `.ui` files:
- No hardcoded layouts
- Qt Designer defines structure
- Runtime loading with `uic.loadUi()`

## Cleanup Sequence

**On application exit:**
1. `app_controller.cleanup()` called
2. Close LMDB database connections
3. Flush logs
4. Qt cleanup
5. Exit process

## Configuration Files

**Loaded during startup:**
- `~/.config/apt-ex-package-manager/` - User settings (QSettings)
- `~/.cache/apt-ex-package-manager/cache.lmdb/` - LMDB database
- `~/.cache/apt-ex-package-manager/apt-ex.log` - Log file

## Error Handling

**During initialization:**
- Missing dependencies → Log warning, skip feature
- Plugin load failure → Log error, continue with other plugins
- Cache error → Log error, operate without cache
- UI file missing → Fatal error, exit application

## Performance Considerations

**Startup timing:**
- Cache population is BLOCKING (5-30 seconds)
- Happens before main window appears
- **Splash screen shows progress during cache loading**
- User sees real-time progress and status updates

**After startup (background threads):**
- Package search across backends
- Update checks
- Package installation/removal
- Manual cache refresh

## Development Mode

**With `--dev-logging` flag:**
- Debug log level enabled
- Additional console output
- Performance timing logged
- Cache operations visible

**With `--dev-outline` flag:**
- Red borders on all widgets
- Visual debugging of layout
- Identify widget boundaries

## Splash Screen

**Design:**
- 500x300 pixels, centered on screen
- Dark background (matches KDE Plasma dark theme)
- App icon/logo at top (64x64)
- App title "Apt-Ex Package Manager"
- Determinate progress bar (0-100%)
- Status label (current operation)
- Detail label (package counts)

**Progress Stages:**
- 0-5%: Starting up
- 5-10%: Initializing services
- 10-15%: Checking cache
- 15-85%: Caching packages (with counts)
- 85-90%: Updating installed status
- 90-98%: Loading UI
- 98-100%: Ready

**User Experience:**
- Always visible during startup
- Shows real progress, not fake animation
- Provides feedback on what's happening
- Smooth transition to main window
