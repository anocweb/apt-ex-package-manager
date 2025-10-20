"""Updates panel controller"""
from PyQt6.QtWidgets import QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from .base_panel import BasePanel
from workers.update_check_worker import UpdateCheckWorker
from widgets.update_list_item import UpdateListItem


class UpdatesPanel(BasePanel):
    """Panel for displaying available updates"""
    
    update_requested = pyqtSignal(str)
    update_all_requested = pyqtSignal()
    updates_count_changed = pyqtSignal(int)
    package_selected = pyqtSignal(dict)
    
    def __init__(self, ui_file, package_manager, lmdb_manager, logging_service, app_settings):
        self.updates_available = False
        super().__init__(ui_file, package_manager, lmdb_manager, logging_service, app_settings)
    
    def on_show(self):
        """Load updates when shown"""
        self.load_updates()
    
    def get_context_actions(self):
        """Return context actions for updates panel"""
        actions = [
            ("🔄 Refresh", self.load_updates),
            ("⬆️ Update All", self.on_update_all)
        ]
        return actions
    
    def get_title(self):
        """Return panel title"""
        return "Available Updates"
    
    def load_updates(self):
        """Load available updates using worker thread"""
        scroll_widget = self.updatesScrollArea.widget()
        container_layout = scroll_widget.layout()
        
        # Clear existing items
        while container_layout.count():
            item = container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get APT backend
        apt_backend = self.package_manager.get_backend('apt')
        if not apt_backend:
            return
        
        # Create and start worker
        self.worker = UpdateCheckWorker(apt_backend)
        self.worker.finished_signal.connect(self.on_updates_loaded)
        self.worker.error_signal.connect(self.on_error)
        self.worker.start()
    
    def on_updates_loaded(self, updates):
        """Handle updates loaded from worker"""
        scroll_widget = self.updatesScrollArea.widget()
        container_layout = scroll_widget.layout()
        
        # Clear loading message
        while container_layout.count():
            item = container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Emit count for sidebar update
        self.updates_count_changed.emit(len(updates))
        
        if not updates:
            self.updates_available = False
            no_updates_label = QLabel("✓ All packages are up to date")
            no_updates_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_updates_label.setStyleSheet("font-size: 18px; color: palette(window-text);")
            
            top_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            container_layout.addItem(top_spacer)
            container_layout.addWidget(no_updates_label)
            bottom_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            container_layout.addItem(bottom_spacer)
        else:
            self.updates_available = True
            # Sort: security updates first
            security_updates = [u for u in updates if u.get('is_security', False)]
            regular_updates = [u for u in updates if not u.get('is_security', False)]
            sorted_updates = security_updates + regular_updates
            
            # Add update items
            for update_info in sorted_updates:
                item = UpdateListItem(update_info)
                item.update_requested.connect(self.update_requested.emit)
                item.double_clicked.connect(lambda u=update_info: self.package_selected.emit(u))
                container_layout.addWidget(item)
            
            # Add spacer at bottom
            spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            container_layout.addItem(spacer)
        
        scroll_widget.updateGeometry()
        self.updatesScrollArea.updateGeometry()
    
    def on_error(self, error_message):
        """Handle error loading updates"""
        scroll_widget = self.updatesScrollArea.widget()
        container_layout = scroll_widget.layout()
        
        # Clear loading message
        while container_layout.count():
            item = container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        error_label = QLabel(f"Error checking for updates: {error_message}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: #FF6B6B; font-size: 14px;")
        container_layout.addWidget(error_label)
        
        self.updates_count_changed.emit(0)
    
    def on_update_all(self):
        """Handle update all request"""
        if self.updates_available:
            self.update_all_requested.emit()
