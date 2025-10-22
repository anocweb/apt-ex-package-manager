"""Widget for managing backend priority order"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QListWidgetItem)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import List, Dict


class BackendPriorityWidget(QWidget):
    """Reorderable list widget for backend priority management"""
    
    priority_changed = pyqtSignal(list)  # Emits ordered list of backend IDs
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backend_map = {}  # backend_id -> display_name
        self.setup_ui()
    
    def setup_ui(self):
        """Setup widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget.model().rowsMoved.connect(self.on_order_changed)
        layout.addWidget(self.list_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.up_button = QPushButton("↑ Move Up")
        self.down_button = QPushButton("↓ Move Down")
        
        self.up_button.clicked.connect(self.move_up)
        self.down_button.clicked.connect(self.move_down)
        
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.down_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        self.list_widget.currentRowChanged.connect(self.update_button_states)
        self.update_button_states()
    
    def set_backends(self, backends: List[Dict[str, str]]):
        """Set available backends
        
        Args:
            backends: List of dicts with 'id' and 'display_name' keys
        """
        self.list_widget.clear()
        self.backend_map.clear()
        
        for backend in backends:
            backend_id = backend['id']
            display_name = backend['display_name']
            self.backend_map[backend_id] = display_name
            
            item = QListWidgetItem(f"≡ {display_name}")
            item.setData(Qt.ItemDataRole.UserRole, backend_id)
            self.list_widget.addItem(item)
    
    def get_priority_order(self) -> List[str]:
        """Get current priority order as list of backend IDs"""
        order = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            backend_id = item.data(Qt.ItemDataRole.UserRole)
            order.append(backend_id)
        return order
    
    def set_priority_order(self, backend_ids: List[str]):
        """Set priority order from list of backend IDs"""
        # Build map of current items
        items_data = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            backend_id = item.data(Qt.ItemDataRole.UserRole)
            display_name = self.backend_map.get(backend_id, backend_id)
            items_data.append((backend_id, display_name))
        
        # Clear and rebuild
        self.list_widget.clear()
        
        for backend_id in backend_ids:
            # Find matching backend
            for bid, display_name in items_data:
                if bid == backend_id:
                    item = QListWidgetItem(f"≡ {display_name}")
                    item.setData(Qt.ItemDataRole.UserRole, backend_id)
                    self.list_widget.addItem(item)
                    break
    
    def move_up(self):
        """Move selected item up"""
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row - 1, item)
            self.list_widget.setCurrentRow(current_row - 1)
            self.on_order_changed()
    
    def move_down(self):
        """Move selected item down"""
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(current_row)
            self.list_widget.insertItem(current_row + 1, item)
            self.list_widget.setCurrentRow(current_row + 1)
            self.on_order_changed()
    
    def update_button_states(self):
        """Update enabled state of up/down buttons"""
        current_row = self.list_widget.currentRow()
        self.up_button.setEnabled(current_row > 0)
        self.down_button.setEnabled(current_row >= 0 and current_row < self.list_widget.count() - 1)
    
    def on_order_changed(self):
        """Emit signal when order changes"""
        self.priority_changed.emit(self.get_priority_order())
