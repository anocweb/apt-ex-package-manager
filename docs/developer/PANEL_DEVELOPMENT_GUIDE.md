# Panel Development Guide

## Quick Start: Creating a New Panel

### 1. Create the UI File
Place your `.ui` file in `src/ui/panels/my_panel.ui`

### 2. Create the Panel Controller

```python
"""My panel controller"""
from PyQt6.QtCore import pyqtSignal
from views.panels.base_panel import BasePanel


class MyPanel(BasePanel):
    """Description of what this panel does"""
    
    # Define signals for actions that need coordination
    action_requested = pyqtSignal(str)
    
    def setup_ui(self):
        """Setup UI components after loading"""
        # Initialize layouts, widgets, etc.
        pass
    
    def connect_signals(self):
        """Connect widget signals to handlers"""
        # self.myButton.clicked.connect(self.on_button_clicked)
        pass
    
    def on_show(self):
        """Called when panel becomes visible"""
        # Load data, refresh display, etc.
        pass
    
    def get_context_actions(self):
        """Return list of (text, callback) for header buttons"""
        return [
            ("🔄 Refresh", self.on_refresh),
            ("➕ Add", self.on_add)
        ]
    
    def get_title(self):
        """Return panel title for header"""
        return "My Panel Title"
    
    # Add your panel-specific methods below
    def on_refresh(self):
        """Handle refresh action"""
        pass
```

### 3. Register in MainView

Edit `src/views/main_view.py`:

```python
from views.panels.my_panel import MyPanel

# In load_panels():
panel_configs = {
    # ... existing panels ...
    'my_panel': ('src/ui/panels/my_panel.ui', MyPanel),
}

# In connect_panel_signals():
elif panel_name == 'my_panel':
    panel.action_requested.connect(self.handle_action)

# In setup_sidebar():
self.myPanelBtn.clicked.connect(lambda: self.select_page('my_panel'))
```

## BasePanel API

### Constructor Parameters
- `ui_file` - Path to .ui file
- `package_manager` - PackageManager instance
- `lmdb_manager` - LMDBManager instance
- `logging_service` - LoggingService instance
- `app_settings` - AppSettings instance

### Available Attributes
- `self.package_manager` - Access to package operations
- `self.lmdb_manager` - Access to cache
- `self.logging_service` - Logging service
- `self.app_settings` - User settings
- `self.logger` - Panel-specific logger

### Lifecycle Methods

#### `setup_ui(self)`
Called after UI is loaded. Use for:
- Creating layouts
- Initializing widgets
- Setting up virtual scrolling containers

#### `connect_signals(self)`
Called after `setup_ui()`. Use for:
- Connecting widget signals to handlers
- Setting up event listeners

#### `on_show(self)`
Called when panel becomes visible. Use for:
- Loading data
- Refreshing display
- Starting timers

#### `get_context_actions(self) -> List[Tuple[str, Callable]]`
Return list of context actions for header. Example:
```python
return [
    ("🔄 Refresh", self.refresh),
    ("⬆️ Update All", self.update_all)
]
```

#### `get_title(self) -> str`
Return panel title for header display.

## Using Worker Threads

### Example: Loading Data in Background

```python
from workers.my_worker import MyWorker

def load_data(self):
    """Load data using worker thread"""
    self.worker = MyWorker(self.package_manager)
    self.worker.finished_signal.connect(self.on_data_loaded)
    self.worker.error_signal.connect(self.on_error)
    self.worker.start()

def on_data_loaded(self, data):
    """Handle loaded data"""
    # Update UI with data
    pass

def on_error(self, error_message):
    """Handle error"""
    self.logger.error(f"Failed to load data: {error_message}")
```

### Creating a Worker

```python
"""My worker thread"""
from PyQt6.QtCore import QThread, pyqtSignal


class MyWorker(QThread):
    """Worker for background operation"""
    
    finished_signal = pyqtSignal(list)  # Emit results
    error_signal = pyqtSignal(str)      # Emit errors
    progress_signal = pyqtSignal(int)   # Emit progress
    
    def __init__(self, package_manager):
        super().__init__()
        self.package_manager = package_manager
    
    def run(self):
        try:
            # Perform long operation
            result = self.package_manager.get_packages()
            self.finished_signal.emit(result)
        except Exception as e:
            self.error_signal.emit(str(e))
```

## Emitting Signals

Panels should emit signals for actions that require coordination:

```python
class MyPanel(BasePanel):
    install_requested = pyqtSignal(str)  # package_name
    remove_requested = pyqtSignal(str)   # package_name
    
    def on_install_clicked(self):
        package_name = self.get_selected_package()
        self.install_requested.emit(package_name)
```

MainView will connect these signals to appropriate handlers.

## Accessing Services

### Package Manager
```python
# Search packages
packages = self.package_manager.search_packages("firefox", backend='apt')

# Get installed packages
installed = self.package_manager.get_installed_packages(backend='apt')

# Install package
self.package_manager.install_package("firefox", backend='apt')
```

### Cache (LMDB)
```python
from cache import PackageCacheModel

pkg_cache = PackageCacheModel(self.lmdb_manager, 'apt')
packages = pkg_cache.get_all_packages(limit=20, offset=0)
```

### Settings
```python
# Get setting
enabled = self.app_settings.get_odrs_enabled()

# Set setting
self.app_settings.set_odrs_enabled(True)
```

### Logging
```python
self.logger.debug("Debug message")
self.logger.info("Info message")
self.logger.error("Error message")
```

## Best Practices

1. **Keep panels focused** - Each panel should have a single responsibility
2. **Use workers for long operations** - Keep UI responsive
3. **Emit signals for coordination** - Don't call MainView methods directly
4. **Handle errors gracefully** - Show user-friendly messages
5. **Clean up resources** - Stop timers, cancel workers in cleanup
6. **Log important actions** - Use appropriate log levels
7. **Follow naming conventions** - snake_case for methods, PascalCase for classes

## Common Patterns

### Virtual Scrolling
```python
from widgets.virtual_category_container import VirtualCategoryContainer

def setup_ui(self):
    self.virtual_container = VirtualCategoryContainer()
    self.layout.addWidget(self.virtual_container)
    self.virtual_container.install_requested.connect(self.on_install)

def load_packages(self, packages):
    self.virtual_container.set_packages(packages)
```

### Loading States
```python
def load_data(self):
    # Show loading message
    self.show_loading()
    
    # Start worker
    self.worker = MyWorker()
    self.worker.finished_signal.connect(self.on_loaded)
    self.worker.start()

def on_loaded(self, data):
    # Hide loading, show data
    self.hide_loading()
    self.display_data(data)
```

### Error Handling
```python
def on_error(self, error_message):
    self.logger.error(f"Operation failed: {error_message}")
    
    # Show error in UI
    error_label = QLabel(f"Error: {error_message}")
    error_label.setStyleSheet("color: #FF6B6B;")
    self.layout.addWidget(error_label)
```

## Testing Panels

```python
import pytest
from views.panels.my_panel import MyPanel

def test_panel_initialization(qtbot):
    panel = MyPanel(
        'src/ui/panels/my_panel.ui',
        mock_package_manager,
        mock_lmdb_manager,
        mock_logging_service,
        mock_app_settings
    )
    
    assert panel.get_title() == "Expected Title"
    assert len(panel.get_context_actions()) == 2
```

## Examples

See existing panels for reference:
- `home_panel.py` - Search and featured packages
- `installed_panel.py` - List with worker thread
- `updates_panel.py` - Context actions, signal emission
- `settings_panel.py` - Form handling, settings management
