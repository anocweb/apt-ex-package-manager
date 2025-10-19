# Development Guide

## Quick Start

### Prerequisites
- **Python**: 3.8 or higher
- **Operating System**: Linux (KDE Plasma 6 recommended)
- **Optional**: python3-apt (for APT backend on Debian/Ubuntu systems)

### Setup

#### 1. Clone repository
```bash
git clone https://github.com/anocweb/apt-ex-package-manager.git
cd apt-ex-package-manager
```

#### 2. Create virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install system packages (optional, backend-specific)

**For APT backend (Debian/Ubuntu only)**:
```bash
sudo apt install python3-apt
```

Note: python-apt must be installed system-wide. It cannot be installed via pip.

**For Flatpak backend (when implemented)**:
```bash
sudo apt install flatpak  # Debian/Ubuntu
sudo dnf install flatpak  # Fedora
```

#### 5. Run application
```bash
python src/main.py

# With debug logging
python src/main.py --dev-logging
```

## Project Structure

```
src/
├── main.py                 # Application entry point
├── controllers/            # Business logic
│   ├── plugins/            # Backend plugins
│   ├── apt_controller.py   # APT operations (legacy)
│   └── package_manager.py  # Package management coordinator
├── views/                  # UI components
│   ├── panels/             # Panel controllers
│   │   ├── base_panel.py   # Base panel class
│   │   ├── home_panel.py   # Home panel
│   │   └── ...             # Other panels
│   └── main_view.py        # Main window coordinator
├── workers/                # Background threads
│   ├── cache_update_worker.py
│   ├── installed_packages_worker.py
│   └── update_check_worker.py
├── models/                 # Data structures
│   ├── package_model.py    # Package data classes
│   ├── category_model.py   # Category CRUD
│   └── package_cache_model.py # Cache CRUD
├── cache/                  # LMDB caching
│   ├── lmdb_manager.py     # Database manager
│   └── package_cache.py    # Package cache
├── ui/                     # Qt Designer files
│   ├── windows/            # Main window layouts
│   ├── panels/             # Panel layouts
│   └── widgets/            # Widget layouts
├── widgets/                # Custom widgets
│   ├── base_list_item.py   # Base list item
│   └── ...                 # Specific list items
├── services/               # Shared services
│   ├── logging_service.py  # Logging
│   ├── status_service.py   # Status bar management
│   └── odrs_service.py     # Ratings service
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

**PackageManager** (`src/controllers/package_manager.py`)
- Unified API for all backends
- Plugin discovery and registration
- Backend routing

**Panel Controllers** (`src/views/panels/`)
- Dedicated controller per panel
- Inherit from BasePanel
- Handle panel-specific logic

**MainView** (`src/views/main_view.py`)
- Main window coordinator (~400 lines)
- Panel navigation
- Signal routing
- Context actions display

**Worker Threads** (`src/workers/`)
- Background operations
- Keep UI responsive
- Signal-based communication

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

### Adding a New Panel
See [PANEL_DEVELOPMENT_GUIDE.md](developer/PANEL_DEVELOPMENT_GUIDE.md) for detailed instructions.

1. Create `.ui` file in `src/ui/panels/`
2. Create panel controller inheriting from BasePanel
3. Register in MainView.load_panels()
4. Add sidebar button connection

### Adding a Backend Plugin
See [PLUGIN_ARCHITECTURE.md](architecture/PLUGIN_ARCHITECTURE.md) for details.

1. Create plugin class inheriting from BasePackageController
2. Implement required methods
3. Place in `src/controllers/plugins/`
4. Plugin auto-discovered on startup

### Creating a Worker Thread
1. Create class inheriting from QThread
2. Define signals (finished_signal, error_signal, etc.)
3. Implement run() method
4. Place in `src/workers/`

### Modifying Cache Schema
1. Update `src/cache/lmdb_manager.py`
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

## Current Architecture

### Plugin System (Implemented)
See [PLUGIN_ARCHITECTURE.md](architecture/PLUGIN_ARCHITECTURE.md) for details.

**Status:**
- ✅ BasePackageController interface
- ✅ Plugin discovery and registration
- ✅ APTPlugin (converted from APTController)
- ✅ Unified PackageManager interface
- 🔄 Flatpak plugin (stub created)
- 📋 AppImage plugin (planned)

### View Architecture (Refactored)
See [VIEW_ARCHITECTURE.md](architecture/VIEW_ARCHITECTURE.md) for details.

**Status:**
- ✅ Panel controller architecture
- ✅ Worker thread system
- ✅ Standardized widgets
- ✅ Organized UI file structure

## Resources

### Documentation
- [INDEX.md](INDEX.md) - Complete documentation index
- [STATUS.md](STATUS.md) - Implementation status
- [FEATURES.md](features/FEATURES.md) - Feature specifications
- [DESIGN_GUIDELINES.md](features/DESIGN_GUIDELINES.md) - UI guidelines

### Developer Guides
- [PANEL_DEVELOPMENT_GUIDE.md](developer/PANEL_DEVELOPMENT_GUIDE.md) - Creating panels
- [AI_ASSISTED_DEVELOPMENT.md](developer/AI_ASSISTED_DEVELOPMENT.md) - Using AI tools
- [MVC_QUICK_REFERENCE.md](developer/MVC_QUICK_REFERENCE.md) - MVC patterns

### Architecture
- [VIEW_ARCHITECTURE.md](architecture/VIEW_ARCHITECTURE.md) - View system
- [PLUGIN_ARCHITECTURE.md](architecture/PLUGIN_ARCHITECTURE.md) - Plugin system
- [DATABASE_ARCHITECTURE.md](architecture/DATABASE_ARCHITECTURE.md) - LMDB caching

## Getting Help

- Check [STATUS.md](STATUS.md) for what's implemented
- Review existing code for patterns
- See [AI_ASSISTED_DEVELOPMENT.md](developer/AI_ASSISTED_DEVELOPMENT.md) for AI assistance tips
