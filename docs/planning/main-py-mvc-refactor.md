# Main.py MVC Architecture Refactor - Implementation Plan

## Overview
Refactor main.py to better align with MVC architecture by extracting business logic, implementing dependency injection, and creating a proper application controller.

## Current Problems
- Business logic (icon theme detection) in entry point
- Direct service instantiation couples main.py to implementations
- View concerns (log window positioning) mixed in bootstrap code
- No central application lifecycle controller
- Configuration parsing mixed with initialization

## Goals
- Pure bootstrap entry point with minimal logic
- Testable, reusable service components
- Clear separation of concerns
- Proper dependency injection
- Centralized application lifecycle management

---

## Phase 1: Extract Services

### Step 1.1: Create IconService
**File**: `src/services/icon_service.py`

**Purpose**: Handle application icon management and theme detection

**Implementation**:
```python
class IconService:
    def __init__(self, app: QApplication):
        self.app = app
        self.base_path = os.path.join(os.path.dirname(__file__), '..', 'icons')
    
    def is_dark_theme(self) -> bool
    def get_icon_path(self) -> str
    def setup_application_icon(self) -> None
```

**Dependencies**: QApplication
**Used by**: ApplicationController

### Step 1.2: Create Config Class
**File**: `src/config/app_config.py`

**Purpose**: Parse and validate application configuration

**Implementation**:
```python
@dataclass
class AppConfig:
    dev_outline: bool
    dev_logging: bool
    stdout_log_level: str
    
    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'AppConfig'
    
    @classmethod
    def parse_arguments(cls) -> 'AppConfig'
```

**Dependencies**: argparse
**Used by**: main.py, ApplicationController

---

## Phase 2: Create Application Controller

### Step 2.1: Implement ApplicationController
**File**: `src/controllers/application_controller.py`

**Purpose**: Coordinate application lifecycle and service initialization

**Implementation**:
```python
class ApplicationController:
    def __init__(self, app: QApplication, config: AppConfig):
        self.app = app
        self.config = config
        self.services = {}
        self.main_view = None
    
    def initialize(self) -> None:
        """Initialize all services and components"""
        self._setup_theme()
        self._initialize_services()
        self._create_main_view()
        self._setup_dev_mode()
    
    def _setup_theme(self) -> None
    def _initialize_services(self) -> None
    def _create_main_view(self) -> None
    def _setup_dev_mode(self) -> None
    
    def show_main_window(self) -> None
    def cleanup(self) -> None
```

**Dependencies**: QApplication, AppConfig, all services
**Used by**: main.py

**Responsibilities**:
- Service initialization order
- Dependency injection to views
- Development mode setup
- Resource cleanup

---

## Phase 3: Move View Logic to Views

### Step 3.1: Add Dev Mode Setup to MainView
**File**: `src/views/main_view.py`

**Add methods**:
```python
def setup_dev_mode(self, dev_logging: bool) -> None:
    """Configure development mode features"""
    if dev_logging:
        self._open_log_window()

def _open_log_window(self) -> None:
    """Open and position log window"""
    from views.log_view import LogView
    self.log_window = LogView(self.logging_service)
    self._position_log_window()
    self.log_window.show()

def _position_log_window(self) -> None:
    """Position log window relative to main window"""
    main_pos = self.pos()
    self.log_window.move(main_pos.x() + 50, main_pos.y() + 50)
```

**Changes**: Move log window logic from main.py to MainView
**Called by**: ApplicationController

---

## Phase 4: Simplify main.py

### Step 4.1: Refactor main() Function
**File**: `src/main.py`

**New implementation**:
```python
def main():
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

**Removed**:
- Icon path detection logic → IconService
- Service instantiation → ApplicationController
- Log window setup → MainView
- Argument parsing details → AppConfig

**Kept**:
- QApplication creation (required at entry point)
- Dev outline stylesheet (simple one-liner)
- Event loop execution
- Cleanup coordination

---

## Phase 5: Optional Enhancements

### Step 5.1: Service Container (Optional)
**File**: `src/services/service_container.py`

**Purpose**: Centralized service registry for dependency injection

**Implementation**:
```python
class ServiceContainer:
    def __init__(self):
        self._services = {}
    
    def register(self, name: str, service: Any) -> None
    def get(self, name: str) -> Any
    def has(self, name: str) -> bool
```

**Benefits**: 
- Easier testing with mock services
- Clearer service dependencies
- Centralized service lifecycle

### Step 5.2: Factory Pattern (Optional)
**File**: `src/factories/view_factory.py`

**Purpose**: Create views with proper dependency injection

**Benefits**:
- Consistent view creation
- Easier to add new views
- Testable view construction

---

## Implementation Order

### Priority 1 (Core Refactor)
1. Create AppConfig class
2. Create IconService
3. Create ApplicationController
4. Move dev mode logic to MainView
5. Refactor main.py

### Priority 2 (Optional Enhancements)
6. Add ServiceContainer
7. Add ViewFactory

---

## Testing Strategy

### Unit Tests Required
- `test_app_config.py`: Argument parsing and validation
- `test_icon_service.py`: Theme detection and icon path resolution
- `test_application_controller.py`: Service initialization order

### Integration Tests
- Full application startup with mocked services
- Cleanup verification
- Dev mode activation

---

## Migration Path

### Step-by-Step Migration
1. **Create new files** without modifying existing code
2. **Add ApplicationController** alongside current main.py logic
3. **Test new implementation** with feature flag
4. **Switch to new implementation** once validated
5. **Remove old code** after confirmation

### Rollback Plan
- Keep original main.py as main_legacy.py during migration
- Use git branches for safe experimentation
- Test thoroughly before removing old code

---

## Benefits Summary

### Testability
- Services can be unit tested independently
- Controllers can be tested with mocked services
- Views can be tested with mocked controllers

### Maintainability
- Clear separation of concerns
- Single responsibility per class
- Easy to locate and modify functionality

### Extensibility
- Easy to add new services
- Simple to modify initialization order
- Straightforward to add configuration options

### Code Quality
- Reduced coupling between components
- Improved cohesion within classes
- Better adherence to SOLID principles

---

## Files to Create
- `src/config/app_config.py`
- `src/services/icon_service.py`
- `src/controllers/application_controller.py`

## Files to Modify
- `src/main.py` (simplify)
- `src/views/main_view.py` (add dev mode methods)

## Files to Test
- `tests/test_app_config.py`
- `tests/test_icon_service.py`
- `tests/test_application_controller.py`
