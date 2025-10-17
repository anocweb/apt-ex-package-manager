from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6 import uic

class UpdateListItem(QFrame):
    """Package update list item with version info and security indicator"""
    
    update_requested = pyqtSignal(str)  # Emits package name when update is clicked
    
    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        uic.loadUi('src/ui/update_list_item.ui', self)
        self.setup_ui()
    
    def setup_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Check if dev outline is active
        from PyQt6.QtWidgets import QApplication
        app_stylesheet = QApplication.instance().styleSheet()
        dev_outline = "border: 1px solid red" in app_stylesheet
        
        # Determine if security update
        is_security = self.update_info.get('is_security', False)
        
        # Set border color based on security status
        if is_security:
            border_color = "#FF6B6B"  # Red for security updates
            bg_hover = "rgba(255, 107, 107, 0.1)"
        else:
            border_color = "palette(mid)"
            bg_hover = "palette(alternate-base)"
        
        if dev_outline:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: palette(base);
                    border: 1px solid red;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px;
                }}
                QFrame:hover {{
                    background-color: {bg_hover};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: palette(base);
                    border: 2px solid {border_color};
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px;
                }}
                QFrame:hover {{
                    background-color: {bg_hover};
                }}
            """)
        
        # Set package data
        name = self.update_info.get('name', 'Unknown Package')
        self.nameLabel.setText(name)
        
        description = self.update_info.get('description', 'No description available')
        self.descLabel.setText(description)
        
        # Set version info
        current_version = self.update_info.get('current_version', '?')
        new_version = self.update_info.get('new_version', '?')
        self.versionLabel.setText(
            f'<span style="color: palette(mid);">{current_version}</span> '
            f'<span style="color: palette(window-text);">→</span> '
            f'<span style="color: palette(highlight);">{new_version}</span>'
        )
        
        # Set security indicator
        if is_security:
            self.securityLabel.setText('🔒 SECURITY')
            self.iconLabel.setText('🔒')
            self.iconLabel.setStyleSheet(
                "background-color: rgba(255, 107, 107, 0.2); border-radius: 8px;"
            )
        else:
            self.securityLabel.setText('')
        
        # Connect update button
        self.updateButton.clicked.connect(lambda: self.update_requested.emit(name))
        
        # Apply dev outline if active
        if dev_outline:
            for widget in [self.iconLabel, self.nameLabel, self.descLabel, 
                          self.versionLabel, self.securityLabel]:
                widget.setStyleSheet(widget.styleSheet() + "; border: 1px solid red;")
            self.updateButton.setStyleSheet(
                self.updateButton.styleSheet().replace("border: none;", "border: 1px solid red;")
            )
        
        # Set transparent for mouse events
        for label in [self.nameLabel, self.descLabel, self.versionLabel, self.securityLabel]:
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
