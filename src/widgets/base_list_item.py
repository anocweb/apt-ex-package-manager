"""Base list item widget with standardized styling"""
from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6 import uic
from utils.path_resolver import PathResolver


class BaseListItem(QFrame):
    """Base class for all list item widgets with consistent styling"""
    
    double_clicked = pyqtSignal()
    
    # Standard dimensions
    ITEM_HEIGHT = 125
    ICON_SIZE = 64
    BUTTON_WIDTH = 80
    BUTTON_HEIGHT = 32
    
    # Standard colors
    COLOR_SECURITY = "#FF6B6B"
    COLOR_SECURITY_BG = "rgba(255, 107, 107, 0.1)"
    
    def __init__(self, ui_file, parent=None):
        super().__init__(parent)
        uic.loadUi(PathResolver.get_ui_path(ui_file), self)
        self._apply_base_styling()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click"""
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)
    
    def _apply_base_styling(self):
        """Apply base styling to the widget"""
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(self.ITEM_HEIGHT)
        
        # Check if dev outline is active
        from PyQt6.QtWidgets import QApplication
        app_stylesheet = QApplication.instance().styleSheet()
        self.dev_outline = "border: 1px solid red" in app_stylesheet
        
        # Apply base frame style
        self._set_frame_style()
        
        # Make labels transparent for mouse events
        self._set_labels_transparent()
    
    def _set_frame_style(self, border_color="palette(mid)", bg_color="palette(button)", bg_hover="palette(alternate-base)"):
        """Set frame style with optional custom colors"""
        if self.dev_outline:
            border = "1px solid red"
        else:
            border = f"2px solid {border_color}"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: {border};
                border-radius: 8px;
                padding: 8px;
                margin: 4px;
            }}
            QFrame:hover {{
                background-color: {bg_hover};
            }}
        """)
    
    def _set_labels_transparent(self):
        """Make all labels transparent for mouse events"""
        for child in self.findChildren(type(self.nameLabel)):
            if child.objectName() != 'iconLabel':
                child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
    
    def _apply_dev_outline(self, *widgets):
        """Apply dev outline to specified widgets"""
        if self.dev_outline:
            for widget in widgets:
                current_style = widget.styleSheet()
                if "border: none" in current_style:
                    widget.setStyleSheet(current_style.replace("border: none;", "border: 1px solid red;"))
                else:
                    widget.setStyleSheet(current_style + "; border: 1px solid red;")
