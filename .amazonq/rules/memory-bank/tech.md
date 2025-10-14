# Apt-Ex Package Manager - Technology Stack

## Programming Languages

### Python 3.8+
- **Primary Language**: All application logic and UI implementation
- **Version Requirement**: Python 3.8 or higher for modern features
- **Type Hints**: Required for function parameters and return values
- **Style Guide**: PEP 8 compliance for code formatting

## Core Dependencies

### GUI Framework
- **PyQt6**: Modern Qt6 bindings for Python
- **Import Pattern**: `from PyQt6.QtWidgets import *`
- **UI Designer**: Qt Designer for layout files (.ui)
- **Theme Integration**: KDE Plasma 6 system colors via QPalette

### Package Backend Integration
- **apt**: Python APT library for Debian/Ubuntu packages
- **flatpak**: Flatpak system integration via subprocess
- **appimage**: AppImage file management and integration
- **subprocess**: System command execution for all backends
- **sys**: System-specific parameters and functions

### Complete Dependency List
```
PyQt6
apt
subprocess
sys
requests  # For AppImage metadata and updates
os        # File system operations for AppImage
```

## Development Environment

### Required Tools
- Python 3.8+ interpreter
- Qt6 development libraries
- Qt Designer for UI layout editing
- APT development headers
- Flatpak runtime (optional, for Flatpak support)
- AppImage runtime support

### Build System
- **Entry Point**: `python src/main.py`
- **Dependencies**: Install via `pip install -r requirements.txt`
- **No Build Step**: Direct Python execution

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py

# Development with Qt Designer
designer src/ui/main_window.ui
```

## Architecture Technologies

### UI Framework
- **Qt6 Widgets**: Native desktop application framework
- **QMainWindow**: Primary window with menu bar and status bar
- **QSettings**: Configuration and preference management
- **QPalette**: System theme color integration

### System Integration
- **Privilege Escalation**: sudo/pkexec for administrative operations
- **Threading**: Asynchronous operations to prevent UI freezing
- **Process Management**: Safe subprocess execution for APT commands
- **File System**: Configuration storage in `~/.config/apt-ex-package-manager/`

### Security Technologies
- **Input Validation**: All user inputs sanitized
- **Command Sanitization**: Safe command-line argument handling
- **Package Verification**: Signature checking when possible
- **Secure Execution**: Controlled privilege escalation

## Platform Requirements

### Operating System
- **Target Platform**: Linux systems (APT-based distributions preferred)
- **Desktop Environment**: Optimized for KDE Plasma 6
- **Compatibility**: Works with other desktop environments
- **Package Systems**: APT (required), Flatpak (optional), AppImage (optional)

### System Dependencies
- APT package management system (required)
- Flatpak runtime (optional, for Flatpak support)
- Qt6 runtime libraries
- Python 3.8+ runtime
- Desktop notification system (optional)
- File manager integration for AppImage

### Integration Features
- KDE Breeze icon theme support
- System color scheme integration
- Desktop file associations
- Command-line interface compatibility