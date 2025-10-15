from PyQt6.QtWidgets import QMainWindow, QGridLayout, QLabel, QPushButton, QWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6 import uic
from models.package_model import Package
from settings.app_settings import AppSettings
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
        self.app_settings = AppSettings()
        uic.loadUi('src/ui/main_window.ui', self)
        
        # Set window icon based on theme
        def get_icon_path():
            base_path = os.path.join(os.path.dirname(__file__), '..', 'icons')
            # Check if dark theme is active
            palette = self.palette()
            is_dark = palette.color(palette.ColorRole.Window).lightness() < 128
            
            if is_dark:
                dark_icon = os.path.join(base_path, 'app-icon-dark.svg')
                if os.path.exists(dark_icon):
                    return dark_icon
            
            # Fallback to light icon
            return os.path.join(base_path, 'app-icon.svg')
        
        icon_path = get_icon_path()
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            # Add multiple sizes to ensure proper scaling
            icon.addFile(icon_path, QSize(16, 16))
            icon.addFile(icon_path, QSize(32, 32))
            icon.addFile(icon_path, QSize(48, 48))
            icon.addFile(icon_path, QSize(64, 64))
            self.setWindowIcon(icon)
        
        self.load_panels()
        self.setup_ui()
        self.restore_window_state()

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
            'utilities': self.utilitiesBtn,
            'categories': self.viewCategoriesBtn
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
        
        # Connect View Categories button
        self.viewCategoriesBtn.clicked.connect(lambda: self.view_categories())
        
        # Set initial selection to last used page
        last_page = self.app_settings.get_last_selected_page()
        page_indices = {'home': 0, 'installed': 1, 'updates': 2, 'category': 3, 'settings': 4, 'about': 5}
        self.select_page(last_page, page_indices.get(last_page, 0))
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
            'category_list': 'category_list_panel.ui',
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
        
        # Save last selected page
        self.app_settings.set_last_selected_page(page_key)
        
        # Update page title
        page_titles = {
            'home': 'Welcome to Apt-Ex Package Manager',
            'installed': 'Installed Packages',
            'updates': 'Available Updates',
            'settings': 'Settings',
            'about': 'About Apt-Ex Package Manager'
        }
        self.pageTitle.setText(page_titles.get(page_key, 'Apt-Ex Package Manager'))
        
        # Clear previous context actions
        self.clear_context_actions()
        
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
            self.setup_updates_context_actions()
            self.statusbar.showMessage("No updates available", 2000)
        elif page_key == 'settings':
            self.populate_settings_panel()
            self.update_default_repository_ui()
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
        
        # Load category packages using APT section mapping
        from controllers.apt_controller import APTController
        apt_controller = APTController()
        self.current_packages = apt_controller.get_packages_by_sidebar_category(category)
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
        """Update category display with KDE Discover-style list items"""
        category_panel = self.panels['category']
        layout = category_panel.packageListLayout
        
        # Clear existing items
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add package list items
        for package in self.current_packages[:20]:  # Show first 20
            package_item = self.create_package_list_item(package)
            layout.addWidget(package_item)
        
        # Add spacer at the end
        from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)
    
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
            
            # Connect default repository buttons
            if hasattr(settings_panel, 'makeDefaultFlatpak'):
                settings_panel.makeDefaultFlatpak.clicked.connect(
                    lambda: self.set_default_repository('flatpak')
                )
            if hasattr(settings_panel, 'makeDefaultApt'):
                settings_panel.makeDefaultApt.clicked.connect(
                    lambda: self.set_default_repository('apt')
                )
    
    def open_apt_sources(self):
        """Open /etc/apt/ folder in default file manager"""
        import subprocess
        try:
            subprocess.run(['xdg-open', '/etc/apt/'], check=True)
        except subprocess.CalledProcessError:
            self.statusbar.showMessage("Could not open /etc/apt/ folder", 3000)
    
    def set_default_repository(self, repo_type: str):
        """Set default repository type"""
        self.app_settings.set_default_repository(repo_type)
        self.update_default_repository_ui()
        self.statusbar.showMessage(f"Set {repo_type.upper()} as default repository", 3000)
    
    def update_default_repository_ui(self):
        """Update UI to reflect default repository setting"""
        if 'settings' not in self.panels:
            return
            
        settings_panel = self.panels['settings']
        default_repo = self.app_settings.get_default_repository()
        
        # Update Flatpak button
        if hasattr(settings_panel, 'makeDefaultFlatpak'):
            if default_repo == 'flatpak':
                settings_panel.makeDefaultFlatpak.setText('★ Default')
                settings_panel.makeDefaultFlatpak.setEnabled(False)
            else:
                settings_panel.makeDefaultFlatpak.setText('☆ Make Default')
                settings_panel.makeDefaultFlatpak.setEnabled(True)
        
        # Update APT button
        if hasattr(settings_panel, 'makeDefaultApt'):
            if default_repo == 'apt':
                settings_panel.makeDefaultApt.setText('★ Default')
                settings_panel.makeDefaultApt.setEnabled(False)
            else:
                settings_panel.makeDefaultApt.setText('☆ Make Default')
                settings_panel.makeDefaultApt.setEnabled(True)
    
    def restore_window_state(self):
        """Restore window geometry and state from settings"""
        geometry = self.app_settings.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.app_settings.get_window_state()
        if state:
            self.restoreState(state)
    
    def closeEvent(self, event):
        """Save window state when closing"""
        self.app_settings.set_window_geometry(self.saveGeometry())
        self.app_settings.set_window_state(self.saveState())
        event.accept()
    
    def clear_context_actions(self):
        """Clear all context action buttons"""
        layout = self.contextActions.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def add_context_action(self, text: str, callback):
        """Add a context action button"""
        from PyQt6.QtWidgets import QPushButton
        button = QPushButton(text)
        button.setFixedHeight(30)
        button.clicked.connect(callback)
        self.contextActions.layout().addWidget(button)
        return button
    
    def setup_updates_context_actions(self):
        """Setup context actions for updates page"""
        self.add_context_action("🔄 Refresh", self.refresh_updates)
        self.add_context_action("⬆️ Update All", self.update_all_packages)
    
    def refresh_updates(self):
        """Refresh available updates"""
        self.statusbar.showMessage("Refreshing updates...", 2000)
    
    def update_all_packages(self):
        """Update all available packages"""
        self.statusbar.showMessage("Updating all packages...", 3000)
    
    def populate_category_list(self):
        """Populate the category list with cached APT sections"""
        from PyQt6.QtWidgets import QTreeWidgetItem
        from cache.category_cache import CategoryCache
        from controllers.apt_controller import APTController
        
        category_panel = self.panels['category_list']
        tree = category_panel.categoryTree
        tree.clear()
        
        # Get cached categories or fetch fresh data
        cache = CategoryCache()
        section_details = cache.get_categories('apt')
        
        if section_details is None:
            # Cache miss - fetch fresh data
            apt_controller = APTController()
            section_details = apt_controller.get_section_details()
            cache.set_categories('apt', section_details)
        
        for section, data in sorted(section_details.items()):
            if isinstance(data, dict):
                # Hierarchical section with subcategories
                total_packages = sum(data.values())
                section_item = QTreeWidgetItem([f"📁 {section} ({total_packages} packages)"])
                tree.addTopLevelItem(section_item)
                
                # Add subcategories
                for subcategory, count in sorted(data.items()):
                    subcat_item = QTreeWidgetItem([f"📄 {subcategory} ({count} packages)"])
                    section_item.addChild(subcat_item)
            else:
                # Flat section
                section_item = QTreeWidgetItem([f"📁 {section} ({data} packages)"])
                tree.addTopLevelItem(section_item)
        
        # Expand all categories by default
        tree.expandAll()
    
    def create_package_list_item(self, package):
        """Create a KDE Discover-style package list item"""
        from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
        from PyQt6.QtCore import Qt
        
        # Main container
        item_widget = QFrame()
        item_widget.setFrameStyle(QFrame.Shape.Box)
        item_widget.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 8px;
                margin: 2px;
            }
            QFrame:hover {
                background-color: palette(alternate-base);
            }
        """)
        item_widget.setFixedHeight(80)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(item_widget)
        main_layout.setSpacing(12)
        
        # Icon placeholder
        icon_label = QLabel("📦")
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px; background-color: palette(button); border-radius: 8px;")
        main_layout.addWidget(icon_label)
        
        # Content area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        # Package name
        name_label = QLabel(package.name)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: palette(text);")
        content_layout.addWidget(name_label)
        
        # Package description
        desc_text = package.description[:80] + "..." if len(package.description) > 80 else package.description
        desc_label = QLabel(desc_text)
        desc_label.setStyleSheet("font-size: 12px; color: palette(mid);")
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)
        
        # Rating placeholder (stars)
        rating_label = QLabel("★★★★☆ 4.2 ratings")
        rating_label.setStyleSheet("font-size: 11px; color: palette(mid);")
        content_layout.addWidget(rating_label)
        
        main_layout.addLayout(content_layout)
        
        # Right side - Install button
        install_btn = QPushButton("⬇ Install")
        install_btn.setFixedSize(80, 32)
        install_btn.setStyleSheet("""
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        install_btn.clicked.connect(lambda: self.install_package(package.name))
        main_layout.addWidget(install_btn)
        
        return item_widget
    
    def view_categories(self):
        """Show categories view"""
        self.update_button_selection('categories')
        # Use category_list panel (index 4)
        panel_index = list(self.panels.keys()).index('category_list')
        self.contentStack.setCurrentIndex(panel_index)
        self.pageTitle.setText("Browse Categories")
        self.populate_category_list()
        self.statusbar.showMessage("Browse packages by category", 2000)