from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QMainWindow
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from widgets.package_list_item import PackageListItem

class VirtualCategoryContainer(QScrollArea):
    """Virtual scrolling container for category packages"""
    
    install_requested = pyqtSignal(str)  # Signal for install requests
    
    def __init__(self, odrs_service=None):
        super().__init__()
        self.odrs_service = odrs_service
        self.all_packages = []
        self.visible_widgets = {}  # index -> PackageListItem
        
        # Virtual scrolling parameters
        self.item_height = 125  # Height per package item with margin and proper text space
        self.viewport_buffer = 3  # Extra items above/below viewport
        
        # Setup container
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        self.container_layout.setSpacing(2)
        
        self.setWidget(self.container)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Connect scroll events
        self.verticalScrollBar().valueChanged.connect(self.update_visible_widgets)
        
        # Update timer to batch updates
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.perform_update)
    
    def set_packages(self, packages):
        """Set packages and trigger virtual scrolling update"""
        self.all_packages = packages
        self.schedule_update()
    
    def schedule_update(self):
        """Schedule a virtual scrolling update"""
        self.update_timer.stop()
        self.update_timer.start(10)  # 10ms delay to batch updates
    
    def perform_update(self):
        """Perform the actual virtual scrolling update"""
        # Clear existing widgets
        for widget in self.visible_widgets.values():
            widget.setParent(None)
        self.visible_widgets.clear()
        
        # Clear layout
        while self.container_layout.count():
            child = self.container_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        if not self.all_packages:
            return
        
        # Calculate total height needed
        total_height = len(self.all_packages) * self.item_height
        self.container.setFixedHeight(total_height)
        
        # Calculate visible range
        viewport_top = self.verticalScrollBar().value()
        viewport_height = self.viewport().height()
        viewport_bottom = viewport_top + viewport_height
        
        # Calculate which items should be visible
        first_visible = max(0, (viewport_top // self.item_height) - self.viewport_buffer)
        last_visible = min(len(self.all_packages) - 1, 
                          ((viewport_bottom // self.item_height) + self.viewport_buffer))
        
        # Add spacer for items above visible range
        if first_visible > 0:
            top_spacer = QWidget()
            top_spacer.setFixedHeight(first_visible * self.item_height)
            self.container_layout.addWidget(top_spacer)
        
        # Create widgets for visible items
        for i in range(first_visible, last_visible + 1):
            if i < len(self.all_packages):
                package = self.all_packages[i]
                widget = PackageListItem(package, self.odrs_service)
                widget.install_requested.connect(self.on_install_requested)
                widget.setFixedHeight(self.item_height)
                self.container_layout.addWidget(widget)
                self.visible_widgets[i] = widget
        
        # Add spacer for items below visible range
        remaining_items = len(self.all_packages) - (last_visible + 1)
        if remaining_items > 0:
            bottom_spacer = QWidget()
            bottom_spacer.setFixedHeight(remaining_items * self.item_height)
            self.container_layout.addWidget(bottom_spacer)
    
    def update_visible_widgets(self):
        """Update visible widgets when scrolling"""
        self.schedule_update()
    
    def on_install_requested(self, package_name):
        """Forward install request signal"""
        self.install_requested.emit(package_name)
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        self.schedule_update()