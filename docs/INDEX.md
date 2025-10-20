# Documentation Index

## Quick Start
- [README](../README.md) - Project overview and setup
- [Implementation Status](STATUS.md) - What's working vs. planned
- [Development Guide](DEVELOPMENT.md) - Setup and architecture
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [INSTALL](../INSTALL.md) - Installation instructions

## Features
- [Features](features/FEATURES.md) - Feature specifications and status
- [Design Guidelines](features/DESIGN_GUIDELINES.md) - KDE Plasma 6 UI guidelines
- [Context Actions](features/CONTEXT_ACTIONS.md) - Header action system
- [APT Section Mapping](features/APT_SECTION_MAPPING.md) - Category mapping

## Architecture
- [Startup Workflow](architecture/STARTUP_WORKFLOW.md) - Application initialization sequence
- [View Architecture](architecture/VIEW_ARCHITECTURE.md) - Panel controllers and worker threads
- [Panels and Scrolling](architecture/PANELS_AND_SCROLLING.md) - Panel system and virtual scrolling
- [Database Architecture](architecture/DATABASE_ARCHITECTURE.md) - LMDB caching system
- [Plugin Architecture](architecture/PLUGIN_ARCHITECTURE.md) - Multi-backend plugin system
- [MVC Architecture](architecture/MVC_REFACTOR_ARCHITECTURE.md) - Application controller and services
- [Service Container](architecture/SERVICE_CONTAINER.md) - Dependency injection
- [Data Structures](architecture/DATA_STRUCTURES.md) - Data models
- [Repository Implementation](architecture/REPOSITORY_IMPLEMENTATION.md) - Repository management

## Plugins
- [Plugin Documentation](plugins/) - Backend plugin documentation
  - [APT Plugin](plugins/apt/) - APT package management

## Developer Guides
- [Panel Development Guide](developer/PANEL_DEVELOPMENT_GUIDE.md) - Creating new panels
- [AI-Assisted Development](developer/AI_ASSISTED_DEVELOPMENT.md) - Using AI tools
- [MVC Quick Reference](developer/MVC_QUICK_REFERENCE.md) - Working with MVC architecture

## Planning
- [Privilege Escalation Implementation](planning/PRIVILEGE_ESCALATION_IMPLEMENTATION.md) - PolicyKit + D-Bus helper system
- [Privilege Escalation Quick Reference](planning/PRIVILEGE_ESCALATION_QUICK_REF.md) - Quick reference guide

## Implementation Notes
- [Refactoring Summary](REFACTORING_SUMMARY.md) - View architecture refactoring
- [Widget Standardization](WIDGET_STANDARDIZATION.md) - List item widget improvements

## Examples
- [Plugin Example](examples/PLUGIN_EXAMPLE.md) - Reference plugin implementation

## Plugin-Specific Documentation
Each plugin has its own documentation directory under `plugins/`:
- **APT**: Lock management, caching, category mapping
- **Flatpak**: Coming soon
- **AppImage**: Coming soon
