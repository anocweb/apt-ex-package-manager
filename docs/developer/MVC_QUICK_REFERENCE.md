# MVC Architecture Quick Reference

## Overview
This guide provides quick reference for working with the refactored MVC architecture.

## Key Components

### 1. AppConfig (`src/config/app_config.py`)
**Purpose**: Application configuration from command-line arguments

```python
from config.app_config import AppConfig

# Parse arguments
config = AppConfig.parse_arguments()

# Access configuration
if config.dev_outline:
    # Enable dev outline
if config.dev_logging:
    # Enable dev logging
log_level = config.stdout_log_level
```

**Adding New Config Options**:
```python
@dataclass
class AppConfig:
    dev_outline: bool
    dev_logging: bool
    stdout_log_level: str
    new_option: str  # Add here
    
    @classmethod
    def parse_arguments(cls) -> 'AppConfig':
        parser = argparse.ArgumentParser(...)
        parser.add_argument('--new-option', ...)  # Add here
        args = parser.parse_args()
        return cls.from_args(args)
```

### 2. ThemeService (`src/services/theme_service.py`)
**Purpose**: Theme detection and icon management

```python
from services.theme_service import ThemeService

# Create service
theme_service = ThemeService(app)

# Check theme
is_dark = theme_service.is_dark_theme()

# Get icon path
icon_path = theme_service.get_icon_path()

# Setup application icon
theme_service.setup_application_icon()
```

**Adding Theme Features**:
```python
class ThemeService:
    def get_stylesheet(self) -> str:
        """Get theme-specific stylesheet"""
        if self.is_dark_theme():
            return "/* dark theme styles */"
        return "/* light theme styles */"
```

### 3. ApplicationController (`src/controllers/application_controller.py`)
**Purpose**: Application lifecycle management

```python
from controllers.application_controller import ApplicationController

# Create controller
app_controller = ApplicationController(app, config)

# Initialize application
app_controller.initialize()

# Show main window
app_controller.show_main_window()

# Cleanup on exit
app_controller.cleanup()
```

**Adding New Services**:
```python
def _initialize_services(self) -> None:
    # Existing services
    logging_service = LoggingService(...)
    self.services['logging'] = logging_service
    
    # Add new service
    new_service = NewService(logging_service)
    self.services['new_service'] = new_service
```

### 4. MainView (`src/views/main_view.py`)
**Purpose**: Main application window

```python
# Dev mode setup (called by ApplicationController)
main_view.setup_dev_mode(dev_logging=True)
```

## Common Tasks

### Adding a New Command-Line Argument

1. **Update AppConfig**:
```python
# src/config/app_config.py
@dataclass
class AppConfig:
    # ... existing fields
    new_feature: bool
    
    @classmethod
    def parse_arguments(cls) -> 'AppConfig':
        parser = argparse.ArgumentParser(...)
        parser.add_argument('--new-feature', action='store_true',
                          help='Enable new feature')
        args = parser.parse_args()
        return cls.from_args(args)
```

2. **Use in ApplicationController**:
```python
# src/controllers/application_controller.py
def _setup_new_feature(self) -> None:
    if self.config.new_feature:
        # Setup new feature
        pass

def initialize(self) -> None:
    self._setup_theme()
    self._initialize_services()
    self._create_main_view()
    self._setup_dev_mode()
    self._setup_new_feature()  # Add here
```

### Adding a New Service

1. **Create Service Class**:
```python
# src/services/new_service.py
class NewService:
    def __init__(self, logging_service):
        self.logger = logging_service.get_logger('new_service')
    
    def do_something(self):
        self.logger.info("Doing something")
```

2. **Register in ApplicationController**:
```python
# src/controllers/application_controller.py
def _initialize_services(self) -> None:
    # ... existing services
    
    # Add new service
    from services.new_service import NewService
    new_service = NewService(self.services['logging'])
    self.services['new_service'] = new_service
```

3. **Inject into Views**:
```python
def _create_main_view(self) -> None:
    self.main_view = MainView(
        self.services['package_manager'],
        self.services['lmdb'],
        logging_service=self.services['logging'],
        new_service=self.services['new_service'],  # Add here
        dev_logging=self.config.dev_logging,
        stdout_log_level=self.config.stdout_log_level
    )
```

### Modifying Service Initialization Order

Services are initialized in this order (dependencies matter):

```python
def initialize(self) -> None:
    self._setup_theme()          # 1. No dependencies
    self._initialize_services()  # 2. Core services
    self._create_main_view()     # 3. Depends on services
    self._setup_dev_mode()       # 4. Depends on view
```

To change order, modify the `initialize()` method:
```python
def initialize(self) -> None:
    self._setup_theme()
    self._initialize_services()
    self._setup_custom_feature()  # Add between services and view
    self._create_main_view()
    self._setup_dev_mode()
```

### Adding Cleanup Logic

```python
# src/controllers/application_controller.py
def cleanup(self) -> None:
    """Clean up resources on application exit"""
    # Cleanup in reverse order of initialization
    
    if 'new_service' in self.services:
        self.services['new_service'].cleanup()
    
    if 'lmdb' in self.services:
        self.services['lmdb'].close()
```

## Testing

### Testing AppConfig
```python
# tests/test_app_config.py
import sys
from config.app_config import AppConfig

def test_parse_arguments():
    sys.argv = ['prog', '--dev-outline', '--dev-logging']
    config = AppConfig.parse_arguments()
    assert config.dev_outline == True
    assert config.dev_logging == True
```

### Testing ThemeService
```python
# tests/test_theme_service.py
from unittest.mock import Mock
from services.theme_service import ThemeService

def test_dark_theme_detection():
    mock_app = Mock()
    mock_palette = Mock()
    mock_color = Mock()
    mock_color.lightness.return_value = 50  # Dark
    mock_palette.color.return_value = mock_color
    mock_app.palette.return_value = mock_palette
    
    service = ThemeService(mock_app)
    assert service.is_dark_theme() == True
```

### Testing ApplicationController
```python
# tests/test_application_controller.py
from unittest.mock import Mock, patch
from controllers.application_controller import ApplicationController
from config.app_config import AppConfig

def test_initialization():
    mock_app = Mock()
    config = AppConfig(dev_outline=False, dev_logging=False, 
                      stdout_log_level='WARNING')
    
    controller = ApplicationController(mock_app, config)
    
    with patch.object(controller, '_setup_theme'):
        with patch.object(controller, '_initialize_services'):
            with patch.object(controller, '_create_main_view'):
                controller.initialize()
                
    assert 'theme' in controller.services
```

## Debugging

### Enable Debug Logging
```bash
python src/main.py --dev-logging --stdout-log-level DEBUG
```

### Enable Widget Outlines
```bash
python src/main.py --dev-outline
```

### Check Service Initialization
Add logging to ApplicationController:
```python
def _initialize_services(self) -> None:
    print("Initializing services...")
    logging_service = LoggingService(...)
    print(f"Created logging service: {logging_service}")
    self.services['logging'] = logging_service
    # ... etc
```

## Best Practices

### 1. Service Dependencies
- Always initialize services in dependency order
- Document dependencies in service docstrings
- Use dependency injection, not global state

### 2. Configuration
- Add all CLI options to AppConfig
- Don't parse arguments outside of AppConfig
- Use type hints for all config fields

### 3. Lifecycle Management
- Initialize in ApplicationController.initialize()
- Cleanup in ApplicationController.cleanup()
- Don't create services in main.py

### 4. Testing
- Mock dependencies in unit tests
- Test each component independently
- Use integration tests for full startup

### 5. Error Handling
- Handle errors in services, not in main.py
- Log errors using LoggingService
- Provide user-friendly error messages

## Migration Guide

### From Old main.py to New Architecture

**Old Pattern**:
```python
# main.py
def main():
    args = parser.parse_args()
    app = QApplication(sys.argv)
    
    # Direct service creation
    service = SomeService()
    
    # Direct view creation
    view = MainView(service)
    view.show()
```

**New Pattern**:
```python
# main.py
def main():
    config = AppConfig.parse_arguments()
    app = QApplication(sys.argv)
    
    # Delegate to controller
    controller = ApplicationController(app, config)
    controller.initialize()
    controller.show_main_window()
```

**Service Creation** (in ApplicationController):
```python
def _initialize_services(self):
    service = SomeService()
    self.services['some_service'] = service
```

**View Creation** (in ApplicationController):
```python
def _create_main_view(self):
    self.main_view = MainView(self.services['some_service'])
```

## Troubleshooting

### Service Not Found
**Problem**: `KeyError: 'service_name'`
**Solution**: Ensure service is registered in `_initialize_services()`

### Wrong Initialization Order
**Problem**: Service fails because dependency not initialized
**Solution**: Check initialization order in `initialize()` method

### Config Not Applied
**Problem**: Configuration option not working
**Solution**: Verify option is added to AppConfig dataclass and parse_arguments()

### View Not Showing
**Problem**: Main window doesn't appear
**Solution**: Ensure `show_main_window()` is called after `initialize()`

## Resources

- [MVC Refactor Architecture](../architecture/MVC_REFACTOR_ARCHITECTURE.md) - Detailed architecture
- [MVC Refactor Completed](../planning/mvc-refactor-completed.md) - Implementation summary
- [MVC Refactor Plan](../planning/main-py-mvc-refactor.md) - Original plan
