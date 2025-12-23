"""Backend preference list item widget with enable checkbox and drag handle"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QLabel, QToolTip
from PyQt6.QtCore import pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QCursor


class BackendPreferenceItem(QWidget):
    """Custom widget for backend preference list item"""
    
    enabled_changed = pyqtSignal(str, bool)  # backend_id, enabled
    
    def __init__(self, backend_id, display_name, enabled=True, status=None, parent=None):
        super().__init__(parent)
        self.backend_id = backend_id
        self.status = status
        
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
        
        # Status icon
        if status and (status.get('missing_system_deps') or status.get('missing_python_deps')):
            # Warning icon for issues
            self.status_icon = QLabel("⚠")
            self.status_icon.setStyleSheet("font-size: 16px; color: #FFA500;")
            self.status_icon.setCursor(Qt.CursorShape.PointingHandCursor)
            self.status_icon.mousePressEvent = self.show_warning_tooltip
            layout.addWidget(self.status_icon)
        else:
            # Info icon for healthy plugins
            self.status_icon = QLabel("ⓘ")
            self.status_icon.setStyleSheet("font-size: 16px; color: palette(mid);")
            self.status_icon.setCursor(Qt.CursorShape.PointingHandCursor)
            self.status_icon.mousePressEvent = self.show_info_tooltip
            layout.addWidget(self.status_icon)
    
    def show_info_tooltip(self, event):
        """Show tooltip with plugin info"""
        tooltip_text = "Plugin is working correctly\nAll dependencies satisfied"
        QToolTip.showText(QCursor.pos(), tooltip_text, self)
    
    def show_warning_tooltip(self, event):
        """Show tooltip with dependency issues"""
        if not self.status:
            return
        
        issues = []
        if self.status.get('missing_system_deps'):
            issues.append("Missing system dependencies:")
            for dep in self.status['missing_system_deps']:
                issues.append(f"  • {dep}")
        
        if self.status.get('missing_python_deps'):
            if issues:
                issues.append("")
            issues.append("Missing Python dependencies:")
            for dep in self.status['missing_python_deps']:
                issues.append(f"  • {dep}")
        
        tooltip_text = "\n".join(issues)
        QToolTip.showText(QCursor.pos(), tooltip_text, self)
