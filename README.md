# Apt-Ex Package Manager

> **⚠️ PRE-ALPHA SOFTWARE**: This project is in early development. Features are incomplete and the application is not ready for production use. Use at your own risk for testing purposes only.

## Overview
Apt-Ex Package Manager is a modern user interface application designed to facilitate the management of the Advanced Package Tool (APT) on Linux systems. This application provides an intuitive graphical interface for users to install, remove, and update packages seamlessly.

## Project Structure
```
apt-ex-package-manager
├── src/                        # Application source code
├── docs/                       # Documentation files
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/anocweb/apt-ex-package-manager.git
cd apt-ex-package-manager
```

### 2. Create a virtual environment (recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Install system packages (optional, backend-specific)

**For APT backend (Debian/Ubuntu-based systems only)**:
```bash
sudo apt install python3-apt
```
Note: python-apt must be installed system-wide and cannot be installed via pip.

**For Flatpak backend (when implemented)**:
```bash
sudo apt install flatpak  # Debian/Ubuntu
# or
sudo dnf install flatpak  # Fedora
```

### 5. Run the application
```bash
python src/main.py
```

### Development Mode
Run with additional logging:
```bash
python src/main.py --dev-logging
```

## System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Linux (KDE Plasma 6 recommended)
- **Optional**: python3-apt (for APT backend on Debian/Ubuntu systems)

## Current Features
- **APT Package Management**: Browse, search, install, and remove APT packages
- **Category Browsing**: Navigate packages by APT sections (games, development, etc.)
- **Package Search**: Fast search across package names and descriptions
- **LMDB Caching**: High-performance caching for quick package access
- **KDE Plasma 6 Integration**: Native look and feel with system theme support
- **Context Actions**: Dynamic header buttons for page-specific operations
- **Plugin Architecture**: Extensible backend system for multiple package managers

## Planned Features
- **Multi-Backend Plugin Architecture**: Extensible system for multiple package managers
- **Flatpak Support**: Install and manage Flatpak applications
- **AppImage Support**: Manage portable AppImage applications
- **Unified Search**: Search across all package backends simultaneously
- **Repository Management**: GUI for managing APT sources and Flatpak remotes

## Documentation
- [Implementation Status](docs/STATUS.md) - What's working vs. planned
- [Documentation Index](docs/INDEX.md) - Complete documentation navigation
- [Feature Requirements](docs/features/FEATURES.md) - Feature specifications
- [Design Guidelines](docs/features/DESIGN_GUIDELINES.md) - KDE Plasma 6 integration
- [Database Architecture](docs/architecture/DATABASE_ARCHITECTURE.md) - LMDB caching system
- [AI-Assisted Development](docs/developer/AI_ASSISTED_DEVELOPMENT.md) - Guide for using AI tools

## Development Status
This is an active side project. APT support is functional, with plugin architecture and additional backends planned for future development. See [STATUS.md](docs/STATUS.md) for details.

## Contributing
Contributions are welcome! This is a personal project, but pull requests and issues are appreciated. Please check [STATUS.md](docs/STATUS.md) to see what's implemented vs. planned.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.