# Apt-Ex Package Manager

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
1. Clone the repository:
   ```
   git clone <repository-url>
   cd apt-ex-package-manager
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Current Features
- **APT Package Management**: Browse, search, install, and remove APT packages
- **Category Browsing**: Navigate packages by APT sections (games, development, etc.)
- **Package Search**: Fast search across package names and descriptions
- **LMDB Caching**: High-performance caching for quick package access
- **KDE Plasma 6 Integration**: Native look and feel with system theme support
- **Context Actions**: Dynamic header buttons for page-specific operations

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