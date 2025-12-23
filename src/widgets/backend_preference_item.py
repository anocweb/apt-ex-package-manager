"""Backend preference list item widget with enable checkbox and drag handle"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QLabel
from PyQt6.QtCore import pyqtSignal, Qt


class BackendPreferenceItem(QWidget):
    """Custom widget for backend preference list item"""
    
    enabled_changed = pyqtSignal(str, bool)  # backend_id, enabled
    
    def __init__(self, backend_id, display_name, enabled=True, parent=None):
        super().__init__(parent)
        self.backend_id = backend_id
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Drag handle icon
        drag_icon = QLabel("☰")
        drag_icon.setStyleSheet("font-size: 16px; color: palette(mid);")
        layout.addWidget(drag_icon)
        
        # Enable checkbox
        self.checkbox = QCheckBox(display_name)
        self.checkbox.setChecked(enabled)
        self.checkbox.toggled.connect(lambda checked: self.enabled_changed.emit(self.backend_id, checked))
        layout.addWidget(self.checkbox)
        
        layout.addStretch()
