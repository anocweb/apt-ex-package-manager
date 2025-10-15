from PyQt6.QtWidgets import QMainWindow, QGridLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import Qt
from PyQt6 import uic
from models.package_model import Package
import os

class MainView(QMainWindow):
    def __init__(self, package_manager):
        super().__init__()
        self.package_manager = package_manager
        self.current_packages = []
        self.selected_button = None
        self.sidebar_buttons = {}
        self.content_layouts = {}
        self.panels = {}
        uic.loadUi('src/ui/main_window.ui', self)
        self.load_panels()
        self.setup_ui()

    def setup_ui(self):
        # Setup content layouts from loaded panels
        home_panel = self.panels['home']
        installed_panel = self.panels['installed']
        category_panel = self.panels['category']
        
        self.package_layout = QGridLayout(home_panel.package_container)
        self.content_layouts['installed'] = QGridLayout(installed_panel.installedContainer)
        self.content_layouts['category'] = QGridLayout(category_panel.categoryContainer)
        
        # Connect search functionality from home panel
        home_panel.search_input.textChanged.connect(self.search_packages)
        
        # Store sidebar buttons for selection management
        self.sidebar_buttons = {
            'home': self.homeBtn,
            'installed': self.installedBtn,
            'updates': self.updatesBtn,
            'settings': self.settingsBtn,
            'about': self.aboutBtn,
            'all': self.allAppsBtn,
            'accessibility': self.accessibilityBtn,
            'development': self.developmentBtn,
            'education': self.educationBtn,
            'games': self.gamesBtn,
            'graphics': self.graphicsBtn,
            'internet': self.internetBtn,
            'multimedia': self.multimediaBtn,
            'office': self.officeBtn,
            'science': self.scienceBtn,
            'system': self.systemBtn,
            'utilities': self.utilitiesBtn
        }
        

        
        # Connect main navigation buttons
        self.homeBtn.clicked.connect(lambda: self.select_page('home', 0))
        self.installedBtn.clicked.connect(lambda: self.select_page('installed', 1))
        self.updatesBtn.clicked.connect(lambda: self.select_page('updates', 2))
        self.settingsBtn.clicked.connect(lambda: self.select_page('settings', 4))
        self.aboutBtn.clicked.connect(lambda: self.select_page('about', 5))
        
        # Connect category buttons
        self.allAppsBtn.clicked.connect(lambda: self.select_category('all'))
        self.accessibilityBtn.clicked.connect(lambda: self.select_category('accessibility'))
        self.developmentBtn.clicked.connect(lambda: self.select_category('development'))
        self.educationBtn.clicked.connect(lambda: self.select_category('education'))
        self.gamesBtn.clicked.connect(lambda: self.select_category('games'))
        self.graphicsBtn.clicked.connect(lambda: self.select_category('graphics'))
        self.internetBtn.clicked.connect(lambda: self.select_category('internet'))
        self.multimediaBtn.clicked.connect(lambda: self.select_category('multimedia'))
        self.officeBtn.clicked.connect(lambda: self.select_category('office'))
        self.scienceBtn.clicked.connect(lambda: self.select_category('science'))
        self.systemBtn.clicked.connect(lambda: self.select_category('system'))
        self.utilitiesBtn.clicked.connect(lambda: self.select_category('utilities'))
        
        # Set initial selection
        self.select_page('home', 0)
        self.load_initial_packages()
        
        # Connect settings panel buttons
        self.connect_settings_buttons()
    
    def load_panels(self):
        """Load all panel UI files and add them to the content stack"""
        panel_files = {
            'home': 'home_panel.ui',
            'installed': 'installed_panel.ui', 
            'updates': 'updates_panel.ui',
            'category': 'category_panel.ui',
            'settings': 'settings_panel.ui',
            'about': 'about_panel.ui'
        }
        
        for panel_name, ui_file in panel_files.items():
            panel_widget = QWidget()
            ui_path = os.path.join('src', 'ui', ui_file)
            uic.loadUi(ui_path, panel_widget)
            self.panels[panel_name] = panel_widget
            self.contentStack.addWidget(panel_widget)

    def search_packages(self):
        home_panel = self.panels['home']
        query = home_panel.search_input.text()
        if query:
            self.current_packages = self.package_manager.search_packages(query)
        else:
            self.current_packages = self.package_manager.get_installed_packages()
        self.update_package_display()

    def load_initial_packages(self):
        self.current_packages = self.package_manager.get_installed_packages()
        self.update_package_display()

    def update_package_display(self):
        # Clear existing widgets
        for i in reversed(range(self.package_layout.count())):
            self.package_layout.itemAt(i).widget().setParent(None)
        
        # Add package cards in grid
        row, col = 0, 0
        for package in self.current_packages[:20]:  # Limit display
            card = self.create_package_card(package)
            self.package_layout.addWidget(card, row, col)
            col += 1
            if col >= 3:  # 3 cards per row
                col = 0
                row += 1

    def create_package_card(self, package):
        card = QWidget()
        card.setFixedSize(200, 120)
        card.setStyleSheet("QWidget { border: 1px solid gray; border-radius: 5px; padding: 5px; }")
        
        layout = QGridLayout(card)
        
        name_label = QLabel(package.name)
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label, 0, 0, 1, 2)
        
        desc_label = QLabel(package.description[:50] + "..." if len(package.description) > 50 else package.description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label, 1, 0, 1, 2)
        
        install_btn = QPushButton("Install")
        install_btn.clicked.connect(lambda: self.install_package(package.name))
        layout.addWidget(install_btn, 2, 0)
        
        return card

    def install_package(self, package_name):
        self.package_manager.install_package(package_name)
        self.statusbar.showMessage(f"Installing {package_name}...", 3000)
    
    def select_page(self, page_key, page_index):
        # Update button selection
        self.update_button_selection(page_key)
        
        # Switch to the appropriate page
        self.contentStack.setCurrentIndex(page_index)
        
        # Update page title
        page_titles = {
            'home': 'Welcome to Apt-Ex Package Manager',
            'installed': 'Installed Packages',
            'updates': 'Available Updates',
            'settings': 'Settings',
            'about': 'About Apt-Ex Package Manager'
        }
        self.pageTitle.setText(page_titles.get(page_key, 'Apt-Ex Package Manager'))
        
        # Load content based on page
        if page_key == 'home':
            self.current_packages = self.package_manager.get_installed_packages()[:6]
            self.update_package_display()
            self.statusbar.showMessage("Home - Featured applications", 2000)
        elif page_key == 'installed':
            self.current_packages = self.package_manager.get_installed_packages()
            self.update_installed_display()
            self.statusbar.showMessage("Showing installed packages", 2000)
        elif page_key == 'updates':
            self.statusbar.showMessage("No updates available", 2000)
        elif page_key == 'settings':
            self.populate_settings_panel()
            self.statusbar.showMessage("Settings panel", 2000)
        elif page_key == 'about':
            self.statusbar.showMessage("About Apt-Ex Package Manager", 2000)
    
    def select_category(self, category):
        # Update button selection
        self.update_button_selection(category)
        
        # Switch to category page
        self.contentStack.setCurrentIndex(3)
        
        # Update page title for category
        self.pageTitle.setText(f"{category.title()} Packages")
        
        # Load category packages
        mock_packages = {
            "all": self.package_manager.get_installed_packages(),
            "accessibility": [Package("orca", "3.38", "Screen reader")],
            "development": [Package("gcc", "11.0", "GNU Compiler Collection"), Package("python3", "3.9", "Python interpreter")],
            "education": [Package("gcompris", "1.0", "Educational games"), Package("kstars", "3.5", "Astronomy software")],
            "games": [Package("supertux", "0.6", "2D platform game"), Package("chess", "1.0", "Chess game")],
            "graphics": [Package("gimp", "2.10", "Image editor"), Package("inkscape", "1.1", "Vector graphics")],
            "internet": [Package("firefox", "100.0", "Web browser"), Package("thunderbird", "91.0", "Email client")],
            "multimedia": [Package("vlc", "3.0", "Media player"), Package("audacity", "3.0", "Audio editor")],
            "office": [Package("libreoffice", "7.2", "Office suite"), Package("evince", "40.0", "Document viewer")],
            "science": [Package("octave", "6.4", "Scientific computing"), Package("r-base", "4.1", "Statistical computing")],
            "system": [Package("htop", "3.0", "System monitor"), Package("systemd", "247", "System manager")],
            "utilities": [Package("file-roller", "3.40", "Archive manager"), Package("calculator", "40.0", "Calculator")]
        }
        self.current_packages = mock_packages.get(category, [])
        self.update_category_display()
        self.statusbar.showMessage(f"Showing {category} packages", 2000)
    
    def update_button_selection(self, selected_key):
        # Clear previous selection
        if self.selected_button:
            self.selected_button.setProperty("selected", "false")
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)
        
        # Set new selection
        if selected_key in self.sidebar_buttons:
            self.selected_button = self.sidebar_buttons[selected_key]
            self.selected_button.setProperty("selected", "true")
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)
    
    def update_installed_display(self):
        layout = self.content_layouts['installed']
        # Clear existing widgets
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)
        
        # Add package cards
        row, col = 0, 0
        for package in self.current_packages[:20]:
            card = self.create_package_card(package)
            layout.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def update_category_display(self):
        layout = self.content_layouts['category']
        # Clear existing widgets
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)
        
        # Add package cards
        row, col = 0, 0
        for package in self.current_packages[:20]:
            card = self.create_package_card(package)
            layout.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def populate_settings_panel(self):
        """Populate settings panel with source data"""
        from PyQt6.QtWidgets import QTreeWidgetItem
        
        settings_panel = self.panels['settings']
        
        # Populate Flatpak sources
        flatpak_tree = settings_panel.flatpakSources
        flatpak_tree.clear()
        flatpak_item = QTreeWidgetItem(["✓ Flathub - dl.flathub.org"])
        flatpak_tree.addTopLevelItem(flatpak_item)
        flatpak_tree.setFixedHeight(flatpak_tree.sizeHintForRow(0) * flatpak_tree.topLevelItemCount() + 4)
        settings_panel.flatpakNoSources.setVisible(False)
        
        # Populate APT sources
        apt_tree = settings_panel.aptSources
        apt_tree.clear()
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
            apt_tree.addTopLevelItem(item)
        apt_tree.setFixedHeight(apt_tree.sizeHintForRow(0) * apt_tree.topLevelItemCount() + 4)
        settings_panel.aptNoSources.setVisible(False)
        
        # AppImage sources (empty - show no sources message)
        appimage_tree = settings_panel.appimageSources
        appimage_tree.clear()
        appimage_tree.setVisible(False)
        settings_panel.appimageNoSources.setVisible(True)
    
    def connect_settings_buttons(self):
        """Connect settings panel button actions"""
        if 'settings' in self.panels:
            settings_panel = self.panels['settings']
            settings_panel.aptSourcesBtn.clicked.connect(self.open_apt_sources)
    
    def open_apt_sources(self):
        """Open /etc/apt/ folder in default file manager"""
        import subprocess
        try:
            subprocess.run(['xdg-open', '/etc/apt/'], check=True)
        except subprocess.CalledProcessError:
            self.statusbar.showMessage("Could not open /etc/apt/ folder", 3000)