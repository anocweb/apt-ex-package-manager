# Development Guide

## Quick Start

### Prerequisites
- Python 3.8+
- Qt6 development libraries
- APT development headers (python3-apt)
- LMDB library

### Setup
```bash
# Clone repository
git clone <repository-url>
cd apt-qt6-manager

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

## Project Structure

```
src/
├── main.py                 # Application entry point
├── controllers/            # Business logic
│   ├── apt_controller.py   # APT operations
│   └── package_manager.py  # Package management coordinator
├── views/                  # UI components
│   └── main_view.py        # Main window
├── models/                 # Data structures
│   ├── package_model.py    # Package data classes
│   ├── category_model.py   # Category CRUD
│   └── package_cache_model.py # Cache CRUD
├── cache/                  # LMDB caching
│   ├── database.py         # Database manager
│   ├── cache_manager.py    # Cache coordinator
│   └── connection_manager.py # Connection pooling
├── ui/                     # Qt Designer files
│   ├── main_window.ui      # Main window layout
│   └── *.ui                # Panel layouts
├── widgets/                # Custom widgets
├── services/               # Shared services
│   └── logging_service.py  # Logging
└── settings/               # Configuration
    └── app_settings.py     # Settings management
```

## Current Architecture

### MVC Pattern
- **Models**: Data structures and database operations
- **Views**: Qt6 UI components and user interactions
- **Controllers**: APT operations and business logic

### Data Flow
```
User Action → View → Controller → APT/Cache → Model → View Update
```

### Key Components

**APTController** (`src/controllers/apt_controller.py`)
- Monolithic APT operations
- Package search, install, remove
- Category management
- Cache integration

**MainView** (`src/views/main_view.py`)
- Main window with sidebar navigation
- Panel management
- Context actions
- UI state management

**LMDB Cache** (`src/cache/`)
- High-performance key-value storage
- Package and category caching
- TTL-based expiration

## Development Workflow

### Running from Source
```bash
python src/main.py
```

### Editing UI Files
```bash
# Open in Qt Designer
designer src/ui/main_window.ui

# UI files are loaded at runtime, no compilation needed
```

### Logging
Logs are written to:
- Console (INFO level)
- `~/.cache/apt-ex-package-manager/apt-ex.log` (DEBUG level)

### Cache Location
- Database: `~/.cache/apt-ex-package-manager/cache.lmdb/`
- Settings: `~/.config/apt-ex-package-manager/`

## Code Style

### Python Standards
- Follow PEP 8
- Use type hints for all functions
- snake_case for functions/variables
- PascalCase for classes
- UPPER_SNAKE_CASE for constants

### Example
```python
def get_installed_packages(self, limit: int = None) -> List[Package]:
    """Get list of installed packages.
    
    Args:
        limit: Maximum number of packages to return
        
    Returns:
        List of Package objects
    """
    pass
```

### Import Organization
```python
# Standard library
import sys
from typing import List

# Third-party
from PyQt6.QtWidgets import QMainWindow

# Local
from models.package_model import Package
```

## Common Tasks

### Adding a New UI Panel
1. Create `.ui` file in `src/ui/`
2. Load in MainView: `uic.loadUi('ui/panel.ui', widget)`
3. Add to sidebar navigation
4. Connect signals/slots

### Adding a Method to APTController
1. Add method with type hints and docstring
2. Implement APT operations
3. Add caching if appropriate
4. Update views to use new method

### Modifying Cache Schema
1. Update `src/cache/database.py`
2. Update model classes in `src/models/`
3. Test migration from old schema

## Testing

### Manual Testing
```bash
# Run application
python src/main.py

# Test specific features
# - Search for packages
# - Install/remove packages
# - Browse categories
# - Check cache behavior
```

### Test Environment
- Ubuntu 22.04+ or Debian-based system
- KDE Plasma 6 (recommended)
- Active APT repositories

## Debugging

### Enable Debug Logging
```python
# In src/main.py
logging_service.set_level(logging.DEBUG)
```

### Common Issues

**Cache not updating:**
- Check `~/.cache/apt-ex-package-manager/cache.lmdb/`
- Clear cache: Delete directory and restart

**UI not loading:**
- Verify `.ui` files exist in `src/ui/`
- Check Qt Designer file paths

**APT errors:**
- Run with sudo if permission issues
- Check APT cache: `sudo apt update`

## Planned Architecture

### Plugin System (Future)
See [docs/architecture/PLUGIN_ARCHITECTURE.md](architecture/PLUGIN_ARCHITECTURE.md) for the planned plugin-based architecture that will replace the current monolithic APTController.

**Key Changes:**
- `APTController` → `APTPlugin`
- Plugin discovery and registration
- Multi-backend support (Flatpak, AppImage)
- Unified PackageManager interface

**Timeline:** No specific timeline (side project)

## Resources

- [STATUS.md](STATUS.md) - Implementation status
- [FEATURES.md](features/FEATURES.md) - Feature specifications
- [DESIGN_GUIDELINES.md](features/DESIGN_GUIDELINES.md) - UI guidelines
- [AI_ASSISTED_DEVELOPMENT.md](developer/AI_ASSISTED_DEVELOPMENT.md) - Using AI tools

## Getting Help

- Check [STATUS.md](STATUS.md) for what's implemented
- Review existing code for patterns
- See [AI_ASSISTED_DEVELOPMENT.md](developer/AI_ASSISTED_DEVELOPMENT.md) for AI assistance tips
