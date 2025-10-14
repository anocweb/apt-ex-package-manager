# Design Guidelines - KDE Discover-Inspired Package Manager

## KDE Discover-Inspired Design

### Overall User Experience
- Emulate KDE Discover's clean, modern interface
- Card-based layout for package display
- Smooth transitions and animations
- Unified experience across different package backends

### Visual Design Principles

#### Color Scheme
- Use KDE Plasma 6 system colors via `QPalette`
- Respect dark/light theme preferences
- Accent colors: Use `QPalette::Highlight` for primary actions
- Status colors: Green (success), Orange (warning), Red (error)
- Backend indicators: Subtle color coding for APT/Flatpak/AppImage

### Typography
- Primary font: System default (typically Noto Sans)
- Monospace font: For package names and technical details
- Font sizes: Follow KDE HIG scaling recommendations

### Layout & Spacing
- Use consistent 8px grid system
- Standard margins: 16px for main containers, 8px for sub-elements
- Button spacing: 8px between related buttons, 16px between groups

## Component Guidelines

### Windows & Dialogs
- Use `QMainWindow` with standard menu bar and status bar
- Modal dialogs for confirmations and settings
- Non-modal dialogs for progress and information
- Window icons: Use system theme icons

### Navigation (KDE Discover Style)
- Primary navigation: Left sidebar with categories (Featured, Applications, System)
- Package type filters: APT, Flatpak, AppImage toggles
- Search-first approach with prominent search bar
- Category browsing with visual cards
- Back/forward navigation for package details

### Controls (Discover-Inspired)
- Buttons: KDE standard styles with backend-specific install/remove actions
- Package cards: Grid layout similar to Discover's app cards
- Lists: `QListView` for detailed views with package type indicators
- Search: Prominent `QLineEdit` with instant results
- Package details: Full-screen overlay similar to Discover's detail view

### Icons & Visual Elements
- Use KDE Breeze icon theme
- Package type icons: `package-x-generic` (APT), `flatpak` (Flatpak), `application-x-executable` (AppImage)
- Action icons: `system-software-install`, `edit-delete`, `system-software-update`
- Size: 16px for indicators, 22px for toolbar, 48px for package cards, 64px for detail view
- Backend badges: Small overlay icons indicating package source

## Interaction Patterns

### Feedback
- Progress bars for operations >2 seconds
- Status messages in status bar
- Tooltips for complex controls
- Confirmation dialogs for destructive actions

### Keyboard Navigation
- Tab order follows logical flow
- Keyboard shortcuts for common actions
- Arrow key navigation in lists
- Enter/Space for activation

### Accessibility
- High contrast support
- Screen reader compatibility
- Keyboard-only operation
- Scalable UI elements

## KDE Integration

### System Integration
- Use KDE notification system (`KNotification`)
- Respect KDE global shortcuts
- Follow KDE application lifecycle
- Support KDE color schemes

### File Associations
- Register appropriate MIME types
- Provide desktop file with proper categories
- Support command-line arguments

### Settings
- Use `QSettings` with KDE-style organization
- Store preferences in `~/.config/apt-ex-package-manager/`
- Respect system-wide KDE settings

## Package Display Patterns

### Package Cards (Grid View)
- Card size: 200x120px minimum, scalable
- Package icon: 48x48px with backend badge overlay
- Title: Package name in bold
- Subtitle: One-line description
- Footer: Backend indicator and install status
- Hover effects: Subtle elevation and highlight

### Package Detail View (Discover-Style)
- Full-screen overlay with close button
- Large package icon (128x128px) with screenshots
- Tabbed information: Overview, Details, Reviews (future)
- Backend-specific metadata sections
- Prominent install/remove/update buttons
- Related packages suggestions

### Backend Integration Indicators
- APT: Blue accent with package icon
- Flatpak: Green accent with Flatpak logo
- AppImage: Orange accent with executable icon
- Status badges: Installed, Available, Update Available
- Source information: Repository/remote name

## Multi-Backend UX Patterns

### Unified Search Results
- Mixed results from all backends
- Backend filtering toggles
- Sort by relevance, name, or backend
- Clear indication of package source
- Consistent card layout regardless of backend

### Installation Workflows
- Backend-appropriate confirmation dialogs
- Progress indicators with backend-specific messaging
- Error handling with backend context
- Post-installation actions (APT: dependencies, Flatpak: permissions)