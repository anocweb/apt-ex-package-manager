# Panels and Virtual Scrolling Architecture

## Panel System

### Panel Loading Pattern
Panels are loaded from UI files and managed by MainView:

```python
def load_panels(self):
    """Load all panel UI files and add them to the content stack"""
    panel_files = {
        'home': 'home_panel.ui',
        'installed': 'installed_panel.ui',
        'updates': 'updates_panel.ui',
        'category': 'category_panel.ui',
        'settings': 'settings_panel.ui',
        'about': 'about_panel.ui'
    }
    
    for panel_name, ui_file in panel_files.items():
        panel_widget = QWidget()
        ui_path = os.path.join('src', 'ui', ui_file)
        uic.loadUi(ui_path, panel_widget)
        self.panels[panel_name] = panel_widget
        self.contentStack.addWidget(panel_widget)
```

### Panel Navigation
```python
def select_page(self, page_key: str):
    """Switch to specified panel"""
    if page_key in self.panels:
        self.contentStack.setCurrentWidget(self.panels[page_key])
        self.update_page_title(page_key)
        self.clear_context_actions()
        self.setup_page_context_actions(page_key)
```

### Panel Structure
Each panel typically contains:
- **Search/Filter UI**: Input fields for user queries
- **Content Container**: Scroll area or virtual container for results
- **Worker Thread**: Background data loading
- **Signal Connections**: Link UI events to data operations

## Virtual Scrolling Pattern

### Why Virtual Scrolling?
Creating thousands of Qt widgets on the main thread causes UI freezing. Virtual scrolling only creates widgets for visible items (~10-20 at a time).

**Performance Comparison**:
- Traditional: 2,400 widgets = UI freeze for 5-10 seconds
- Virtual scrolling: 10-20 widgets = instant response

### Virtual Container Implementation

#### Core Components
```python
class VirtualInstalledContainer(QScrollArea):
    def __init__(self):
        super().__init__()
        self.all_packages = []           # Full dataset
        self.visible_widgets = {}        # Currently rendered widgets
        self.item_height = 125           # Fixed item height
        self.viewport_buffer = 3         # Extra items above/below viewport
```

#### Key Methods
```python
def set_packages(self, packages):
    """Set full dataset and trigger render"""
    self.all_packages = packages
    self.schedule_update()

def perform_update(self):
    """Render only visible items"""
    # Calculate visible range
    viewport_top = self.verticalScrollBar().value()
    viewport_height = self.viewport().height()
    first_visible = (viewport_top // self.item_height) - self.viewport_buffer
    last_visible = ((viewport_top + viewport_height) // self.item_height) + self.viewport_buffer
    
    # Skip if range unchanged
    if current_range == existing_range:
        return
    
    # Create spacers and visible widgets
    # Top spacer: first_visible * item_height
    # Visible widgets: first_visible to last_visible
    # Bottom spacer: remaining_items * item_height
```

### Virtual Scrolling Parameters

#### Item Height
Must match the UI file design height:
```python
self.item_height = 125  # Match installed_list_item.ui height
```

#### Viewport Buffer
Number of extra items to render above/below viewport:
```python
self.viewport_buffer = 3  # Render 3 extra items on each side
```
- Lower value = fewer widgets, more frequent updates
- Higher value = more widgets, smoother scrolling
- Recommended: 2-5 items

#### Update Delay
Debounce timer to reduce update frequency:
```python
self.update_timer.start(50)  # 50ms delay
```
- Lower value = more responsive, more CPU usage
- Higher value = less responsive, less CPU usage
- Recommended: 50-100ms

### Panel Integration Pattern

#### Worker Thread for Data Loading
```python
class InstalledPackagesWorker(QThread):
    initial_loaded = pyqtSignal(list)
    remaining_loaded = pyqtSignal(list)
    
    def run(self):
        # Load initial batch (20 packages)
        initial = packages[:20]
        self.initial_loaded.emit(initial)
        
        # Load remaining in batches (50 at a time)
        for i in range(20, total, 50):
            batch = packages[i:i+50]
            self.remaining_loaded.emit(batch)
```

#### Panel Setup
```python
class InstalledPanel:
    def setup_ui(self):
        # Create virtual container
        self.virtual_container = VirtualInstalledContainer()
        self.virtual_container.remove_requested.connect(self.on_remove_package)
        
        # Replace scroll area in layout
        layout.replaceWidget(old_scroll_area, self.virtual_container)
    
    def load_packages(self):
        # Start worker thread
        self.worker = InstalledPackagesWorker(self.package_manager)
        self.worker.initial_loaded.connect(self.on_initial_loaded)
        self.worker.remaining_loaded.connect(self.on_remaining_loaded)
        self.worker.start()
    
    def on_initial_loaded(self, packages):
        # Show first batch immediately
        self.virtual_container.set_packages(packages)
    
    def on_remaining_loaded(self, packages):
        # Add remaining batches
        self.virtual_container.add_packages(packages)
```

## Existing Virtual Containers

### VirtualInstalledContainer
- **Location**: `src/widgets/virtual_installed_container.py`
- **Purpose**: Display installed packages list
- **Item Height**: 125px
- **Widget**: InstalledListItem
- **Signals**: remove_requested

### VirtualCategoryContainer
- **Location**: `src/widgets/virtual_category_container.py`
- **Purpose**: Display category package lists
- **Item Height**: Variable (depends on item type)
- **Widget**: PackageListItem

### VirtualLogContainer
- **Location**: `src/widgets/virtual_log_container.py`
- **Purpose**: Display application logs
- **Item Height**: Variable (text-based)
- **Widget**: Log entry labels

## When to Use Virtual Scrolling

### Use Virtual Scrolling When:
- Displaying 100+ items in a list
- Items have fixed or predictable heights
- Creating widgets is expensive (complex UI)
- Users need to scroll through large datasets

### Use Traditional Scrolling When:
- Displaying < 50 items
- Items have highly variable heights
- Items are simple (single label/button)
- List is paginated or filtered to small size

## Performance Guidelines

### Virtual Scrolling Best Practices
1. **Fixed Heights**: Use fixed item heights for predictable layout
2. **Minimal Buffer**: Keep viewport_buffer small (2-5 items)
3. **Debounce Updates**: Use 50-100ms timer delay
4. **Range Checking**: Skip updates when visible range unchanged
5. **Batch Loading**: Load data in background thread with batches

### Avoid Common Pitfalls
- Don't call `setFixedHeight()` on individual widgets (let UI file control height)
- Don't update on every scroll pixel (use debounce timer)
- Don't create all widgets upfront (defeats purpose of virtual scrolling)
- Don't use variable heights without recalculating positions

## Testing Virtual Scrolling

### Manual Testing Checklist
- [ ] Scroll smoothly without lag
- [ ] Items display at correct height (not squished)
- [ ] No visual gaps or overlaps
- [ ] Scroll to top/bottom works correctly
- [ ] Resize window updates layout
- [ ] Large datasets (1000+ items) remain responsive

### Performance Metrics
- Initial render: < 100ms
- Scroll update: < 50ms
- Memory usage: ~10-20 widgets regardless of dataset size
- CPU usage: Minimal during idle scrolling
