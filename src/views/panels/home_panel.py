"""Home panel controller"""
from PyQt6.QtWidgets import QGridLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from .base_panel import BasePanel


class HomePanel(BasePanel):
    """Home panel with search and featured packages"""
    
    install_requested = pyqtSignal(str)
    refresh_requested = pyqtSignal()
    
    def __init__(self, ui_file, package_manager, lmdb_manager, logging_service, app_settings):
        self.current_packages = []
        super().__init__(ui_file, package_manager, lmdb_manager, logging_service, app_settings)
    
    def setup_ui(self):
        """Setup home panel UI"""
        self.package_layout = QGridLayout(self.package_container)
        
        # Add backend selector
        self.backend_selector = QComboBox()
        self.backend_selector.addItem("All Backends", None)
        for backend_id in self.package_manager.get_available_backends():
            backend = self.package_manager.get_backend(backend_id)
            self.backend_selector.addItem(backend.display_name, backend_id)
        
        # Add to layout if search_input has a parent layout
        if self.search_input.parent() and self.search_input.parent().layout():
            self.search_input.parent().layout().insertWidget(0, self.backend_selector)
    
    def connect_signals(self):
        """Connect signals"""
        self.search_input.textChanged.connect(self.on_search)
        self.backend_selector.currentIndexChanged.connect(self.on_backend_changed)
    
    def on_show(self):
        """Load initial packages when shown"""
        self.load_initial_packages()
    
    def get_context_actions(self):
        """Return context actions for home panel"""
        return [("🔄 Refresh Cache", self.on_refresh)]
    
    def get_title(self):
        """Return panel title"""
        return "Welcome to Apt-Ex Package Manager"
    
    def on_search(self):
        """Handle search text change"""
        query = self.search_input.text()
        selected_backend = self.backend_selector.currentData()
        
        if query:
            self.logger.info(f"Searching packages: {query} (backend: {selected_backend or 'all'})")
            self.current_packages = self.package_manager.search_packages(query, backend=selected_backend)
        else:
            self.current_packages = self.package_manager.get_installed_packages(backend=selected_backend or 'apt')
        
        self.update_display()
    
    def on_backend_changed(self, index):
        """Handle backend selector change"""
        selected_backend = self.backend_selector.currentData()
        self.logger.info(f"Backend changed to: {selected_backend or 'all'}")
        self.on_search()
    
    def load_initial_packages(self):
        """Load initial featured packages"""
        self.current_packages = self.package_manager.get_installed_packages(backend='apt', limit=6)
        self.update_display()
    
    def update_display(self):
        """Update package display"""
        # Clear existing widgets
        for i in reversed(range(self.package_layout.count())):
            self.package_layout.itemAt(i).widget().setParent(None)
        
        # Add package cards in grid
        row, col = 0, 0
        for package in self.current_packages[:20]:
            card = self.create_package_card(package)
            self.package_layout.addWidget(card, row, col)
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def create_package_card(self, package):
        """Create a package card widget"""
        from PyQt6.QtWidgets import QWidget
        
        card = QWidget()
        card.setFixedSize(200, 120)
        card.setStyleSheet("QWidget { border: 1px solid gray; border-radius: 5px; padding: 5px; }")
        
        layout = QGridLayout(card)
        
        # Name with backend badge
        name_text = package.name
        if hasattr(package, 'backend'):
            backend_badge = f" [{package.backend.upper()}]"
            name_label = QLabel(name_text)
            name_label.setStyleSheet("font-weight: bold;")
            badge_label = QLabel(backend_badge)
            badge_label.setStyleSheet("font-size: 9px; color: palette(mid);")
            layout.addWidget(name_label, 0, 0)
            layout.addWidget(badge_label, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            name_label = QLabel(name_text)
            name_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(name_label, 0, 0, 1, 2)
        
        desc_label = QLabel(package.description[:50] + "..." if len(package.description) > 50 else package.description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label, 1, 0, 1, 2)
        
        install_btn = QPushButton("Install")
        install_btn.clicked.connect(lambda: self.install_requested.emit(package.name))
        layout.addWidget(install_btn, 2, 0)
        
        return card
    
    def on_refresh(self):
        """Handle refresh request"""
        self.refresh_requested.emit()
