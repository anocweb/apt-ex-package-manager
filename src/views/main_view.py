from PyQt6.QtWidgets import QMainWindow, QGridLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import Qt
from PyQt6 import uic
from models.package_model import Package

class MainView(QMainWindow):
    def __init__(self, package_manager):
        super().__init__()
        self.package_manager = package_manager
        uic.loadUi('src/ui/main_window.ui', self)
        self.setup_ui()
        self.current_packages = []

    def setup_ui(self):
        self.search_input.textChanged.connect(self.search_packages)
        self.package_layout = QGridLayout(self.package_container)
        
        # Connect main navigation buttons
        self.homeBtn.clicked.connect(self.show_home)
        self.installedBtn.clicked.connect(self.show_installed)
        self.updatesBtn.clicked.connect(self.show_updates)
        self.settingsBtn.clicked.connect(self.show_settings)
        self.aboutBtn.clicked.connect(self.show_about)
        
        # Connect category buttons
        self.allAppsBtn.clicked.connect(lambda: self.show_category("all"))
        self.accessibilityBtn.clicked.connect(lambda: self.show_category("accessibility"))
        self.developmentBtn.clicked.connect(lambda: self.show_category("development"))
        self.educationBtn.clicked.connect(lambda: self.show_category("education"))
        self.gamesBtn.clicked.connect(lambda: self.show_category("games"))
        self.graphicsBtn.clicked.connect(lambda: self.show_category("graphics"))
        self.internetBtn.clicked.connect(lambda: self.show_category("internet"))
        self.multimediaBtn.clicked.connect(lambda: self.show_category("multimedia"))
        self.officeBtn.clicked.connect(lambda: self.show_category("office"))
        self.scienceBtn.clicked.connect(lambda: self.show_category("science"))
        self.systemBtn.clicked.connect(lambda: self.show_category("system"))
        self.utilitiesBtn.clicked.connect(lambda: self.show_category("utilities"))
        
        self.load_initial_packages()

    def search_packages(self):
        query = self.search_input.text()
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
    
    def show_installed(self):
        self.current_packages = self.package_manager.get_installed_packages()
        self.update_package_display()
        self.statusbar.showMessage("Showing installed packages", 2000)
    
    def show_updates(self):
        # Mock updates - in real implementation would check for updates
        self.current_packages = []
        self.update_package_display()
        self.statusbar.showMessage("No updates available", 2000)
    
    def show_settings(self):
        self.statusbar.showMessage("Settings not implemented yet", 2000)
    
    def show_home(self):
        self.current_packages = self.package_manager.get_installed_packages()[:6]  # Featured apps
        self.update_package_display()
        self.statusbar.showMessage("Home - Featured applications", 2000)
    
    def show_about(self):
        self.statusbar.showMessage("About Apt-Ex Package Manager", 2000)
    
    def show_category(self, category):
        # Mock category filtering with more categories
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
        self.update_package_display()
        self.statusbar.showMessage(f"Showing {category} packages", 2000)