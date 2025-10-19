# Development Guidelines

## Code Quality Standards

### Python Style Conventions
- **PEP 8 Compliance**: Follow PEP 8 recommendations for Python code formatting
- **Naming Conventions**:
  - `snake_case` for functions, methods, variables, and module names
  - `PascalCase` for class names (e.g., `MainView`, `APTController`, `PackageManager`)
  - `UPPER_CASE` for constants
- **Type Hints**: Use type hints for function parameters and return values
  ```python
  def get_installed_packages(self, limit: int = None, offset: int = 0) -> List[dict]:
  ```
- **Docstrings**: Provide docstrings for classes and public methods
  ```python
  def populate_caches_on_startup(self):
      """Populate caches if empty or expired on application startup"""
  ```

### Import Organization
- Standard library imports first
- Third-party imports second (PyQt6, apt, lmdb, requests)
- Local application imports last
- Group related imports together
  ```python
  from PyQt6.QtWidgets import QMainWindow, QGridLayout, QLabel
  from PyQt6.QtCore import Qt, QSize, QTimer
  from PyQt6.QtGui import QIcon, QTextCursor
  from PyQt6 import uic
  
  from models.package_model import Package
  from services.logging_service import LoggingService
  ```

### Code Structure
- Keep methods focused and single-purpose
- Use private methods (prefix with `_`) for internal implementation details
- Separate UI logic from business logic
- Use descriptive variable names that convey intent

## Architectural Patterns

### MVC Pattern Implementation
**Models** (`models/`):
- Data structures and business entities
- No UI dependencies
- Example: `Package`, `PackageSummary`, `PackageCache`

**Views** (`views/`, `widgets/`, `ui/`):
- UI components and user interaction
- Load UI from `.ui` files using `uic.loadUi()`
- Connect signals to controller methods
- Example pattern:
  ```python
  class MainView(QMainWindow):
      def __init__(self, package_manager, lmdb_manager, logging_service=None):
          super().__init__()
          self.package_manager = package_manager
          self.lmdb_manager = lmdb_manager
          uic.loadUi('src/ui/main_window.ui', self)
  ```

**Controllers** (`controllers/`):
- Business logic and coordination
- No direct UI manipulation
- Return data to views
- Example: `APTController`, `PackageManager`

### Plugin Architecture Pattern
All backend plugins follow a consistent structure:

**Base Interface**:
```python
class BasePackageController(ABC):
    @property
    @abstractmethod
    def backend_id(self) -> str:
        """Unique identifier for backend"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if backend is available on system"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Set[str]:
        """Return set of supported operations"""
        pass
```

**Plugin Implementation**:
- Inherit from `BasePackageController`
- Implement all required abstract methods
- Declare capabilities via `get_capabilities()`
- Place in `src/controllers/plugins/` directory
- Automatic discovery and registration

**Standard Capabilities**:
- `search`, `install`, `remove`, `update`
- `list_installed`, `list_updates`, `categories`
- `ratings`, `repositories`, `dependencies`, `permissions`

### Repository Pattern
**Purpose**: Abstract data access from business logic

**Structure**:
```python
class BaseRepository(ABC):
    @abstractmethod
    def get_sources(self) -> List[RepositorySource]:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
```

**Implementation**:
- Separate repositories for APT, Flatpak, AppImage
- Repository manager coordinates multiple repositories
- Repositories handle system-level operations

### Service Container Pattern
**Purpose**: Centralized dependency injection

**Usage**:
```python
# Services are singletons accessible throughout application
self.logging_service = LoggingService(stdout_log_level='WARNING')
self.logger = self.logging_service.get_logger('ui')
```

**Common Services**:
- `LoggingService`: Application-wide logging
- `ODRSService`: Package ratings integration
- `ThemeService`: Theme and styling management

## Qt6 and PyQt6 Patterns

### UI Loading Pattern
**Always use Qt Designer UI files**:
```python
uic.loadUi('src/ui/main_window.ui', self)
```

**Panel Loading**:
```python
def load_panels(self):
    """Load all panel UI files and add them to the content stack"""
    panel_files = {
        'home': 'home_panel.ui',
        'installed': 'installed_panel.ui'
    }
    
    for panel_name, ui_file in panel_files.items():
        panel_widget = QWidget()
        ui_path = os.path.join('src', 'ui', ui_file)
        uic.loadUi(ui_path, panel_widget)
        self.panels[panel_name] = panel_widget
        self.contentStack.addWidget(panel_widget)
```

### Signal/Slot Connection Pattern
**Lambda for inline connections**:
```python
self.homeBtn.clicked.connect(lambda: self.select_page('home'))
```

**Direct method connections**:
```python
home_panel.search_input.textChanged.connect(self.search_packages)
```

**Custom signals in widgets**:
```python
class InstalledListItem(QWidget):
    remove_requested = pyqtSignal(str)
    
    def on_remove_clicked(self):
        self.remove_requested.emit(self.package_name)
```

### Threading Pattern for Long Operations
**Worker Thread Pattern**:
```python
class CacheUpdateWorker(QThread):
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(str)
    
    def __init__(self, params):
        super().__init__()
        self.params = params
    
    def run(self):
        try:
            # Long-running operation
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

# Usage
self.worker = CacheUpdateWorker(params)
self.worker.finished_signal.connect(self.on_finished)
self.worker.error_signal.connect(self.on_error)
self.worker.start()
```

### Dynamic UI Updates
**Property-based styling**:
```python
button.setProperty("selected", "true")
button.style().unpolish(button)
button.style().polish(button)
```

**Context actions pattern**:
```python
def clear_context_actions(self):
    """Clear all context action buttons"""
    layout = self.contextActions.layout()
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

def add_context_action(self, text: str, callback):
    """Add a context action button"""
    button = QPushButton(text)
    button.clicked.connect(callback)
    self.contextActions.layout().addWidget(button)
    return button
```

## Logging Patterns

### Logger Initialization
**Service-based logging**:
```python
# In __init__
self.logging_service = LoggingService(stdout_log_level='WARNING')
self.logger = self.logging_service.get_logger('ui')

# Pre-register additional loggers
self.logging_service.get_logger('odrs')
self.logging_service.get_logger('rating_cache')
```

### Logging Levels
- **DEBUG**: Detailed diagnostic information
  ```python
  self.logger.debug("Starting panel loading")
  ```
- **INFO**: General informational messages
  ```python
  self.logger.info(f"Navigated to {page_key} page")
  ```
- **ERROR**: Error conditions
  ```python
  self.logger.error(f"Failed to load panel {panel_name}: {e}")
  ```

### Logging Best Practices
- Log user actions at INFO level
- Log technical details at DEBUG level
- Log errors with context information
- Use named loggers for different components

## Caching Patterns

### LMDB Cache Usage
**Cache initialization**:
```python
from cache import LMDBManager, PackageCacheModel

lmdb_manager = LMDBManager()
pkg_cache = PackageCacheModel(lmdb_manager, 'apt')
```

**Cache operations**:
```python
# Get packages
packages = pkg_cache.get_all_packages(limit=20, offset=0)

# Add package
pkg_cache.add_package(package_data)

# Update status
pkg_cache.update_installed_status(package_id, is_installed)
```

### TTL-Based Cache Validation
- Cache entries have time-to-live (TTL)
- Check cache validity before using
- Force refresh when needed:
  ```python
  self.lmdb_manager.force_refresh('apt')
  ```

### Batch Processing Pattern
**Process large datasets in batches**:
```python
batch_size = 100
for batch_start in range(0, total, batch_size):
    batch_end = min(batch_start + batch_size, total)
    batch = packages[batch_start:batch_end]
    
    for pkg_data in batch:
        pkg_cache.add_package(pkg_data)
```

## Error Handling Patterns

### Try-Except with Logging
```python
try:
    result = operation()
except Exception as e:
    self.logger.error(f"Operation failed: {e}")
    self.statusbar.showMessage(f"Error: {e}", 5000)
    return default_value
```

### Graceful Degradation
```python
# Check availability before using
if hasattr(self, 'lmdb_manager') and self.lmdb_manager:
    # Use cache
else:
    # Fallback behavior
```

### User-Friendly Error Messages
- Show technical errors in logs
- Display user-friendly messages in UI
- Provide actionable feedback when possible

## Status Bar and User Feedback

### Status Messages
**Temporary messages**:
```python
self.statusbar.showMessage("Loading packages...", 3000)  # 3 seconds
```

**Animated status for long operations**:
```python
def start_animated_status(self, base_message):
    """Start animated status with dots"""
    self.status_base_message = base_message
    self.status_timer = QTimer()
    self.status_timer.timeout.connect(self.animate_status_dots)
    self.status_timer.start(500)

def animate_status_dots(self):
    """Animate the dots in status message"""
    dots = "." * (self.status_dots + 1)
    self.statusbar.showMessage(f"{self.status_base_message}{dots}")
    self.status_dots = (self.status_dots + 1) % 3
```

## Settings Management

### QSettings Pattern
```python
from settings.app_settings import AppSettings

self.app_settings = AppSettings()

# Get settings
enabled = self.app_settings.get_odrs_enabled()
default_repo = self.app_settings.get_default_repository()

# Set settings
self.app_settings.set_odrs_enabled(True)
self.app_settings.set_default_repository('apt')
```

### Settings Location
- Stored in `~/.config/apt-ex-package-manager/`
- Use QSettings for cross-platform compatibility

## Testing Patterns

### Test Script Structure
```python
#!/usr/bin/env python3
"""Test script description"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_feature():
    """Test specific feature"""
    print("Testing feature...")
    # Test implementation
    print("✓ Test passed")

def main():
    """Run all tests"""
    try:
        test_feature()
        print("✓ All tests completed successfully!")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## Common Code Idioms

### Conditional Logging
```python
if self.logger:
    self.logger.debug(f"Processing {item}")
```

### Lambda with Side Effects
```python
# Execute multiple statements in lambda
self.homeBtn.clicked.connect(
    lambda: (self.logging_service.debug("Home clicked"), self.select_page('home'))[1]
)
```

### Dictionary-Based Dispatch
```python
page_titles = {
    'home': 'Welcome to Apt-Ex Package Manager',
    'installed': 'Installed Packages',
    'updates': 'Available Updates'
}
self.pageTitle.setText(page_titles.get(page_key, 'Apt-Ex Package Manager'))
```

### Safe Attribute Access
```python
if hasattr(settings_panel, 'makeDefaultFlatpak'):
    settings_panel.makeDefaultFlatpak.clicked.connect(callback)
```

## Performance Optimization

### Virtual Scrolling
- Use virtual scrolling for large lists
- Load items on-demand as user scrolls
- Example: `VirtualCategoryContainer`, `VirtualLogContainer`

### Lazy Loading
- Load data only when needed
- Use pagination for large datasets
- Example: `get_installed_packages(limit=20, offset=0)`

### Background Processing
- Use QThread for long operations
- Keep UI responsive during processing
- Show progress indicators

## Security Practices

### Input Validation
- Validate all user inputs before processing
- Sanitize command-line arguments
- Use parameterized queries for database operations

### Privilege Escalation
- Use sudo/pkexec for operations requiring root
- Minimize privileged operations
- Validate operations before escalation

### Safe Subprocess Calls
```python
# Hardcoded paths are safe
subprocess.run(['xdg-open', '/etc/apt/'], check=True)
```

## Documentation Standards

### Code Comments
- Use comments to explain "why", not "what"
- Document complex algorithms
- Add TODO comments for future improvements

### Method Documentation
```python
def get_installed_packages_list(self, lmdb_manager, limit: int = None, offset: int = 0) -> List[dict]:
    """Get list of installed packages with minimal info for display
    
    Args:
        lmdb_manager: LMDB manager instance
        limit: Maximum number of packages to return
        offset: Number of packages to skip
    
    Returns:
        List of package dictionaries with name, version, description
    """
```

### Inline Documentation
- Document non-obvious design decisions
- Explain workarounds and edge cases
- Reference related documentation files

## Project-Specific Conventions

### Backend Identification
- Always include backend identifier in package data
- Use `backend` attribute: `'apt'`, `'flatpak'`, `'appimage'`
- Display backend badges in UI

### Category Mapping
- Map backend-specific categories to standard sidebar categories
- Use `get_sidebar_category_mapping()` method
- Standard categories: games, graphics, internet, multimedia, office, development, system, utilities, education, science, accessibility, all

### Context Actions
- Clear actions when switching pages: `clear_context_actions()`
- Add page-specific actions: `add_context_action(text, callback)`
- Limit to 3-4 buttons for clean interface
- Use emoji icons for visual appeal

### File Paths
- Use `os.path.join()` for cross-platform compatibility
- Store relative paths from project root
- Use absolute paths for system locations
