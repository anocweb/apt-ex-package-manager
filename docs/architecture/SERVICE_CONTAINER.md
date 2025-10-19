# Service Container Architecture

## Overview
The ServiceContainer provides centralized service registry and dependency injection for the Apt-Ex Package Manager application.

## Purpose
- Centralized service management
- Easier dependency injection
- Better testability with mock services
- Clear service lifecycle management

## Implementation

### ServiceContainer Class
```python
class ServiceContainer:
    def __init__(self):
        self._services = {}
    
    def register(self, name: str, service: Any) -> None
    def get(self, name: str) -> Any
    def has(self, name: str) -> bool
    def get_optional(self, name: str) -> Optional[Any]
    def clear(self) -> None
```

## Usage

### Registering Services
```python
container = ServiceContainer()

# Register services
container.register('logging', logging_service)
container.register('lmdb', lmdb_manager)
container.register('package_manager', package_manager)
```

### Retrieving Services
```python
# Get service (raises KeyError if not found)
logging_service = container.get('logging')

# Check if service exists
if container.has('theme'):
    theme_service = container.get('theme')

# Get optional service (returns None if not found)
optional_service = container.get_optional('optional_feature')
```

### In ApplicationController
```python
class ApplicationController:
    def __init__(self, app: QApplication, config: AppConfig):
        self.container = ServiceContainer()
    
    def _initialize_services(self):
        # Register services in dependency order
        logging_service = LoggingService(...)
        self.container.register('logging', logging_service)
        
        lmdb_manager = LMDBManager(logging_service)
        self.container.register('lmdb', lmdb_manager)
    
    def _create_main_view(self):
        # Inject services from container
        self.main_view = MainView(
            self.container.get('package_manager'),
            self.container.get('lmdb'),
            logging_service=self.container.get('logging')
        )
```

## Benefits

### 1. Centralized Service Management
All services registered in one place, making it easy to see what's available:
```python
# Before (dict)
self.services['logging'] = logging_service
self.services['lmdb'] = lmdb_manager

# After (container)
self.container.register('logging', logging_service)
self.container.register('lmdb', lmdb_manager)
```

### 2. Better Error Handling
Clear error messages when service not found:
```python
# Raises: KeyError: "Service 'missing' not found in container"
service = container.get('missing')
```

### 3. Easier Testing
Mock services easily in tests:
```python
def test_application_controller():
    container = ServiceContainer()
    container.register('logging', MockLoggingService())
    container.register('lmdb', MockLMDBManager())
    
    controller = ApplicationController(app, config)
    controller.container = container  # Inject mock container
    controller.initialize()
```

### 4. Optional Dependencies
Handle optional services gracefully:
```python
# Won't raise error if service doesn't exist
optional_service = container.get_optional('optional_feature')
if optional_service:
    optional_service.do_something()
```

## Service Registration Order

Services must be registered in dependency order:

1. **ThemeService** (no dependencies)
2. **LoggingService** (no dependencies)
3. **LMDBManager** (depends on LoggingService)
4. **PackageManager** (depends on LMDBManager, LoggingService)

```python
def initialize(self):
    self._setup_theme()          # Registers 'theme'
    self._initialize_services()  # Registers 'logging', 'lmdb', 'package_manager'
    self._create_main_view()     # Uses services from container
```

## Registered Services

### Core Services
- `theme`: ThemeService - Theme detection and icon management
- `logging`: LoggingService - Application logging
- `lmdb`: LMDBManager - Database and cache management
- `package_manager`: PackageManager - Package operations

### Future Services
- `odrs`: ODRSService - Package ratings (optional)
- `repository`: RepositoryManager - Repository management (optional)
- `settings`: AppSettings - Application settings (optional)

## Testing Examples

### Unit Test with Mock Services
```python
def test_main_view_with_mocks():
    container = ServiceContainer()
    container.register('package_manager', MockPackageManager())
    container.register('lmdb', MockLMDBManager())
    container.register('logging', MockLoggingService())
    
    main_view = MainView(
        container.get('package_manager'),
        container.get('lmdb'),
        logging_service=container.get('logging')
    )
    
    assert main_view is not None
```

### Integration Test
```python
def test_full_initialization():
    config = AppConfig(dev_outline=False, dev_logging=False, 
                      stdout_log_level='WARNING')
    app = QApplication([])
    
    controller = ApplicationController(app, config)
    controller.initialize()
    
    # Verify all services registered
    assert controller.container.has('theme')
    assert controller.container.has('logging')
    assert controller.container.has('lmdb')
    assert controller.container.has('package_manager')
```

## Best Practices

### 1. Register Early, Use Late
Register all services during initialization, retrieve them when needed:
```python
# Good
def _initialize_services(self):
    self.container.register('logging', LoggingService())
    self.container.register('lmdb', LMDBManager(self.container.get('logging')))

def _create_main_view(self):
    self.main_view = MainView(self.container.get('package_manager'))
```

### 2. Use Type Hints
Add type hints for better IDE support:
```python
def get_logging_service(self) -> LoggingService:
    return self.container.get('logging')
```

### 3. Document Dependencies
Document what services a component needs:
```python
class MainView:
    """
    Main application window.
    
    Dependencies:
    - package_manager: PackageManager
    - lmdb: LMDBManager
    - logging: LoggingService
    """
```

### 4. Cleanup in Reverse Order
Clean up services in reverse order of registration:
```python
def cleanup(self):
    # Cleanup in reverse order
    if self.container.has('package_manager'):
        self.container.get('package_manager').cleanup()
    if self.container.has('lmdb'):
        self.container.get('lmdb').close()
```

## Comparison: Before vs After

### Before (Dict)
```python
class ApplicationController:
    def __init__(self, app, config):
        self.services = {}
    
    def _initialize_services(self):
        self.services['logging'] = LoggingService()
        self.services['lmdb'] = LMDBManager(self.services['logging'])
    
    def cleanup(self):
        if 'lmdb' in self.services:
            self.services['lmdb'].close()
```

### After (ServiceContainer)
```python
class ApplicationController:
    def __init__(self, app, config):
        self.container = ServiceContainer()
    
    def _initialize_services(self):
        self.container.register('logging', LoggingService())
        self.container.register('lmdb', LMDBManager(self.container.get('logging')))
    
    def cleanup(self):
        if self.container.has('lmdb'):
            self.container.get('lmdb').close()
```

## Future Enhancements

### Lazy Loading
```python
def register_lazy(self, name: str, factory: Callable) -> None:
    """Register a service factory for lazy initialization"""
    self._factories[name] = factory

def get(self, name: str) -> Any:
    if name not in self._services and name in self._factories:
        self._services[name] = self._factories[name]()
    return self._services[name]
```

### Service Lifecycle
```python
def register_singleton(self, name: str, service: Any) -> None:
    """Register a singleton service"""
    
def register_transient(self, name: str, factory: Callable) -> None:
    """Register a transient service (new instance each time)"""
```

### Dependency Resolution
```python
def resolve(self, service_class: Type) -> Any:
    """Automatically resolve dependencies"""
    # Inspect constructor, resolve dependencies, create instance
```

## Conclusion

The ServiceContainer provides a clean, testable way to manage application services with:
- Centralized registration
- Clear error messages
- Easy mocking for tests
- Optional dependency support
- Simple, minimal API
