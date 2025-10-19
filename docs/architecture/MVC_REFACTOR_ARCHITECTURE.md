# MVC Refactor Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ 1. Parse config (AppConfig)                        │     │
│  │ 2. Create QApplication                             │     │
│  │ 3. Apply dev outline stylesheet (if enabled)       │     │
│  │ 4. Create ApplicationController                    │     │
│  │ 5. Initialize & show                               │     │
│  │ 6. Run event loop                                  │     │
│  │ 7. Cleanup on exit                                 │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              ApplicationController                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Responsibilities:                                  │     │
│  │ • Service initialization order                     │     │
│  │ • Dependency injection                             │     │
│  │ • Application lifecycle management                 │     │
│  │ • Resource cleanup                                 │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  initialize()                                                │
│  ├─> _setup_theme()          → ThemeService                 │
│  ├─> _initialize_services()  → LoggingService               │
│  │                           → LMDBManager                   │
│  │                           → PackageManager                │
│  ├─> _create_main_view()     → MainView (with DI)           │
│  └─> _setup_dev_mode()       → MainView.setup_dev_mode()    │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────────┐  ┌──────────────┐
│ ThemeService │  │ Core Services    │  │  MainView    │
├──────────────┤  ├──────────────────┤  ├──────────────┤
│ • Theme      │  │ • LoggingService │  │ • UI Display │
│   detection  │  │ • LMDBManager    │  │ • User       │
│ • Icon setup │  │ • PackageManager │  │   interaction│
│ • Multi-size │  │                  │  │ • Dev mode   │
│   icons      │  │                  │  │   setup      │
└──────────────┘  └──────────────────┘  └──────────────┘
```

## Data Flow

### Application Startup
```
1. main.py
   └─> AppConfig.parse_arguments()
       └─> Returns: AppConfig(dev_outline, dev_logging, stdout_log_level)

2. main.py
   └─> QApplication(sys.argv)

3. main.py
   └─> ApplicationController(app, config)
       └─> Stores app and config references

4. ApplicationController.initialize()
   ├─> _setup_theme()
   │   └─> ThemeService(app)
   │       ├─> is_dark_theme()
   │       ├─> get_icon_path()
   │       └─> setup_application_icon()
   │
   ├─> _initialize_services()
   │   ├─> LoggingService(stdout_log_level)
   │   ├─> LMDBManager(logging_service)
   │   └─> PackageManager(lmdb_manager, logging_service)
   │
   ├─> _create_main_view()
   │   └─> MainView(package_manager, lmdb_manager, logging_service, ...)
   │
   └─> _setup_dev_mode()
       └─> MainView.setup_dev_mode(dev_logging)
           └─> _open_log_window() [if dev_logging=True]
               └─> _position_log_window()

5. ApplicationController.show_main_window()
   └─> MainView.show()

6. main.py
   └─> app.exec() [Event loop]

7. main.py (finally block)
   └─> ApplicationController.cleanup()
       └─> LMDBManager.close()
```

## Dependency Graph

```
main.py
  │
  ├─> AppConfig (config/)
  │     └─> argparse
  │
  └─> ApplicationController (controllers/)
        │
        ├─> ThemeService (services/)
        │     ├─> QApplication
        │     ├─> QIcon
        │     └─> os
        │
        ├─> LoggingService (services/)
        │
        ├─> LMDBManager (cache/)
        │     └─> LoggingService
        │
        ├─> PackageManager (controllers/)
        │     ├─> LMDBManager
        │     └─> LoggingService
        │
        └─> MainView (views/)
              ├─> PackageManager
              ├─> LMDBManager
              └─> LoggingService
```

## Service Initialization Order

**Critical**: Services must be initialized in this order due to dependencies:

1. **ThemeService** (no dependencies)
   - Sets up application icon
   - Detects theme

2. **LoggingService** (no dependencies)
   - Required by all other services

3. **LMDBManager** (depends on LoggingService)
   - Database connection
   - Cache management

4. **PackageManager** (depends on LMDBManager, LoggingService)
   - Package operations
   - Backend coordination

5. **MainView** (depends on all above)
   - UI display
   - User interaction

## Separation of Concerns

### main.py
- **Responsibility**: Application bootstrap
- **Concerns**: 
  - Parse configuration
  - Create QApplication
  - Apply simple dev stylesheet
  - Delegate to ApplicationController
  - Run event loop
  - Coordinate cleanup

### AppConfig
- **Responsibility**: Configuration management
- **Concerns**:
  - Parse command-line arguments
  - Validate configuration
  - Provide type-safe config access

### ThemeService
- **Responsibility**: Theme and icon management
- **Concerns**:
  - Detect system theme
  - Resolve icon paths
  - Set up application icons

### ApplicationController
- **Responsibility**: Application lifecycle
- **Concerns**:
  - Service initialization order
  - Dependency injection
  - Development mode setup
  - Resource cleanup

### MainView
- **Responsibility**: UI presentation
- **Concerns**:
  - Display UI
  - Handle user interaction
  - Coordinate with services
  - Development mode features

## Benefits of This Architecture

### 1. Testability
Each component can be tested independently:
- **AppConfig**: Test argument parsing with mock sys.argv
- **ThemeService**: Test with mock QApplication
- **ApplicationController**: Test with mock services
- **MainView**: Test with mock package manager

### 2. Maintainability
Clear boundaries between components:
- Configuration logic in AppConfig
- Theme logic in ThemeService
- Lifecycle logic in ApplicationController
- UI logic in MainView

### 3. Extensibility
Easy to add new features:
- New services: Add to ApplicationController._initialize_services()
- New config options: Add to AppConfig dataclass
- New theme features: Add to ThemeService
- New UI features: Add to MainView

### 4. Reusability
Components can be reused:
- ThemeService can be used by other views
- AppConfig can be extended for more options
- ApplicationController pattern can be applied to other apps

## Comparison: Before vs After

### Before (Monolithic main.py)
```python
def main():
    # 67 lines of mixed concerns:
    parser = argparse.ArgumentParser(...)  # Config
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    
    def get_icon_path():  # Theme logic
        # 15 lines of icon detection
    
    try:  # Icon setup
        # 10 lines of icon setup
    
    if args.dev_outline:  # Dev mode
        app.setStyleSheet(...)
    
    # Service instantiation
    logging_service = LoggingService(...)
    lmdb_manager = LMDBManager(...)
    package_manager = PackageManager(...)
    main_view = MainView(...)
    
    if args.dev_logging:  # More dev mode
        # 5 lines of log window setup
    
    main_view.show()
    
    try:
        sys.exit(app.exec())
    finally:
        lmdb_manager.close()
```

### After (Clean Separation)
```python
def main():
    # 20 lines with clear delegation:
    config = AppConfig.parse_arguments()
    app = QApplication(sys.argv)
    
    if config.dev_outline:
        app.setStyleSheet("* { border: 1px solid red; }")
    
    app_controller = ApplicationController(app, config)
    app_controller.initialize()
    app_controller.show_main_window()
    
    try:
        sys.exit(app.exec())
    finally:
        app_controller.cleanup()
```

## Future Enhancements

### ServiceContainer (Optional)
```python
class ServiceContainer:
    def __init__(self):
        self._services = {}
    
    def register(self, name: str, service: Any) -> None:
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        return self._services[name]
```

**Benefits**:
- Centralized service registry
- Easier dependency injection
- Better for testing with mocks

### ViewFactory (Optional)
```python
class ViewFactory:
    def __init__(self, service_container: ServiceContainer):
        self.services = service_container
    
    def create_main_view(self) -> MainView:
        return MainView(
            self.services.get('package_manager'),
            self.services.get('lmdb'),
            logging_service=self.services.get('logging')
        )
```

**Benefits**:
- Consistent view creation
- Easier to add new views
- Testable view construction
