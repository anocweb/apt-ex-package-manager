from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QFrame, QStatusBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QCursor
import pyte

class OperationPanel(QWidget):
    """Resizable overlay panel for package operations with collapsible status bar"""
    
    collapsed = pyqtSignal()
    
    def __init__(self, parent=None, app_settings=None):
        super().__init__(parent)
        self.setObjectName("operationPanel")
        self.is_expanded = False
        self.default_height = 300
        self.min_height = 150
        self.max_height_ratio = 0.8
        self.drag_start_y = None
        self.drag_start_height = None
        self.app_settings = app_settings
        self.last_height = app_settings.get_operation_panel_height() if app_settings else self.default_height
        
        # Create overlay shade
        self.shade = QWidget(parent)
        self.shade.setObjectName("overlayShade")
        self.shade.setStyleSheet("""
            #overlayShade {
                background-color: rgba(0, 0, 0, 0.5);
            }
        """)
        self.shade.hide()
        
        self.setup_ui()
        self.hide()
    
    def setup_ui(self):
        """Setup the overlay panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Drag handle for resizing
        self.drag_handle = QFrame()
        self.drag_handle.setObjectName("dragHandle")
        self.drag_handle.setFixedHeight(6)
        self.drag_handle.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.drag_handle.mousePressEvent = self.start_resize
        self.drag_handle.mouseMoveEvent = self.do_resize
        self.drag_handle.mouseReleaseEvent = self.end_resize
        layout.addWidget(self.drag_handle)
        
        # Content area
        content = QWidget()
        content.setObjectName("operationContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 8, 12, 12)
        
        # Header
        self.title_label = QLabel("Operations Console")
        title_font = QFont()
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)
        content_layout.addWidget(self.title_label)
        
        # Output text area with terminal emulation
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("monospace", 9))
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        content_layout.addWidget(self.output_text)
        
        # Terminal emulator (will be initialized with proper size)
        self.screen = None
        self.stream = None
        self._init_terminal()
        
        layout.addWidget(content)
        
        # Style with shadow
        self.setStyleSheet("""
            #operationPanel {
                background: palette(base);
                border-top: 2px solid palette(mid);
                border-left: 1px solid palette(mid);
                border-right: 1px solid palette(mid);
            }
            #dragHandle {
                background: palette(mid);
            }
            #dragHandle:hover {
                background: palette(highlight);
            }
            #operationContent {
                background: palette(base);
            }
        """)
        
        # Add drop shadow effect
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(-5)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)
    
    def start_resize(self, event):
        """Start resizing the panel"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_y = event.globalPosition().y()
            self.drag_start_height = self.height()
    
    def do_resize(self, event):
        """Resize the panel as user drags"""
        if self.drag_start_y is not None:
            delta = self.drag_start_y - event.globalPosition().y()
            new_height = self.drag_start_height + delta
            
            max_height = int(self.parent().height() * self.max_height_ratio)
            new_height = int(max(self.min_height, min(new_height, max_height)))
            
            self.setFixedHeight(new_height)
            self.last_height = new_height
            self.update_position()
    
    def end_resize(self, event):
        """End resizing"""
        self.drag_start_y = None
        self.drag_start_height = None
        # Save height to settings after resize is complete
        if self.app_settings:
            self.app_settings.set_operation_panel_height(self.last_height)
    
    def expand_panel(self):
        """Expand the panel with animation"""
        if self.is_expanded:
            return
        
        self.is_expanded = True
        
        # Show and position shade
        if self.parent():
            self.shade.setGeometry(0, 0, self.parent().width(), self.parent().height())
            self.shade.show()
            self.shade.raise_()
        
        self.show()
        self.raise_()
        
        # Use last height, constrained by current window size
        parent_height = self.parent().height()
        max_height = int(parent_height * self.max_height_ratio)
        panel_height = min(self.last_height, max_height)
        
        self.setFixedHeight(panel_height)
        self.update_position()
        
        # Animate slide up
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setStartValue(QPoint(0, parent_height))
        self.animation.setEndValue(QPoint(0, parent_height - panel_height))
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.finished.connect(self._on_expand_finished)
        self.animation.start()
    
    def _on_expand_finished(self):
        """Handle expansion animation finished"""
        # Recalculate terminal width now that panel is fully visible
        if self.screen:
            new_cols = self._calculate_terminal_width()
            if new_cols != self.screen.columns:
                self.screen.resize(lines=self.screen.lines, columns=new_cols)
    
    def collapse_panel(self):
        """Collapse the panel with animation"""
        if not self.is_expanded:
            return
        
        self.is_expanded = False
        
        # Hide shade
        self.shade.hide()
        
        # Animate slide down
        parent_height = self.parent().height()
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(QPoint(0, parent_height))
        self.animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.animation.finished.connect(self.hide)
        self.animation.start()
        
        self.collapsed.emit()
    
    def update_position(self):
        """Update panel position based on parent size"""
        if self.parent() and self.is_expanded:
            parent_height = self.parent().height()
            self.move(0, parent_height - self.height())
            self.setFixedWidth(self.parent().width())
            # Update shade size
            self.shade.setGeometry(0, 0, self.parent().width(), parent_height)
    
    def _init_terminal(self):
        """Initialize terminal with calculated dimensions"""
        cols = self._calculate_terminal_width()
        rows = 100  # Large enough for scrolling
        self.screen = pyte.Screen(cols, rows)
        self.stream = pyte.Stream(self.screen)
    
    def _calculate_terminal_width(self):
        """Calculate terminal width based on widget width"""
        if not self.output_text or not self.output_text.isVisible():
            return 120
        
        # Get font metrics
        font_metrics = self.output_text.fontMetrics()
        char_width = font_metrics.horizontalAdvance('M')  # Use 'M' for monospace width
        
        if char_width <= 0:
            return 120
        
        # Get available width (account for scrollbar ~20px and small margin)
        available_width = self.output_text.viewport().width() - 25
        
        if available_width <= 0:
            return 120
        
        # Calculate columns
        cols = max(80, available_width // char_width)
        return cols
    
    def resizeEvent(self, event):
        """Handle resize to update terminal width"""
        super().resizeEvent(event)
        if self.screen:
            new_cols = self._calculate_terminal_width()
            if new_cols != self.screen.columns:
                # Resize terminal
                self.screen.resize(lines=self.screen.lines, columns=new_cols)
    
    def set_operation(self, operation_type: str, package_name: str, command: str):
        """Set the current operation details"""
        if command:
            self.title_label.setText(f"Operations Console: {command}")
        else:
            self.title_label.setText("Operations Console")
        self.output_text.clear()
        # Reinitialize terminal with current width
        self._init_terminal()
    
    def append_output(self, text: str):
        """Update output area with terminal content"""
        # Update display with full terminal content
        self.output_text.setPlainText(text)
        self.output_text.verticalScrollBar().setValue(
            self.output_text.verticalScrollBar().maximum()
        )
    
    def set_complete(self, success: bool):
        """Mark operation as complete"""
        if success:
            self.append_output("\n✓ Operation completed successfully")
        else:
            self.append_output("\n✗ Operation failed")


class OperationStatusBar(QStatusBar):
    """Collapsible status bar for package operations"""
    
    expand_requested = pyqtSignal()
    collapse_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("operationStatusBar")
        self.setFixedHeight(40)
        self.spinner_frame = 0
        self.spinner_timer = QTimer()
        self.spinner_timer.timeout.connect(self.update_spinner)
        self.is_expanded = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup status bar UI"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # Expand/collapse icon (always visible)
        self.expand_icon = QLabel("▲")
        expand_font = QFont()
        expand_font.setPointSize(14)
        self.expand_icon.setFont(expand_font)
        self.expand_icon.setFixedWidth(20)
        self.expand_icon.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.expand_icon.setToolTip("Expand operations console")
        self.expand_icon.mousePressEvent = lambda e: self.toggle_panel()
        layout.addWidget(self.expand_icon)
        
        # Operation section (hidden by default)
        self.operation_widget = QWidget()
        op_layout = QHBoxLayout(self.operation_widget)
        op_layout.setContentsMargins(0, 0, 0, 0)
        
        # Spinner
        self.spinner_label = QLabel("⟳")
        spinner_font = QFont()
        spinner_font.setPointSize(14)
        self.spinner_label.setFont(spinner_font)
        op_layout.addWidget(self.spinner_label)
        
        # Status text
        self.status_label = QLabel()
        op_layout.addWidget(self.status_label)
        
        # Expand button
        self.expand_btn = QPushButton("Show Details")
        self.expand_btn.clicked.connect(self.expand_requested.emit)
        op_layout.addWidget(self.expand_btn)
        
        self.operation_widget.hide()
        layout.addWidget(self.operation_widget)
        
        # General status message (always visible)
        self.general_status_label = QLabel("Ready")
        layout.addWidget(self.general_status_label)
        
        layout.addStretch()
        
        # Permanent widgets container
        self.permanent_widgets = []
        
        self.addWidget(container, 1)
        
        # Style
        self.setStyleSheet("""
            #operationStatusBar {
                background: palette(window);
                border-top: 1px solid palette(mid);
            }
        """)
    
    def add_permanent_widget(self, widget):
        """Add a permanent widget to the right side"""
        self.permanent_widgets.append(widget)
        self.addPermanentWidget(widget)
    
    def show_message(self, message: str, timeout: int = 0):
        """Show a general status message"""
        # Don't show if operation is active
        if not self.operation_widget.isVisible():
            self.general_status_label.setText(message)
            if timeout > 0:
                QTimer.singleShot(timeout, lambda: self.general_status_label.setText("Ready") if not self.operation_widget.isVisible() else None)
    
    def start_operation(self, operation_type: str, package_name: str):
        """Start showing operation in status bar"""
        self.status_label.setText(f"{operation_type} {package_name}...")
        self.operation_widget.show()
        self.general_status_label.clear()
        self.spinner_timer.start(100)
    
    def update_spinner(self):
        """Animate spinner"""
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_label.setText(spinners[self.spinner_frame % len(spinners)])
        self.spinner_frame += 1
    
    def set_complete(self, success: bool, message: str):
        """Show completion status"""
        self.spinner_timer.stop()
        
        if success:
            self.spinner_label.setText("✓")
            self.status_label.setText(message)
        else:
            self.spinner_label.setText("✗")
            self.status_label.setText(f"Failed: {message}")
        
        # Auto-hide after 3 seconds
        QTimer.singleShot(3000, self.stop_operation)
    
    def stop_operation(self):
        """Stop showing operation"""
        self.spinner_timer.stop()
        self.operation_widget.hide()
        self.general_status_label.setText("Ready")
    
    def toggle_panel(self):
        """Toggle panel expanded/collapsed"""
        if self.is_expanded:
            self.collapse_requested.emit()
        else:
            self.expand_requested.emit()
    
    def set_expanded(self, expanded: bool):
        """Update icon based on expanded state"""
        self.is_expanded = expanded
        self.expand_icon.setText("▼" if expanded else "▲")
        self.expand_icon.setToolTip("Collapse operations console" if expanded else "Expand operations console")
