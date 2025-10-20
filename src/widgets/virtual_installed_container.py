"""Virtual scrolling container for installed packages"""
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from widgets.installed_list_item import InstalledListItem


class VirtualInstalledContainer(QScrollArea):
    """Virtual scrolling container for installed packages"""
    
    remove_requested = pyqtSignal(str)
    package_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.all_packages = []
        self.visible_widgets = {}
        
        # Virtual scrolling parameters
        self.item_height = 125
        self.viewport_buffer = 3
        
        # Setup container
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Connect scroll events
        self.verticalScrollBar().valueChanged.connect(self.update_visible_widgets)
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.perform_update)
    
    def set_packages(self, packages):
        """Set packages and trigger update"""
        self.all_packages = packages
        self.schedule_update()
    
    def add_packages(self, packages):
        """Add more packages"""
        self.all_packages.extend(packages)
        # Don't update display for every batch
    
    def schedule_update(self):
        """Schedule update"""
        self.update_timer.stop()
        self.update_timer.start(50)
    
    def perform_update(self):
        """Perform virtual scrolling update"""
        if not self.all_packages:
            return
        
        # Calculate visible range
        viewport_top = self.verticalScrollBar().value()
        viewport_height = self.viewport().height()
        viewport_bottom = viewport_top + viewport_height
        
        first_visible = max(0, (viewport_top // self.item_height) - self.viewport_buffer)
        last_visible = min(len(self.all_packages) - 1,
                          ((viewport_bottom // self.item_height) + self.viewport_buffer))
        
        # Check if range changed significantly
        current_range = set(range(first_visible, last_visible + 1))
        existing_range = set(self.visible_widgets.keys())
        
        if current_range == existing_range:
            return  # No change needed
        
        # Clear existing widgets
        for widget in self.visible_widgets.values():
            widget.setParent(None)
        self.visible_widgets.clear()
        
        # Clear layout
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        # Calculate total height
        total_height = len(self.all_packages) * self.item_height
        self.container.setFixedHeight(total_height)
        
        # Top spacer
        if first_visible > 0:
            top_spacer = QWidget()
            top_spacer.setFixedHeight(first_visible * self.item_height)
            self.container_layout.addWidget(top_spacer)
        
        # Create visible widgets
        for i in range(first_visible, last_visible + 1):
            if i < len(self.all_packages):
                pkg_info = self.all_packages[i]
                widget = InstalledListItem(pkg_info)
                widget.remove_requested.connect(self.remove_requested.emit)
                widget.double_clicked.connect(lambda p=pkg_info: self.package_selected.emit(p))
                self.container_layout.addWidget(widget)
                self.visible_widgets[i] = widget
        
        # Bottom spacer
        remaining_items = len(self.all_packages) - (last_visible + 1)
        if remaining_items > 0:
            bottom_spacer = QWidget()
            bottom_spacer.setFixedHeight(remaining_items * self.item_height)
            self.container_layout.addWidget(bottom_spacer)
    
    def update_visible_widgets(self):
        """Update on scroll"""
        self.schedule_update()
    
    def resizeEvent(self, event):
        """Handle resize"""
        super().resizeEvent(event)
        self.schedule_update()
