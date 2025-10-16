# Apt-Ex Package Manager - Development Guidelines

## Code Quality Standards

### Python Conventions
- **Class Names**: PascalCase (e.g., `MainView`, `APTController`, `PackageModel`)
- **Method Names**: snake_case (e.g., `install_package`, `update_ui`, `fetch_package_info`)
- **Variable Names**: snake_case (e.g., `package_name`, `main_view`)
- **Constants**: UPPER_SNAKE_CASE for module-level constants

### Import Organization
- **Standard Library**: First (e.g., `import sys`)
- **Third-Party**: Second (e.g., `from PyQt6.QtWidgets import QApplication`)
- **Local Modules**: Last (e.g., `from views.main_view import MainView`)
- **Qt6 Import Pattern**: Use specific imports `from PyQt6.QtWidgets import QMainWindow, QApplication`

### Documentation Standards
- **Docstrings**: Use for all public methods and classes
- **Inline Comments**: Explain complex logic and business rules
- **Method Comments**: Brief descriptions above method definitions
- **TODO Comments**: Mark incomplete implementations with `# Code to...` pattern

## Structural Conventions

### Modular MVC Architecture Patterns
- **Views**: Inherit from Qt6 widgets with Discover-style card layouts
- **Package Manager**: Unified interface coordinating multiple backends
- **Backend Controllers**: APT, Flatpak, and AppImage-specific implementations
- **Models**: Unified package representation with backend-specific metadata
- **Separation**: Views handle UI, Manager coordinates backends, Controllers handle backend logic

### Class Structure
- **Constructor Pattern**: `__init__(self, ...)` with parameter assignment
- **UI Setup**: Dedicated `setup_ui()` method for UI initialization
- **Event Handlers**: Methods named after actions (e.g., `install_package`)
- **Update Methods**: `update_ui()` for refreshing display state

### Method Organization
- **Constructor**: First method after class declaration
- **Setup Methods**: UI and initialization methods
- **Event Handlers**: User interaction methods
- **Utility Methods**: Helper and update methods
- **String Representation**: `__str__` method for data classes

## Implementation Patterns

### UI Integration Patterns (Discover-Style)
- **UI Loading**: Use `uic.loadUi('path/to/file.ui', self)` for Qt Designer files
- **Card Layout**: Grid-based package cards similar to KDE Discover
- **Signal Connection**: Connect UI elements in `setup_ui()` method
- **Manager Injection**: Pass package manager instance to view constructor
- **Widget Access**: Direct access to UI elements by name (e.g., `self.install_button`)
- **Backend Indicators**: Visual badges showing package source (APT/Flatpak/AppImage)
- **Context Actions**: Use header action area for page-specific buttons
- **Custom Widget Styling**: Set `Qt.WidgetAttribute.WA_StyledBackground` for stylesheet backgrounds

### Event Handling
- **Button Clicks**: Connect to controller methods via view wrapper methods
- **Input Retrieval**: Get text from inputs using `.text()` method
- **UI Updates**: Call `update_ui()` after state-changing operations
- **List Updates**: Clear and repopulate list widgets for data refresh
- **Selection Events**: Both left-click and right-click should set selection state
- **Context Menus**: Right-click shows context menu after setting selection

### Data Flow Patterns (Multi-Backend)
- **View → Cache**: Views check cache first for fast data access
- **Cache → Controller**: Cache miss triggers fresh data fetch
- **Controller → Backend**: Controllers delegate to appropriate backend
- **Backend → Model**: Backend data converted to unified models
- **Model → Cache**: Fresh data stored in SQLite cache
- **Cache → View**: Cached data displayed with backend indicators

## Common Code Idioms

### Application Bootstrap
```python
def main():
    app = QApplication(sys.argv)
    main_view = MainView()
    main_view.show()
    sys.exit(app.exec())
```

### UI Element Connection
```python
def setup_ui(self):
    self.install_button.clicked.connect(self.install_package)
    self.remove_button.clicked.connect(self.remove_package)
```

### Context Actions Pattern
```python
def select_page(self, page_key, page_index):
    self.clear_context_actions()
    if page_key == 'updates':
        self.add_context_action("🔄 Refresh", self.refresh_updates)
        self.add_context_action("⬆️ Update All", self.update_all)
```

### List Widget Population
```python
self.package_list_widget.clear()
for package in packages:
    self.package_list_widget.addItem(f"{package.name} - {package.version}: {package.description}")
```

### Data Class String Representation
```python
def __str__(self):
    return f"{self.name} - {self.version}: {self.description}"
```

### Custom Widget with Stylesheet Support
```python
class ExpandableItem(QWidget):
    def __init__(self, ...):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Enable stylesheet backgrounds for custom widgets
```

## Architectural Guidelines

### Package Manager Design
- **Backend Coordination**: Manager delegates operations to appropriate backends
- **Unified Interface**: Consistent API regardless of package type
- **Method Naming**: Use verb-noun pattern (e.g., `install_package`, `search_packages`)
- **Return Values**: Methods return unified package models
- **Error Handling**: Manager handles backend-specific errors uniformly

### Backend Controller Design
- **Backend-Specific**: Each controller handles one package system
- **Consistent Interface**: All backends implement common methods
- **Capability Declaration**: Backends declare supported operations
- **Error Translation**: Convert backend errors to unified format

### Model Design
- **Data Models**: Dataclasses for type-safe data structures
- **CRUD Models**: Database operations with proper error handling
- **Cache Models**: High-level caching interfaces
- **Initialization**: Constructor takes all required data parameters
- **Database Operations**: Create, read, update, delete with transactions
- **Serialization**: Implement `__str__` for display purposes

### View Design
- **UI Responsibility**: Views only handle display and user interaction
- **Controller Delegation**: Delegate all business logic to controllers
- **State Synchronization**: Update UI after controller operations
- **Widget Management**: Direct manipulation of Qt6 widgets
- **Context Actions**: Each page defines relevant header actions using `add_context_action()`
- **Custom Widgets**: Use `WA_StyledBackground` attribute for stylesheet support
- **Expandable Items**: Single-selection mode with context menus and background styling

## Development Standards

### File Organization
- **Entry Point**: `main.py` contains application bootstrap
- **UI Files**: Store Qt Designer files in `ui/` directory
- **Relative Imports**: Use relative imports within package structure
- **Path References**: Use relative paths for UI file loading

### Database and Caching Patterns
- **Cache First**: Always check cache before fetching fresh data
- **TTL Validation**: Automatic cache expiration and validation
- **Graceful Fallback**: Use stale cache data if fresh fetch fails
- **Transaction Safety**: Use context managers for database operations
- **Schema Evolution**: Design for future schema migrations

### Error Handling Preparation
- **Database Errors**: Handle SQLite exceptions gracefully
- **Cache Misses**: Automatic fallback to fresh data fetching
- **Transaction Rollback**: Ensure data consistency on failures
- **Placeholder Methods**: Use `pass` for unimplemented methods
- **Comment Stubs**: Mark incomplete implementations with descriptive comments
- **Recursion Prevention**: Use flags to prevent infinite loops in UI updates

### Testing Considerations
- **Method Isolation**: Design methods for easy unit testing
- **Dependency Injection**: Pass dependencies through constructors
- **State Visibility**: Provide getter methods for internal state access