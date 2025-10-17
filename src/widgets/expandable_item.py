from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QMenu, QApplication
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class ExpandableItem(QWidget):
    """Reusable expandable item widget with collapsible content section"""
    
    selection_changed = pyqtSignal(object)  # Signal when this item is selected
    
    # Class-level style cache
    _styles_computed = False
    _cached_styles = {}
    
    @classmethod
    def _compute_styles(cls):
        """Compute and cache all styles once"""
        if cls._styles_computed:
            return
        
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            return
        
        palette = app.palette()
        is_dark = palette.color(palette.ColorRole.Window).lightness() < 128
        
        if is_dark:
            bg_normal = palette.color(palette.ColorRole.AlternateBase).darker(110).name()
            bg_selected = palette.color(palette.ColorRole.Highlight).name()
            text_selected = palette.color(palette.ColorRole.HighlightedText).name()
        else:
            bg_normal = palette.color(palette.ColorRole.AlternateBase).darker(105).name()
            bg_selected = palette.color(palette.ColorRole.Highlight).name()
            text_selected = palette.color(palette.ColorRole.HighlightedText).name()
        
        cls._cached_styles = {
            'normal': f"ExpandableItem {{ background-color: {bg_normal}; border-radius: 3px; }}",
            'selected': f"ExpandableItem {{ background-color: {bg_selected}; border-radius: 3px; }}",
            'text_selected': text_selected
        }
        cls._styles_computed = True
    
    def __init__(self, message: str, data: str = None, color=None, logging_service=None):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.message = message
        self.data = data
        self.is_expanded = False
        self.is_selected = False
        self.message_color = color
        
        # Ensure styles are computed
        self._compute_styles()
        
        self.setup_ui()
        # Don't call update_appearance() here - let Qt handle initial styling
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with expand button and message
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 2, 5, 2)
        
        # Expand/collapse button
        self.expand_button = QPushButton()
        self.expand_button.setFixedSize(16, 16)
        self.expand_button.setFlat(True)
        self.expand_button.setStyleSheet("QPushButton { border: none; }")
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
            
            # Set partial opacity background for data section
            palette = self.palette()
            is_dark = palette.color(palette.ColorRole.Window).lightness() < 128
            if is_dark:
                data_bg_color = "rgba(42, 42, 42, 0.7)"  # Semi-transparent dark gray
            else:
                data_bg_color = "rgba(245, 245, 245, 0.7)"  # Semi-transparent light gray
            self.data_widget.setStyleSheet(f"QTextEdit {{ background-color: {data_bg_color}; border: 1px solid rgba(136, 136, 136, 0.5); }}")
            
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
    
    def mousePressEvent(self, event):
        """Handle mouse press for selection and context menu"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if Ctrl is held for multi-selection
            modifiers = event.modifiers()
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                # Multi-select mode - toggle selection
                self.selection_changed.emit(self)
            else:
                # Single select mode - clear others first
                self.clear_other_selections()
                self.set_selected(True)
                self.selection_changed.emit(self)
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())
        super().mousePressEvent(event)
    
    def clear_other_selections(self):
        """Clear selections of other items (handled by parent)"""
        # This will be handled by the log view's on_item_selected method
        pass
    

    
    def show_context_menu(self, position):
        """Show context menu for copying"""
        # Get parent virtual container to check for multiple selections
        parent_widget = self.parent()
        while parent_widget and not hasattr(parent_widget, 'get_selected_widgets'):
            parent_widget = parent_widget.parent()
        
        menu = QMenu(self)
        
        if parent_widget:
            selected_widgets = parent_widget.get_selected_widgets()
            if len(selected_widgets) > 1:
                # Multiple items selected
                count = len(selected_widgets)
                copy_text_action = menu.addAction(f"Copy Text ({count} items)")
                copy_text_action.triggered.connect(lambda: self.copy_multiple_text(selected_widgets))
                
                # Check if any selected items have data
                has_data = any(item.data for item in selected_widgets)
                if has_data:
                    copy_data_action = menu.addAction(f"Copy Data ({count} items)")
                    copy_data_action.triggered.connect(lambda: self.copy_multiple_data(selected_widgets))
                    
                    copy_both_action = menu.addAction(f"Copy Both ({count} items)")
                    copy_both_action.triggered.connect(lambda: self.copy_multiple_both(selected_widgets))
            else:
                # Single item (this item)
                copy_text_action = menu.addAction("Copy Text")
                copy_text_action.triggered.connect(self.copy_text)
                
                if self.data:
                    copy_data_action = menu.addAction("Copy Data")
                    copy_data_action.triggered.connect(self.copy_data)
                    
                    copy_both_action = menu.addAction("Copy Both")
                    copy_both_action.triggered.connect(self.copy_both)
        
        menu.exec(position)
    
    def copy_text(self):
        """Copy message text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.message)
    
    def copy_data(self):
        """Copy data to clipboard"""
        if self.data:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.data)
    
    def copy_both(self):
        """Copy both message and data to clipboard"""
        if self.data:
            combined = f"{self.message}\n\nData:\n{self.data}"
            clipboard = QApplication.clipboard()
            clipboard.setText(combined)
    
    def copy_multiple_text(self, items):
        """Copy text from multiple items with separators"""
        texts = []
        for i, item in enumerate(items):
            if i > 0:
                prev_item = items[i-1]
                if item.parent() and prev_item.parent():
                    current_pos = item.parent().layout().indexOf(item)
                    prev_pos = prev_item.parent().layout().indexOf(prev_item)
                    if current_pos - prev_pos > 1:
                        texts.append("...")
            texts.append(item.message)
        
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(texts))
    
    def copy_multiple_data(self, items):
        """Copy data from multiple items with separators"""
        texts = []
        for i, item in enumerate(items):
            if item.data:
                if i > 0:
                    prev_item = items[i-1]
                    if item.parent() and prev_item.parent():
                        current_pos = item.parent().layout().indexOf(item)
                        prev_pos = prev_item.parent().layout().indexOf(prev_item)
                        if current_pos - prev_pos > 1:
                            texts.append("...")
                texts.append(item.data)
        
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(texts))
    
    def copy_multiple_both(self, items):
        """Copy both text and data from multiple items with separators"""
        texts = []
        for i, item in enumerate(items):
            if i > 0:
                prev_item = items[i-1]
                if item.parent() and prev_item.parent():
                    current_pos = item.parent().layout().indexOf(item)
                    prev_pos = prev_item.parent().layout().indexOf(prev_item)
                    if current_pos - prev_pos > 1:
                        texts.append("...")
            texts.append(item.message)
            if item.data:
                texts.append(item.data)
        
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(texts))
    

    
    def set_selected(self, selected: bool):
        """Set selection state"""
        if self.is_selected != selected:  # Only update if state changed
            self.is_selected = selected
            self.update_appearance()
    
    def update_appearance(self):
        """Update widget appearance based on selection state"""
        if self.is_selected:
            self.setStyleSheet(self._cached_styles['selected'])
            text_color = self._cached_styles['text_selected']
        else:
            self.setStyleSheet(self._cached_styles['normal'])
            text_color = self.message_color.name() if self.message_color else None
        
        if text_color:
            self.message_label.setStyleSheet(f"QLabel {{ color: {text_color}; background: transparent; }}")
        else:
            self.message_label.setStyleSheet("QLabel { background: transparent; }")
    
    def set_message_color(self, color):
        """Set the color of the message text"""
        if self.message_color != color:
            self.message_color = color
            if not self.is_selected:  # Only update if not selected
                self.update_appearance()