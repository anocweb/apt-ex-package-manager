"""Plugin card widget"""
from PyQt6.QtWidgets import QFrame, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6 import uic
import subprocess

class PluginCard(QFrame):
    """Card widget for displaying plugin information"""
    
    def __init__(self, status, parent=None):
        super().__init__(parent)
        uic.loadUi('src/ui/widgets/plugin_card.ui', self)
        self.status = status
        self.populate()
    
    def populate(self):
        """Populate card with plugin data"""
        status = self.status
        
        # Header
        status_icon = "✅" if status['available'] else "❌"
        version = status.get('version', '1.0.0')
        self.nameLabel.setText(f"{status_icon} {status['display_name']} v{version}")
        
        # Action button
        self.setup_action_button()
        
        # Dependencies
        self.populate_dependencies()
    
    def populate_dependencies(self):
        """Populate dependencies section"""
        layout = self.depsContainerLayout
        
        # System dependencies
        for dep in self.status['dependencies']['system']:
            dep_text = f"  • {dep['name']} ({dep['command']})"
            if dep['satisfied']:
                dep_text += " ✓"
                if dep['installed_version']:
                    dep_text += f" v{dep['installed_version']}"
                color = "green"
            else:
                dep_text += " ✗ Missing"
                if dep['required_version']:
                    dep_text += f" (requires {dep['required_version']})"
                color = "red"
            
            label = QLabel(dep_text)
            label.setStyleSheet(f"font-size: 12px; color: {color};")
            layout.addWidget(label)
        
        # Python dependencies
        for dep in self.status['dependencies']['python']:
            dep_text = f"  • Python: {dep['package']}"
            if dep['satisfied']:
                dep_text += " ✓"
                if dep['installed_version']:
                    dep_text += f" v{dep['installed_version']}"
                color = "green"
            else:
                dep_text += " ✗ Missing"
                if dep['required_version']:
                    dep_text += f" (requires {dep['required_version']})"
                color = "red"
            
            label = QLabel(dep_text)
            label.setStyleSheet(f"font-size: 12px; color: {color};")
            layout.addWidget(label)
    
    def setup_action_button(self):
        """Setup context-sensitive action button"""
        if self.status['missing_dependencies']:
            self.actionBtn.setText("Install")
            self.actionBtn.clicked.connect(self.install_dependencies)
        elif self.status['available']:
            # TODO: Add enable/disable functionality
            self.actionBtn.setText("Disable")
            self.actionBtn.setEnabled(False)  # Disabled until implemented
        else:
            self.actionBtn.setText("Enable")
            self.actionBtn.setEnabled(False)  # Disabled until implemented
    
    def get_install_command(self):
        """Generate install command for missing dependencies"""
        commands = []
        
        for dep in self.status['dependencies']['system']:
            if not dep['satisfied']:
                commands.append(dep.get('package', dep['command']))
        
        for dep in self.status['dependencies']['python']:
            if not dep['satisfied']:
                pkg = dep['package']
                if dep['required_version']:
                    pkg += dep['required_version']
                commands.append(f"python3-{pkg}")
        
        if commands:
            return f"sudo apt install {' '.join(commands)}"
        return None
    
    def install_dependencies(self):
        """Install missing dependencies"""
        install_cmd = self.get_install_command()
        if not install_cmd:
            return
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Install Dependencies",
            f"Install missing dependencies?\n\n{install_cmd}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Run install command with pkexec for GUI password prompt
                cmd = ['pkexec', 'apt-get', 'install', '-y'] + self.get_package_list()
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    QMessageBox.information(self, "Success", "Dependencies installed successfully!")
                else:
                    QMessageBox.warning(self, "Error", f"Installation failed:\n{result.stderr}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to install dependencies:\n{str(e)}")
    
    def get_package_list(self):
        """Get list of packages to install"""
        packages = []
        
        for dep in self.status['dependencies']['system']:
            if not dep['satisfied']:
                packages.append(dep.get('package', dep['command']))
        
        for dep in self.status['dependencies']['python']:
            if not dep['satisfied']:
                pkg = dep['package']
                # Try python3- prefix first, fallback to python- if not found
                python3_pkg = f"python3-{pkg}"
                python_pkg = f"python-{pkg}"
                
                # Check which package exists
                try:
                    result = subprocess.run(['apt-cache', 'show', python3_pkg], 
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if result.returncode == 0:
                        packages.append(python3_pkg)
                    else:
                        # Try python- prefix
                        result = subprocess.run(['apt-cache', 'show', python_pkg], 
                                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        if result.returncode == 0:
                            packages.append(python_pkg)
                        else:
                            # Default to python3- if neither found
                            packages.append(python3_pkg)
                except:
                    # Fallback to python3- on error
                    packages.append(python3_pkg)
        
        return packages
