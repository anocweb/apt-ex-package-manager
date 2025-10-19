"""Settings panel controller"""
from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal
from .base_panel import BasePanel
import subprocess


class SettingsPanel(BasePanel):
    """Panel for application settings"""
    
    default_repository_changed = pyqtSignal(str)
    
    def setup_ui(self):
        """Setup settings panel UI"""
        self.populate_sources()
        self.update_default_repository_ui()
    
    def connect_signals(self):
        """Connect signals"""
        self.aptSourcesBtn.clicked.connect(self.open_apt_sources)
        
        if hasattr(self, 'makeDefaultFlatpak'):
            self.makeDefaultFlatpak.clicked.connect(lambda: self.set_default_repository('flatpak'))
        if hasattr(self, 'makeDefaultApt'):
            self.makeDefaultApt.clicked.connect(lambda: self.set_default_repository('apt'))
        
        if hasattr(self, 'odrsEnabledCheckbox'):
            self.odrsEnabledCheckbox.toggled.connect(self.set_odrs_enabled)
            self.odrsEnabledCheckbox.setChecked(self.app_settings.get_odrs_enabled())
    
    def get_title(self):
        """Return panel title"""
        return "Settings"
    
    def populate_sources(self):
        """Populate repository sources"""
        # Populate Flatpak sources
        self.flatpakSources.clear()
        flatpak_item = QTreeWidgetItem(["✓ Flathub - dl.flathub.org"])
        self.flatpakSources.addTopLevelItem(flatpak_item)
        self.flatpakSources.setFixedHeight(self.flatpakSources.sizeHintForRow(0) * self.flatpakSources.topLevelItemCount() + 4)
        self.flatpakNoSources.setVisible(False)
        
        # Populate APT sources
        self.aptSources.clear()
        apt_sources = [
            "✓ downloads.1password.com/linux/debian/amd64 - Stable (main)",
            "✓ brave-browser-apt-release.s3.brave.com - Stable (main)",
            "✓ ppa.launchpadcontent.net/danielrichter2007/grub-customizer/ubuntu - Questing (main)",
            "✓ Ubuntu Questing (main universe restricted multiverse)",
            "✓ Ubuntu Questing updates (main universe restricted multiverse)",
            "✓ Ubuntu Questing backports (main universe restricted multiverse)",
            "✓ Ubuntu Questing security (main universe restricted multiverse)",
            "✓ packages.microsoft.com/repos/code - Stable (main)"
        ]
        for source in apt_sources:
            item = QTreeWidgetItem([source])
            self.aptSources.addTopLevelItem(item)
        self.aptSources.setFixedHeight(self.aptSources.sizeHintForRow(0) * self.aptSources.topLevelItemCount() + 4)
        self.aptNoSources.setVisible(False)
        
        # AppImage sources (empty)
        self.appimageSources.clear()
        self.appimageSources.setVisible(False)
        self.appimageNoSources.setVisible(True)
    
    def open_apt_sources(self):
        """Open /etc/apt/ folder in file manager"""
        self.logger.info("Opening APT sources folder")
        try:
            subprocess.run(['xdg-open', '/etc/apt/'], check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to open APT sources: {e}")
    
    def set_default_repository(self, repo_type):
        """Set default repository type"""
        self.logger.info(f"Changed default repository to {repo_type}")
        self.app_settings.set_default_repository(repo_type)
        self.update_default_repository_ui()
        self.default_repository_changed.emit(repo_type)
    
    def update_default_repository_ui(self):
        """Update UI to reflect default repository setting"""
        default_repo = self.app_settings.get_default_repository()
        
        if hasattr(self, 'makeDefaultFlatpak'):
            if default_repo == 'flatpak':
                self.makeDefaultFlatpak.setText('★ Default')
                self.makeDefaultFlatpak.setEnabled(False)
            else:
                self.makeDefaultFlatpak.setText('☆ Make Default')
                self.makeDefaultFlatpak.setEnabled(True)
        
        if hasattr(self, 'makeDefaultApt'):
            if default_repo == 'apt':
                self.makeDefaultApt.setText('★ Default')
                self.makeDefaultApt.setEnabled(False)
            else:
                self.makeDefaultApt.setText('☆ Make Default')
                self.makeDefaultApt.setEnabled(True)
    
    def set_odrs_enabled(self, enabled):
        """Set ODRS enabled setting"""
        self.app_settings.set_odrs_enabled(enabled)
        self.logger.info(f"ODRS {'enabled' if enabled else 'disabled'}")
