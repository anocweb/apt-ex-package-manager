"""Package detail panel controller"""
from PyQt6.QtCore import pyqtSignal
from .base_panel import BasePanel


class PackageDetailPanel(BasePanel):
    """Panel for displaying package details"""
    
    back_requested = pyqtSignal()
    install_requested = pyqtSignal(str, str)
    remove_requested = pyqtSignal(str, str)
    
    def __init__(self, ui_file, package_manager, lmdb_manager, logging_service, app_settings):
        self.current_package = None
        self.return_panel = None
        super().__init__(ui_file, package_manager, lmdb_manager, logging_service, app_settings)
        self.actionButton.clicked.connect(self.on_action)
    
    def get_context_actions(self):
        """Return context actions for detail panel"""
        return [("← Back", self.on_back)]
    
    def show_package(self, package_info, return_panel):
        """Display package details"""
        self.current_package = package_info
        self.return_panel = return_panel
        
        # Fetch full package details
        package_name = package_info.get('name')
        backend = package_info.get('backend', 'apt')
        backend_obj = self.package_manager.get_backend(backend)
        
        if backend_obj and hasattr(backend_obj, 'get_package_details'):
            full_details = backend_obj.get_package_details(package_name)
            if full_details:
                package_info = full_details
                self.current_package = full_details
        
        # Set basic info
        self.nameLabel.setText(package_info.get('name', 'Unknown'))
        self.summaryLabel.setText(package_info.get('summary', package_info.get('description', '')[:100]))
        self.descriptionLabel.setText(package_info.get('description', 'No description available'))
        
        # Set version
        version = package_info.get('version', 'Unknown')
        self.versionLabel.setText(f"Version: {version}")
        
        # Set backend
        backend = package_info.get('backend', 'apt').upper()
        self.backendLabel.setText(backend)
        
        # Build details section with groups
        details = []
        
        # Package Information
        pkg_info = []
        if 'section' in package_info and package_info['section']:
            pkg_info.append(f"<b>Section:</b> {package_info['section']}")
        if 'priority' in package_info and package_info['priority']:
            pkg_info.append(f"<b>Priority:</b> {package_info['priority']}")
        if 'architecture' in package_info and package_info['architecture']:
            pkg_info.append(f"<b>Architecture:</b> {package_info['architecture']}")
        if 'license' in package_info and package_info['license']:
            pkg_info.append(f"<b>License:</b> {package_info['license']}")
        
        if pkg_info:
            details.append('<b style="font-size: 12pt;">Package Information</b>')
            details.extend(pkg_info)
            details.append('')
        
        # Size Information
        size_info = []
        if 'installed_size' in package_info:
            size = package_info['installed_size']
            if size > 1024 * 1024:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            elif size > 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} B"
            size_info.append(f"<b>Installed Size:</b> {size_str}")
        if 'size' in package_info and package_info['size']:
            size = package_info['size']
            if size > 1024 * 1024:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            elif size > 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} B"
            size_info.append(f"<b>Download Size:</b> {size_str}")
        
        if size_info:
            details.append('<b style="font-size: 12pt;">Size</b>')
            details.extend(size_info)
            details.append('')
        
        # Contact & Links
        contact_info = []
        if 'maintainer' in package_info and package_info['maintainer']:
            maintainer = package_info['maintainer']
            if '<' in maintainer and '>' in maintainer:
                import re
                match = re.search(r'(.+?)<(.+?)>', maintainer)
                if match:
                    name, email = match.groups()
                    contact_info.append(f"<b>Maintainer:</b> {name.strip()} &lt;<a href='mailto:{email}'>{email}</a>&gt;")
                else:
                    contact_info.append(f"<b>Maintainer:</b> {maintainer}")
            else:
                contact_info.append(f"<b>Maintainer:</b> {maintainer}")
        if 'homepage' in package_info and package_info['homepage']:
            homepage = package_info['homepage']
            contact_info.append(f"<b>Homepage:</b> <a href='{homepage}'>{homepage}</a>")
        if 'source' in package_info and package_info['source']:
            contact_info.append(f"<b>Source:</b> {package_info['source']}")
        
        if contact_info:
            details.append('<b style="font-size: 12pt;">Contact & Links</b>')
            details.extend(contact_info)
            details.append('')
        
        # Dependencies
        dep_info = []
        if 'depends' in package_info and package_info['depends']:
            dep_info.append(f"<b>Dependencies:</b> {package_info['depends']}")
        if 'recommends' in package_info and package_info['recommends']:
            dep_info.append(f"<b>Recommends:</b> {package_info['recommends']}")
        
        if dep_info:
            details.append('<b style="font-size: 12pt;">Dependencies</b>')
            details.extend(dep_info)
        
        self.detailsLabel.setText('<br>'.join(details) if details else 'No additional details available')
        self.detailsLabel.setOpenExternalLinks(True)
        
        # Set action button
        is_installed = package_info.get('installed', False)
        if is_installed:
            self.actionButton.setText("🗑 Remove")
            self.actionButton.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #FF5252;
                }
            """)
        else:
            self.actionButton.setText("⬇ Install")
            self.actionButton.setStyleSheet("""
                QPushButton {
                    background-color: palette(highlight);
                    color: palette(highlighted-text);
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: palette(dark);
                }
            """)
    
    def on_back(self):
        """Handle back button"""
        self.back_requested.emit()
    
    def on_action(self):
        """Handle install/remove action"""
        if not self.current_package:
            return
        
        name = self.current_package.get('name')
        backend = self.current_package.get('backend', 'apt')
        is_installed = self.current_package.get('installed', False)
        
        if is_installed:
            self.remove_requested.emit(name, backend)
        else:
            self.install_requested.emit(name, backend)
    
    def get_title(self):
        """Return panel title"""
        return 'Package Details'
