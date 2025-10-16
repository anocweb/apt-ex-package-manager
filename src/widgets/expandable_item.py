from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ExpandableItem(QWidget):
    """Reusable expandable item widget with collapsible content section"""
    
    def __init__(self, message: str, data: str = None, color=None):
        super().__init__()
        self.message = message
        self.data = data
        self.is_expanded = False
        
        self.setup_ui()
        if color:
            self.message_label.setStyleSheet(f"color: {color.name()};")
    
    def setup_ui(self):
        # Set secondary background color
        palette = self.palette()
        bg_color = palette.color(palette.ColorRole.AlternateBase)
        self.setStyleSheet(f"ExpandableItem {{ background-color: {bg_color.name()}; border-radius: 3px; }}")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(0)
        
        # Header with expand button and message
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Expand/collapse button
        self.expand_button = QPushButton()
        self.expand_button.setFixedSize(16, 16)
        self.expand_button.setFlat(True)
        self.expand_button.clicked.connect(self.toggle_expanded)
        
        if self.data:
            self.expand_button.setText("▶")
            self.expand_button.setToolTip("Click to expand data")
        else:
            self.expand_button.setText(" ")
            self.expand_button.setEnabled(False)
        
        header_layout.addWidget(self.expand_button)
        
        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        header_layout.addWidget(self.message_label, 1)
        
        layout.addLayout(header_layout)
        
        # Data section (initially hidden)
        if self.data:
            self.data_widget = QTextEdit()
            self.data_widget.setPlainText(self.data)
            self.data_widget.setReadOnly(True)
            self.data_widget.setMaximumHeight(0)  # Start collapsed
            
            # Use monospace font for JSON
            font = QFont("Consolas", 9)
            font.setStyleHint(QFont.StyleHint.Monospace)
            self.data_widget.setFont(font)
            
            # Set darker background for data section
            palette = self.palette()
            is_dark = palette.color(palette.ColorRole.Window).lightness() < 128
            if is_dark:
                data_bg_color = "#2a2a2a"  # Darker gray for dark theme
            else:
                data_bg_color = "#f5f5f5"  # Light gray for light theme
            self.data_widget.setStyleSheet(f"QTextEdit {{ background-color: {data_bg_color}; border: 1px solid #888; }}")
            
            layout.addWidget(self.data_widget)
        else:
            self.data_widget = None
    
    def toggle_expanded(self):
        """Toggle the expanded state of the data section"""
        if not self.data_widget:
            return
        
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.expand_button.setText("▼")
            self.expand_button.setToolTip("Click to collapse data")
            # Calculate height needed for data
            doc_height = self.data_widget.document().size().height()
            target_height = min(int(doc_height) + 10, 200)  # Max 200px
            self.data_widget.setMaximumHeight(target_height)
        else:
            self.expand_button.setText("▶")
            self.expand_button.setToolTip("Click to expand data")
            self.data_widget.setMaximumHeight(0)
    
    def set_message_color(self, color):
        """Set the color of the message text"""
        self.message_label.setStyleSheet(f"color: {color.name()};")