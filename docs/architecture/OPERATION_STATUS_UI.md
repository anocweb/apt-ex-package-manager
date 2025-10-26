# Operation Status UI Architecture

## Overview
The operation status UI provides real-time feedback for package operations (install, remove, update) without blocking the main interface. It uses a hybrid approach combining a collapsible status bar with a resizable overlay panel.

## Components

### 1. OperationStatusBar
**Location**: Bottom of main window  
**Height**: 40px (fixed)  
**Visibility**: Shows during operations, auto-hides 3 seconds after completion

**Elements**:
- **Spinner**: Animated spinner (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏) showing operation in progress
- **Status Text**: "Installing package-name..." or "Removing package-name..."
- **Expand Button**: "▲ Show Details" - expands overlay panel
- **Completion Icon**: ✓ (success) or ✗ (failure) when operation completes

**States**:
- **Hidden**: No operation in progress
- **Active**: Operation running, spinner animating
- **Complete**: Shows result for 3 seconds, then auto-hides

### 2. OperationPanel (Overlay)
**Location**: Slides up from bottom, overlays main content  
**Default Height**: 300px  
**Resizable**: Yes (150px min, 80% of window max)  
**Visibility**: Hidden by default, shown when user clicks expand

**Elements**:
- **Drag Handle**: 6px bar at top for resizing (cursor changes to resize)
- **Title**: "Installing package-name" or "Removing package-name"
- **Command Label**: Shows full command being executed (e.g., "pkexec apt-get install vim")
- **Output Text Area**: Scrollable, monospace font, shows real-time command output
- **Collapse Button**: "▼ Collapse" - returns to status bar only view

**Behavior**:
- Slides up with animation (200ms, ease-out)
- Slides down with animation (200ms, ease-in)
- User can drag top edge to resize
- Auto-scrolls output to bottom as new lines arrive
- Persists size preference during session

## User Flows

### Flow 1: Install Package (Minimal Interaction)
1. User clicks "Install" on package
2. Status bar appears at bottom with spinner
3. Operation completes
4. Status bar shows "✓ Installed package-name" for 3 seconds
5. Status bar auto-hides

### Flow 2: Install Package (View Details)
1. User clicks "Install" on package
2. Status bar appears at bottom with spinner
3. User clicks "▲ Show Details"
4. Overlay panel slides up showing command and output
5. User watches real-time output
6. Operation completes, output shows "✓ Operation completed successfully"
7. User clicks "▼ Collapse" or clicks backdrop
8. Overlay slides down, status bar remains
9. Status bar auto-hides after 3 seconds

### Flow 3: Install Package (Resize Panel)
1. User expands overlay panel
2. User drags top edge of panel up/down
3. Panel resizes to user preference
4. Size persists for session

### Flow 4: Error Handling
1. Operation fails (e.g., package not found)
2. Status bar shows "✗ Failed: Installing package-name"
3. If overlay is open, shows error output
4. Status bar remains visible (doesn't auto-hide on error)
5. User can review error details in overlay

## Integration with Main Window

### MainWindow Structure
```
QMainWindow
├── centralWidget
│   ├── contentStack (existing panels)
│   ├── operationPanel (overlay, z-index above content)
│   └── operationStatusBar (bottom, always on top)
```

### Signal Flow
```
User Action (Install/Remove)
    ↓
PackageOperationWorker.start()
    ↓
worker.command_started → OperationStatusBar.start_operation()
                      → OperationPanel.set_operation()
    ↓
worker.output_line → OperationPanel.append_output()
    ↓
worker.finished → OperationStatusBar.set_complete()
               → OperationPanel.set_complete()
```

## Technical Implementation

### Worker Thread (PackageOperationWorker)
**Signals**:
- `command_started(str)`: Emitted when command starts, passes full command string
- `output_line(str)`: Emitted for each line of output from subprocess
- `finished(bool, str)`: Emitted when operation completes (success, package_name)
- `error(str)`: Emitted on exception

**Implementation**:
- Uses `subprocess.Popen()` for real-time output
- Reads stdout/stderr line by line
- Emits each line immediately (no buffering)
- Non-blocking for UI thread

### Animation
**Expand Animation**:
- Duration: 200ms
- Easing: OutCubic (fast start, slow end)
- Property: position (y-coordinate)

**Collapse Animation**:
- Duration: 200ms
- Easing: InCubic (slow start, fast end)
- Property: position (y-coordinate)

### Resizing
**Drag Handle**:
- Cursor changes to SizeVerCursor on hover
- Mouse press captures start position and height
- Mouse move calculates delta and updates height
- Constrained to min/max bounds
- Mouse release ends resize

**Constraints**:
- Minimum height: 150px
- Maximum height: 80% of window height
- Width: Always matches window width

## Styling

### Status Bar
```css
#operationStatusBar {
    background: palette(window);
    border-top: 1px solid palette(mid);
}
```

### Overlay Panel
```css
#operationPanel {
    background: palette(base);
    border-top: 2px solid palette(mid);
}

#dragHandle {
    background: palette(mid);
}

#dragHandle:hover {
    background: palette(highlight);
}
```

### Output Text
- Font: Monospace, 9pt
- Read-only
- Auto-scroll to bottom
- Preserves ANSI color codes (future enhancement)

## Accessibility

### Keyboard Support
- **Escape**: Collapse overlay panel
- **Ctrl+Shift+O**: Toggle overlay panel (future)

### Screen Reader
- Status bar announces operation start/completion
- Output text is accessible to screen readers
- Buttons have clear labels

## Future Enhancements

### Planned Features
1. **Operation Queue**: Show multiple operations in status bar
2. **ANSI Color Support**: Preserve colored output from apt
3. **Progress Bar**: Show download/install progress percentage
4. **Cancel Button**: Allow user to cancel operation
5. **History**: Keep log of recent operations
6. **Notifications**: Desktop notifications for completion

### Potential Improvements
1. **Detachable Panel**: Allow panel to be detached as separate window
2. **Multiple Operations**: Show multiple operations simultaneously
3. **Operation Pause/Resume**: Pause long-running operations
4. **Smart Auto-Expand**: Auto-expand on errors or prompts

## Design Rationale

### Why Overlay Instead of Modal?
- **Non-blocking**: User can browse packages while installing
- **Contextual**: Stays visible but doesn't dominate screen
- **Flexible**: User controls visibility and size

### Why Status Bar + Overlay?
- **Progressive Disclosure**: Minimal by default, detailed on demand
- **Always Accessible**: Status bar always shows current state
- **User Control**: User decides when to see details

### Why Resizable?
- **User Preference**: Different users want different amounts of detail
- **Adaptive**: Works on different screen sizes
- **Persistent**: Size preference maintained during session

## Related Documentation
- [Worker Threads](WORKER_THREADS.md)
- [Signal/Slot Patterns](../developer/SIGNAL_SLOT_PATTERNS.md)
- [UI Components](UI_COMPONENTS.md)
