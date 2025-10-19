from PyQt6.QtCore import pyqtSignal
from widgets.base_list_item import BaseListItem


class UpdateListItem(BaseListItem):
    """Package update list item with version info and security indicator"""
    
    update_requested = pyqtSignal(str)
    
    def __init__(self, update_info, parent=None):
        self.update_info = update_info
        super().__init__('src/ui/widgets/update_list_item.ui', parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup update-specific UI"""
        # Determine if security update and set styling
        is_security = self.update_info.get('is_security', False)
        if is_security:
            self._set_frame_style(self.COLOR_SECURITY, self.COLOR_SECURITY_BG)
        
        # Set package data
        name = self.update_info.get('name', 'Unknown Package')
        self.nameLabel.setText(name)
        self.descLabel.setText(self.update_info.get('description', 'No description available'))
        
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
        
        # Apply dev outline
        self._apply_dev_outline(self.iconLabel, self.nameLabel, self.descLabel,
                                self.versionLabel, self.securityLabel, self.updateButton)
