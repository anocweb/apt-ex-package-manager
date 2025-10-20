# Plugin Documentation

This directory contains documentation for each backend plugin in Apt-Ex Package Manager.

## Available Plugins

### [APT Plugin](apt/)
Package management for Debian-based systems using the Advanced Package Tool.

**Status**: ✅ Fully implemented  
**Capabilities**: search, install, remove, list_installed, list_updates, categories

### Flatpak Plugin (Planned)
Package management for Flatpak applications.

**Status**: 🚧 Planned  
**Documentation**: Coming soon

### AppImage Plugin (Planned)
Management for portable AppImage applications.

**Status**: 🚧 Planned  
**Documentation**: Coming soon

## Plugin Structure

Each plugin has its own directory containing:
- `README.md` - Plugin overview and capabilities
- Feature-specific documentation (e.g., `locking.md`, `caching.md`)
- Configuration examples
- Troubleshooting guides

## Plugin Development

For information on creating new plugins, see:
- [Plugin Architecture](../architecture/PLUGIN_ARCHITECTURE.md)
- [Plugin Development Rules](../../.amazonq/rules/plugin-development.md)
