from PyQt6.QtCore import pyqtSignal
from widgets.base_list_item import BaseListItem


class InstalledListItem(BaseListItem):
    """Installed package list item with version and size info"""
    
    remove_requested = pyqtSignal(str)
    
    def __init__(self, package_info, parent=None):
        self.package_info = package_info
        super().__init__('widgets/installed_list_item.ui', parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup installed package-specific UI"""
        # Set package data
        name = self.package_info.get('name', 'Unknown Package')
        self.nameLabel.setText(name)
        self.descLabel.setText(self.package_info.get('description', 'No description available'))
        self.backendLabel.setText(self.package_info.get('backend', 'apt').upper())
        
        # Set version and size info
        version = self.package_info.get('version', 'Unknown')
        installed_size = self.package_info.get('installed_size', 0)
        size_str = self._format_size(installed_size)
        
        self.infoLabel.setText(
            f'<span style="color: palette(window-text);">{version}</span> '
            f'<span style="color: palette(window-text);">•</span> '
            f'<span style="color: palette(window-text);">{size_str}</span>'
        )
        
        # Connect remove button
        self.removeButton.clicked.connect(lambda: self.remove_requested.emit(name))
        
        # Apply dev outline
        self._apply_dev_outline(self.iconLabel, self.nameLabel, self.descLabel,
                                self.infoLabel, self.backendLabel, self.removeButton)
    
    def _format_size(self, size_bytes):
        """Format size in bytes to human-readable string"""
        if size_bytes > 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        elif size_bytes > 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes} B"
