from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6 import uic

class InstalledListItem(QFrame):
    """Installed package list item with version and size info"""
    
    remove_requested = pyqtSignal(str)  # Emits package name when remove is clicked
    
    def __init__(self, package_info, parent=None):
        super().__init__(parent)
        self.package_info = package_info
        uic.loadUi('src/ui/installed_list_item.ui', self)
        self.setup_ui()
    
    def setup_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Check if dev outline is active
        from PyQt6.QtWidgets import QApplication
        app_stylesheet = QApplication.instance().styleSheet()
        dev_outline = "border: 1px solid red" in app_stylesheet
        
        if dev_outline:
            self.setStyleSheet("""
                QFrame {
                    background-color: palette(base);
                    border: 1px solid red;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px;
                }
                QFrame:hover {
                    background-color: palette(alternate-base);
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: palette(base);
                    border: 1px solid palette(mid);
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px;
                }
                QFrame:hover {
                    background-color: palette(alternate-base);
                }
            """)
        
        # Set package data
        name = self.package_info.get('name', 'Unknown Package')
        self.nameLabel.setText(name)
        
        description = self.package_info.get('description', 'No description available')
        self.descLabel.setText(description)
        
        backend = self.package_info.get('backend', 'apt')
        self.backendLabel.setText(backend.upper())
        
        # Set version and size info
        version = self.package_info.get('version', 'Unknown')
        installed_size = self.package_info.get('installed_size', 0)
        
        # Format size
        if installed_size > 1024 * 1024:  # MB
            size_str = f"{installed_size / (1024 * 1024):.1f} MB"
        elif installed_size > 1024:  # KB
            size_str = f"{installed_size / 1024:.1f} KB"
        else:
            size_str = f"{installed_size} B"
        
        self.infoLabel.setText(
            f'<span style="color: palette(window-text);">{version}</span> '
            f'<span style="color: palette(window-text);">•</span> '
            f'<span style="color: palette(window-text);">{size_str}</span>'
        )
        
        # Connect remove button
        self.removeButton.clicked.connect(lambda: self.remove_requested.emit(name))
        
        # Apply dev outline if active
        if dev_outline:
            for widget in [self.iconLabel, self.nameLabel, self.descLabel, 
                          self.infoLabel, self.backendLabel]:
                widget.setStyleSheet(widget.styleSheet() + "; border: 1px solid red;")
            self.removeButton.setStyleSheet(
                self.removeButton.styleSheet().replace("border: none;", "border: 1px solid red;")
            )
        
        # Set transparent for mouse events
        for label in [self.nameLabel, self.descLabel, self.infoLabel, self.backendLabel]:
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
