"""Refactored main view with panel controllers"""
from PyQt6.QtWidgets import QMainWindow, QPushButton
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon
from PyQt6 import uic
from settings.app_settings import AppSettings
from services.logging_service import LoggingService
from services.status_service import StatusService
from workers.cache_update_worker import CacheUpdateWorker
from views.panels.home_panel import HomePanel
from views.panels.installed_panel import InstalledPanel
from views.panels.updates_panel import UpdatesPanel
from views.panels.category_panel import CategoryPanel
from views.panels.settings_panel import SettingsPanel
from views.panels.about_panel import AboutPanel
from views.panels.category_list_panel import CategoryListPanel
from views.panels.package_detail_panel import PackageDetailPanel
import os


class MainView(QMainWindow):
    """Main application window"""
    
    def __init__(self, package_manager, lmdb_manager, logging_service=None, dev_logging=False, stdout_log_level='WARNING'):
        super().__init__()
        self.package_manager = package_manager
        self.lmdb_manager = lmdb_manager
        self.selected_button = None
        self.sidebar_buttons = {}
        self.panels = {}
        self.app_settings = AppSettings()
        self.cache_updating = False
        self.pending_action = None
        self.log_messages = []
        self.log_window = None
        
        # Setup logging
        if logging_service:
            self.logging_service = logging_service
        else:
            self.logging_service = LoggingService(stdout_log_level=stdout_log_level)
        self.logging_service.set_app_log_callback(self.add_log_message)
        self.logger = self.logging_service.get_logger('ui')
        
        # Pre-register loggers
        self.logging_service.get_logger('odrs')
        self.logging_service.get_logger('rating_cache')
        self.logging_service.get_logger('db.connection')
        
        if dev_logging:
            import logging
            self.logging_service.app_log_handler.setLevel(logging.DEBUG)
            self.logger.debug("Debug logging enabled")
        
        # Enable file logging if configured
        if self.app_settings.get_file_logging_enabled():
            log_dir = self.app_settings.get_log_directory()
            self.logging_service.enable_file_logging(log_dir)
        
        # Load UI
        uic.loadUi('src/ui/windows/main_window.ui', self)
        self.setMinimumSize(1150, 700)
        
        # Setup window icon
        self.setup_window_icon()
        
        # Setup status service
        self.status_service = StatusService(self.statusbar)
        
        # Setup UI
        self.setup_status_bar_log_icon()
        self.load_panels()
        self.setup_sidebar()
        self.setup_dev_mode(dev_logging)
        
        # Initial page
        self.select_page('home')
    
    def setup_window_icon(self):
        """Setup window icon based on theme"""
        base_path = os.path.join(os.path.dirname(__file__), '..', 'icons')
        palette = self.palette()
        is_dark = palette.color(palette.ColorRole.Window).lightness() < 128
        
        icon_path = os.path.join(base_path, 'app-icon-dark.svg' if is_dark else 'app-icon.svg')
        if not os.path.exists(icon_path):
            icon_path = os.path.join(base_path, 'app-icon.svg')
        
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            for size in [16, 32, 48, 64]:
                icon.addFile(icon_path, QSize(size, size))
            self.setWindowIcon(icon)
    
    def load_panels(self):
        """Load all panel controllers"""
        panel_configs = {
            'home': ('src/ui/panels/home_panel.ui', HomePanel),
            'installed': ('src/ui/panels/installed_panel.ui', InstalledPanel),
            'updates': ('src/ui/panels/updates_panel.ui', UpdatesPanel),
            'category': ('src/ui/panels/category_panel.ui', CategoryPanel),
            'category_list': ('src/ui/panels/category_list_panel.ui', CategoryListPanel),
            'package_detail': ('src/ui/panels/package_detail_panel.ui', PackageDetailPanel),
            'settings': ('src/ui/panels/settings_panel.ui', SettingsPanel),
            'about': ('src/ui/panels/about_panel.ui', AboutPanel)
        }
        
        for panel_name, (ui_file, panel_class) in panel_configs.items():
            try:
                panel = panel_class(ui_file, self.package_manager, self.lmdb_manager, 
                                   self.logging_service, self.app_settings)
                self.panels[panel_name] = panel
                self.contentStack.addWidget(panel)
                
                # Connect panel signals
                self.connect_panel_signals(panel_name, panel)
                
                self.logger.info(f"Loaded panel: {panel_name}")
            except Exception as e:
                self.logger.error(f"Failed to load panel {panel_name}: {e}")
    
    def connect_panel_signals(self, panel_name, panel):
        """Connect signals from panel controllers"""
        if panel_name == 'home':
            panel.install_requested.connect(self.install_package)
            panel.refresh_requested.connect(self.refresh_cache)
            panel.package_selected.connect(self.show_package_detail)
        elif panel_name == 'installed':
            panel.remove_requested.connect(self.remove_package)
            panel.package_selected.connect(self.show_package_detail)
        elif panel_name == 'updates':
            panel.update_requested.connect(self.update_package)
            panel.update_all_requested.connect(self.update_all_packages)
            panel.updates_count_changed.connect(self.update_updates_button)
        elif panel_name == 'category':
            panel.install_requested.connect(self.install_package)
            panel.refresh_requested.connect(self.refresh_cache)
            panel.package_selected.connect(self.show_package_detail)
        elif panel_name == 'package_detail':
            panel.back_requested.connect(self.return_from_detail)
            panel.install_requested.connect(self.install_package)
            panel.remove_requested.connect(self.remove_package)
        elif panel_name == 'settings':
            panel.default_repository_changed.connect(self.on_default_repository_changed)
    
    def setup_sidebar(self):
        """Setup sidebar navigation buttons"""
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
        
        # Connect main navigation
        self.homeBtn.clicked.connect(lambda: self.select_page('home'))
        self.installedBtn.clicked.connect(lambda: self.select_page('installed'))
        self.updatesBtn.clicked.connect(lambda: self.select_page('updates'))
        self.settingsBtn.clicked.connect(lambda: self.select_page('settings'))
        self.aboutBtn.clicked.connect(lambda: self.select_page('about'))
        
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
        self.viewCategoriesBtn.clicked.connect(lambda: self.select_page('category_list'))
        
        self.logger.info("Application started")
    
    def select_page(self, page_key):
        """Select a page by key"""
        self.logger.info(f"Navigated to {page_key} page")
        
        if page_key not in self.panels:
            self.logger.error(f"Panel {page_key} not found")
            return
        
        panel = self.panels[page_key]
        
        # Update button selection
        self.update_button_selection(page_key)
        
        # Switch to panel
        self.contentStack.setCurrentWidget(panel)
        
        # Update title
        self.pageTitle.setText(panel.get_title())
        
        # Update context actions
        self.update_context_actions(panel)
        
        # Notify panel it's being shown
        panel.on_show()
        
        # Update status
        self.status_service.show_message(f"{panel.get_title()}", 2000)
        
        # Save last selected page
        self.app_settings.set_last_selected_page(page_key)
    
    def select_category(self, category):
        """Select a category"""
        self.logger.info(f"Selected category: {category}")
        self.update_button_selection(category)
        
        panel = self.panels['category']
        self.contentStack.setCurrentWidget(panel)
        self.pageTitle.setText(panel.get_title())
        self.update_context_actions(panel)
        
        panel.load_category(category)
        self.status_service.show_message(f"Loading {category} packages", 2000)
    
    def update_button_selection(self, selected_key):
        """Update sidebar button selection"""
        if self.selected_button:
            self.selected_button.setProperty("selected", "false")
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)
        
        if selected_key in self.sidebar_buttons:
            self.selected_button = self.sidebar_buttons[selected_key]
            self.selected_button.setProperty("selected", "true")
            self.selected_button.style().unpolish(self.selected_button)
            self.selected_button.style().polish(self.selected_button)
    
    def update_context_actions(self, panel):
        """Update context actions for current panel"""
        # Clear existing actions
        layout = self.contextActions.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add panel-specific actions
        for text, callback in panel.get_context_actions():
            button = QPushButton(text)
            button.setFixedHeight(30)
            button.clicked.connect(callback)
            layout.addWidget(button)
    
    def show_package_detail(self, package_info):
        """Show package detail panel"""
        current_panel_key = None
        for key, panel in self.panels.items():
            if self.contentStack.currentWidget() == panel:
                current_panel_key = key
                break
        
        detail_panel = self.panels['package_detail']
        detail_panel.show_package(package_info, current_panel_key)
        self.contentStack.setCurrentWidget(detail_panel)
        self.pageTitle.setText(detail_panel.get_title())
        self.update_context_actions(detail_panel)
    
    def return_from_detail(self):
        """Return from detail panel to previous panel"""
        detail_panel = self.panels['package_detail']
        if detail_panel.return_panel and detail_panel.return_panel in self.panels:
            self.select_page(detail_panel.return_panel)
        else:
            self.select_page('home')
    
    def install_package(self, package_name, backend='apt'):
        """Install a package"""
        self.logger.info(f"User requested install: {package_name}")
        self.package_manager.install_package(package_name, backend=backend)
        self.status_service.show_message(f"Installing {package_name}...", 3000)
    
    def remove_package(self, package_name, backend='apt'):
        """Remove a package"""
        self.logger.info(f"User requested removal: {package_name}")
        self.status_service.show_message(f"Removing {package_name}...", 3000)
    
    def update_package(self, package_name):
        """Update a package"""
        self.logger.info(f"User requested update: {package_name}")
        self.status_service.show_message(f"Updating {package_name}...", 3000)
    
    def update_all_packages(self):
        """Update all packages"""
        self.logger.info("Starting system-wide package update")
        self.status_service.show_message("Updating all packages...", 3000)
    
    def update_updates_button(self, count):
        """Update the updates button text with count"""
        if count > 0:
            self.updatesBtn.setText(f"⬆️ Updates ({count})")
        else:
            self.updatesBtn.setText("⬆️ Updates")
    
    def on_default_repository_changed(self, repo_type):
        """Handle default repository change"""
        self.status_service.show_message(f"Set {repo_type.upper()} as default repository", 3000)
    
    def refresh_cache(self):
        """Refresh package cache"""
        if self.cache_updating:
            self.status_service.show_message("Cache update already in progress", 3000)
            return
        
        self.logger.info("User requested cache refresh")
        self.populate_caches_on_startup()
    
    def populate_caches_on_startup(self):
        """Refresh cache when manually requested"""
        self.cache_updating = True
        self.status_service.start_animation("Refreshing package data")
        
        self.cache_worker = CacheUpdateWorker(
            True, True, True,  # update_categories, update_packages, update_installed
            self.logging_service, self.lmdb_manager
        )
        self.cache_worker.finished_signal.connect(self.on_cache_update_finished)
        self.cache_worker.error_signal.connect(self.on_cache_update_error)
        self.cache_worker.progress_signal.connect(self.status_service.update_message)
        self.cache_worker.start()
    
    def on_cache_update_finished(self):
        """Handle cache update completion"""
        self.cache_updating = False
        self.status_service.stop_animation()
        self.logger.info("Package cache update completed")
        self.status_service.show_message("Package data updated", 3000)
        
        if self.pending_action:
            action = self.pending_action
            self.pending_action = None
            action()
    
    def on_cache_update_error(self, error_message):
        """Handle cache update error"""
        self.cache_updating = False
        self.status_service.stop_animation()
        self.logger.error(f"Cache update failed: {error_message}")
        self.status_service.show_message(f"Failed to update cache: {error_message}", 5000)
    
    def setup_status_bar_log_icon(self):
        """Add log icon to status bar"""
        from PyQt6.QtWidgets import QLabel
        
        # DB stats label
        self.db_stats_label = QLabel()
        self.db_stats_label.setStyleSheet("padding: 0 10px; font-size: 11px;")
        self.statusbar.addPermanentWidget(self.db_stats_label)
        
        # Update stats periodically
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_db_stats)
        self.stats_timer.start(500)
        self.update_db_stats()
        
        # Log button
        self.log_button = QPushButton("📋")
        self.log_button.setFixedSize(QSize(30, 20))
        self.log_button.setToolTip("View application logs")
        self.log_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: palette(highlight);
                border-radius: 3px;
            }
        """)
        self.log_button.clicked.connect(self.show_log_view)
        self.statusbar.addPermanentWidget(self.log_button)
    
    def update_db_stats(self):
        """Update database stats"""
        stats = "LMDB: Ready"
        try:
            from cache import PackageCacheModel
            pkg_cache = PackageCacheModel(self.lmdb_manager, 'apt')
            packages = pkg_cache.get_all_packages(limit=1)
            if packages:
                stats = "LMDB: Cached"
        except:
            pass
        self.db_stats_label.setText(stats)
    
    def add_log_message(self, message):
        """Add message to log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_messages.append(f"[{timestamp}] {message}")
        if len(self.log_messages) > 100:
            self.log_messages = self.log_messages[-100:]
    
    def show_log_view(self):
        """Show log view window"""
        if self.log_window and not self.log_window.isHidden():
            self.log_window.raise_()
            self.log_window.activateWindow()
        else:
            from views.log_view import LogView
            self.log_window = LogView(self.logging_service)
            self.log_window.show()
    
    def setup_dev_mode(self, dev_logging):
        """Setup development mode"""
        if dev_logging:
            self.show_log_view()
    
    def closeEvent(self, event):
        """Handle application close"""
        if hasattr(self, 'stats_timer'):
            self.stats_timer.stop()
        event.accept()
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()
