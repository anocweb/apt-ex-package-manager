# Apt-Ex Package Manager Development Rules

> **Note**: Comprehensive project information is available in the Memory Bank files (product.md, structure.md, tech.md, guidelines.md).

## Project Standards
- Project name: "Apt-Ex Package Manager" (not apt-qt6-manager)
- Store settings in `~/.config/apt-ex-package-manager/`

## Multi-Backend Integration Requirements
- **Primary Backend**: APT with full feature support
- **Secondary Backend**: Flatpak with repository management
- **Tertiary Backend**: AppImage with file integration
- Implement asynchronous operations to prevent UI freezing
- Handle privilege escalation with sudo/pkexec (APT)
- Provide progress indicators for operations >2 seconds
- Include confirmation dialogs for destructive actions
- Support unified search, install, remove, update across all backends

## KDE Discover-Inspired UX Requirements
- Card-based package display similar to Discover
- Smooth navigation with back/forward support
- Full-screen package detail overlays
- Category-based browsing with visual appeal
- Search-first approach with prominent search bar
- Backend indicators (APT/Flatpak/AppImage badges)

## Accessibility Requirements
- Support keyboard navigation and shortcuts
- Provide tooltips for complex controls
- Ensure high contrast support
- Make UI scalable for different screen sizes

## Documentation Maintenance
- Keep Amazon Q rules synchronized with docs/FEATURES.md and docs/DESIGN_GUIDELINES.md
- Update .amazonq/rules/ when project documentation changes
- Ensure consistency between documentation and development rules