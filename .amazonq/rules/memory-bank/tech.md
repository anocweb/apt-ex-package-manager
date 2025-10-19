# Technology Stack

## Programming Languages
- **Python 3**: Primary language for application logic
- **Qt Designer XML**: UI layout definitions (.ui files)

## Core Dependencies

### GUI Framework
- **PyQt6**: Python bindings for Qt6 framework
  - Modern Qt6 API
  - Native KDE Plasma 6 integration
  - Cross-platform GUI toolkit

### System Integration
- **python-apt**: Python interface to APT package management
  - Direct access to APT cache
  - Package installation/removal
  - Repository management

### Database
- **LMDB (Lightning Memory-Mapped Database)**: High-performance key-value store
  - Memory-mapped file access
  - ACID transactions
  - Zero-copy reads
  - Used for package and category caching

## Development Tools

### Build System
- **Makefile**: Build automation and common tasks
- **setup.py**: Python package setup and distribution

### UI Development
- **Qt Designer**: Visual UI layout editor
  - Creates .ui XML files
  - Generates Python code with pyuic6
  - Rapid UI prototyping

### Version Control
- **Git**: Source code management
- **.gitignore**: Excludes cache, build artifacts, Python bytecode

## Development Commands

### Running the Application
```bash
python src/main.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Building UI Files
```bash
# Convert .ui files to Python (if using Makefile)
make ui
```

### Testing
```bash
# Run plugin tests
python test_plugins.py

# Run LMDB tests
python test_lmdb.py
```

## Project Configuration Files

### requirements.txt
```
PyQt6
apt
lmdb
```

### setup.py
- Package metadata
- Entry points
- Installation configuration

### Makefile
- Common development tasks
- UI file compilation
- Build automation

## Runtime Environment

### Operating System
- **Linux**: Primary target platform
- **Debian/Ubuntu-based**: APT package manager required
- **KDE Plasma 6**: Recommended desktop environment

### System Requirements
- Python 3.x
- Qt6 libraries
- APT package manager
- LMDB library
- Sudo/pkexec for privilege escalation

### File System Locations
- **Config**: `~/.config/apt-ex-package-manager/`
- **Cache**: `data/cache.lmdb/` (relative to project)
- **Logs**: Configured in logging service

## Architecture Technologies

### Design Patterns
- **MVC (Model-View-Controller)**: Application architecture
- **Repository Pattern**: Data access abstraction
- **Plugin Architecture**: Extensible backend system
- **Service Container**: Dependency injection
- **Observer Pattern**: Qt signals/slots for event handling

### Caching Strategy
- **LMDB**: Persistent key-value storage
- **TTL (Time-To-Live)**: Cache invalidation strategy
- **Lazy Loading**: On-demand data loading
- **Background Updates**: Non-blocking cache refresh

### Concurrency
- **Qt Threading**: QThread for background operations
- **Async Operations**: Non-blocking package operations
- **Signal/Slot**: Thread-safe communication

## External Services

### ODRS (Open Desktop Ratings Service)
- Package ratings and reviews
- Integration via odrs_service.py
- Optional feature for package metadata

### APT System
- System package manager
- Command-line interface via python-apt
- Requires root privileges for modifications

## Development Workflow

### Code Organization
- **src/**: All application code
- **docs/**: Comprehensive documentation
- **tests/**: Test files
- **.amazonq/rules/**: AI assistant rules and memory bank

### UI Development Flow
1. Design UI in Qt Designer (.ui files)
2. Generate Python code with pyuic6
3. Import generated UI classes in views/widgets
4. Connect signals to controller methods

### Plugin Development Flow
1. Create plugin class inheriting BasePackageController
2. Implement required abstract methods
3. Declare capabilities via get_capabilities()
4. Add category mapping via get_sidebar_category_mapping()
5. Place in src/controllers/plugins/
6. Automatic discovery and registration

## Testing Infrastructure

### Test Files
- **test_plugins.py**: Plugin system tests
- **test_lmdb.py**: LMDB caching tests
- **tests/**: Additional test directory

### Testing Approach
- Unit tests for individual components
- Integration tests for plugin system
- Manual testing for UI interactions

## Performance Considerations

### LMDB Benefits
- Memory-mapped file I/O (fast reads)
- Zero-copy architecture
- ACID transactions
- Concurrent read access

### UI Responsiveness
- Virtual scrolling for large lists
- Background threading for long operations
- Incremental search results
- Cached package data

## Security Practices

### Privilege Escalation
- Sudo/pkexec for package operations
- Input validation before system commands
- Sanitized command-line arguments

### Data Validation
- User input sanitization
- Package signature verification (when possible)
- Secure configuration storage

## Future Technology Considerations

### Planned Integrations
- **Flatpak**: Additional package backend
- **AppImage**: Portable application support
- **Snap**: Potential future backend

### Potential Enhancements
- **D-Bus**: System integration
- **PackageKit**: Alternative backend interface
- **Notifications**: Desktop notification system
