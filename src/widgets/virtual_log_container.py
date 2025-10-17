from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from widgets.expandable_item import ExpandableItem

class VirtualLogContainer(QScrollArea):
    """Virtual scrolling container for log entries"""
    
    def __init__(self, logging_service):
        super().__init__()
        self.logging_service = logging_service
        self.all_log_entries = []  # All log data
        self.filtered_entries = []  # Filtered log data
        self.visible_widgets = {}  # index -> ExpandableItem
        self.expanded_items = set()  # Indices of expanded items
        self.selected_items = set()  # Indices of selected items
        
        # Virtual scrolling parameters
        self.item_height = 30  # Estimated height per item
        self.viewport_buffer = 5  # Extra items above/below viewport
        
        # Setup container
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(1)
        
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        
        # Connect scroll events
        self.verticalScrollBar().valueChanged.connect(self.update_visible_widgets)
        
        # Update timer to batch updates
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.perform_update)
    
    def set_log_entries(self, entries, colors):
        """Set log entries and trigger virtual scrolling update"""
        self.all_log_entries = entries
        self.colors = colors
        self.schedule_update()
    
    def set_filtered_entries(self, entries):
        """Set filtered entries and update display"""
        self.filtered_entries = entries
        self.schedule_update()
    
    def schedule_update(self):
        """Schedule a virtual scrolling update"""
        self.update_timer.stop()
        self.update_timer.start(10)  # 10ms delay to batch updates
    
    def perform_update(self):
        """Perform the actual virtual scrolling update"""
        # Clear existing widgets
        for widget in list(self.visible_widgets.values()):
            widget.setParent(None)
        self.visible_widgets.clear()
        
        # Clear layout
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        # Calculate visible range based on current scroll position
        viewport_top = self.verticalScrollBar().value()
        viewport_height = self.viewport().height()
        
        if len(self.filtered_entries) == 0:
            return
        
        # Simple approach: show all filtered entries for now
        # This can be optimized later for very large lists
        for i, entry in enumerate(self.filtered_entries):
            widget = self.create_widget_for_entry(entry, i)
            self.container_layout.addWidget(widget)
            self.visible_widgets[i] = widget
        
        # Add stretch to push items to top
        self.container_layout.addStretch()
    
    def create_widget_for_entry(self, entry, index):
        """Create ExpandableItem widget for log entry"""
        # Handle both old string format and new dict format
        if isinstance(entry, dict):
            message = entry['message']
            data = entry.get('data')
        else:
            message = entry
            data = None
        
        # Extract log level for color
        level = 'INFO'
        for lvl in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']:
            if lvl in message:
                level = lvl
                break
        
        color = self.colors.get(level, self.colors['INFO'])
        
        # Create widget
        widget = ExpandableItem(message, data, color, self.logging_service)
        widget.selection_changed.connect(lambda w: self.on_item_selected(w, index))
        
        # Restore state
        if index in self.expanded_items:
            widget.is_expanded = True
            widget.toggle_expanded()
        
        if index in self.selected_items:
            widget.set_selected(True)
        
        return widget
    
    def on_item_selected(self, widget, index):
        """Handle item selection"""
        from PyQt6.QtWidgets import QApplication
        
        # Check if Ctrl was held (multi-select mode)
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Multi-select: toggle selection
            if index in self.selected_items:
                widget.set_selected(False)
                self.selected_items.remove(index)
            else:
                widget.set_selected(True)
                self.selected_items.add(index)
        else:
            # Single-select: clear others and select this one
            self.clear_all_selections()
            widget.set_selected(True)
            self.selected_items.add(index)
    
    def clear_all_selections(self):
        """Clear all selections"""
        for widget in self.visible_widgets.values():
            widget.set_selected(False)
        self.selected_items.clear()
    
    def update_visible_widgets(self):
        """Update visible widgets when scrolling"""
        # For now, we're showing all items, so no need to update on scroll
        # This can be optimized later for true virtual scrolling
        pass
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        self.schedule_update()
    
    def get_selected_widgets(self):
        """Get currently selected widgets for context menu operations"""
        selected_widgets = []
        for index in self.selected_items:
            if index in self.visible_widgets:
                selected_widgets.append(self.visible_widgets[index])
        return selected_widgets