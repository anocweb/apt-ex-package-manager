"""Settings panel controller with dynamic backend integration"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTreeWidget, QTreeWidgetItem, QGroupBox)
from PyQt6.QtCore import pyqtSignal
from .base_panel import BasePanel
from widgets.backend_priority_widget import BackendPriorityWidget
from utils.settings_widget_factory import SettingsWidgetFactory
import subprocess


class SettingsPanel(BasePanel):
    """Panel for application settings with dynamic backend integration"""
    
    default_repository_changed = pyqtSignal(str)
    
    def setup_ui(self):
        """Setup settings panel UI"""
        # Setup backend priority widget
        self.priority_widget = BackendPriorityWidget()
        self.priorityContainerLayout.addWidget(self.priority_widget)
        
        # Load current priority
        self.load_backend_priority()
        
        # Load backends and their settings
        self.current_sort = 'priority'
        self.load_backend_sections()
    
    def connect_signals(self):
        """Connect signals"""
        if hasattr(self, 'odrsEnabledCheckbox'):
            self.odrsEnabledCheckbox.toggled.connect(self.set_odrs_enabled)
            self.odrsEnabledCheckbox.setChecked(self.app_settings.get_odrs_enabled())
        
        self.priority_widget.priority_changed.connect(self.on_priority_changed)
        
        if hasattr(self, 'sortComboBox'):
            self.sortComboBox.currentTextChanged.connect(self.on_sort_changed)
    
    def get_title(self):
        """Return panel title"""
        return "Settings"
    
    def load_backend_priority(self):
        """Load backend priority from settings"""
        try:
            # Get available backends
            available_backends = self.package_manager.get_available_backends()
            
            if not available_backends:
                self.logger.warning("No backends available")
                return
            
            # Get saved priority
            saved_priority = self.app_settings.get_backend_priority()
            
            # Build backend list with display names
            backend_list = []
            for backend_id in available_backends:
                backend = self.package_manager.get_backend(backend_id)
                if backend:
                    backend_list.append({
                        'id': backend_id,
                        'display_name': backend.display_name
                    })
            
            if not backend_list:
                self.logger.warning("No valid backends found")
                return
            
            self.priority_widget.set_backends(backend_list)
            
            # Apply saved priority order
            if saved_priority:
                # Filter to only include available backends
                valid_priority = [bid for bid in saved_priority if bid in available_backends]
                # Add any new backends not in saved priority
                for bid in available_backends:
                    if bid not in valid_priority:
                        valid_priority.append(bid)
                self.priority_widget.set_priority_order(valid_priority)
            else:
                # Use discovery order as default
                self.priority_widget.set_priority_order(available_backends)
        except Exception as e:
            self.logger.error(f"Error loading backend priority: {e}")
    
    def on_priority_changed(self, priority_order):
        """Handle priority order change"""
        self.app_settings.set_backend_priority(priority_order)
        self.logger.info(f"Backend priority updated: {priority_order}")
        
        # Update backend section headers if sorted by priority
        if self.current_sort == 'priority':
            self.refresh_backend_sections()
    
    def on_sort_changed(self, sort_text):
        """Handle sort order change"""
        self.current_sort = 'priority' if sort_text == 'Priority' else 'alphabetical'
        self.refresh_backend_sections()
    
    def load_backend_sections(self):
        """Load backend-specific settings sections"""
        try:
            # Clear existing backend sections
            layout = self.backendSettingsLayout
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # Get available backends
            available_backends = self.package_manager.get_available_backends()
            
            if not available_backends:
                self.logger.warning("No backends available for settings")
                return
            
            # Order backends based on current sort
            if self.current_sort == 'alphabetical':
                # Sort alphabetically by display name
                backend_items = []
                for backend_id in available_backends:
                    backend = self.package_manager.get_backend(backend_id)
                    if backend:
                        backend_items.append((backend.display_name, backend_id, backend))
                backend_items.sort(key=lambda x: x[0])
                ordered_backends = [(bid, backend, None) for _, bid, backend in backend_items]
            else:
                # Sort by priority
                priority_order = self.app_settings.get_backend_priority()
                if priority_order:
                    ordered_backend_ids = [bid for bid in priority_order if bid in available_backends]
                    for bid in available_backends:
                        if bid not in ordered_backend_ids:
                            ordered_backend_ids.append(bid)
                else:
                    ordered_backend_ids = available_backends
                
                ordered_backends = []
                for index, backend_id in enumerate(ordered_backend_ids):
                    backend = self.package_manager.get_backend(backend_id)
                    if backend:
                        ordered_backends.append((backend_id, backend, index + 1))
            
            # Create section for each backend
            for backend_id, backend, priority_num in ordered_backends:
                section = self.create_backend_section(backend, priority_num)
                layout.addWidget(section)
        except Exception as e:
            self.logger.error(f"Error loading backend sections: {e}")
    
    def refresh_backend_sections(self):
        """Refresh backend sections to update priority numbers"""
        self.load_backend_sections()
    
    def create_backend_section(self, backend, priority_num):
        """Create settings section for a backend
        
        Args:
            backend: Backend controller instance
            priority_num: Priority position (1 = highest) or None for alphabetical
        
        Returns:
            QGroupBox containing backend settings
        """
        if priority_num:
            title = f"{backend.display_name} (#{priority_num} Priority)"
        else:
            title = backend.display_name
        
        group = QGroupBox(title)
        group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        layout = QVBoxLayout(group)
        
        # Check if backend provides custom widget
        custom_widget = backend.get_settings_widget(group)
        if custom_widget:
            layout.addWidget(custom_widget)
        else:
            # Try to generate from schema
            schema = backend.get_settings_schema()
            if schema:
                current_values = self.app_settings.get_all_plugin_settings(backend.backend_id)
                factory = SettingsWidgetFactory()
                factory.setting_changed.connect(
                    lambda key, value, bid=backend.backend_id: self.on_backend_setting_changed(bid, key, value)
                )
                settings_widget = factory.create_widget_from_schema(schema, current_values)
                layout.addWidget(settings_widget)
            else:
                # No settings available
                no_settings_label = QLabel("No configurable settings for this backend.")
                no_settings_label.setStyleSheet("color: gray; font-style: italic;")
                layout.addWidget(no_settings_label)
        
        # Add repository management section if backend supports it
        if 'repositories' in backend.get_capabilities():
            repo_section = self.create_repository_section(backend)
            layout.addWidget(repo_section)
        
        return group
    
    def create_repository_section(self, backend):
        """Create repository management section for backend"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Header with actions
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        repo_label = QLabel("Repository Sources")
        repo_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        header_layout.addWidget(repo_label)
        header_layout.addStretch()
        
        # Backend-specific action buttons
        if backend.backend_id == 'apt':
            sources_btn = QPushButton("📦 Software Sources")
            sources_btn.clicked.connect(lambda: self.open_apt_sources())
            header_layout.addWidget(sources_btn)
        
        layout.addWidget(header)
        
        # Repository list (placeholder for now)
        repo_tree = QTreeWidget()
        repo_tree.setHeaderHidden(True)
        repo_tree.setRootIsDecorated(False)
        repo_tree.setMaximumHeight(150)
        
        # Add placeholder items
        item = QTreeWidgetItem([f"Repository management for {backend.display_name}"])
        repo_tree.addTopLevelItem(item)
        
        layout.addWidget(repo_tree)
        
        return container
    
    def on_backend_setting_changed(self, backend_id, key, value):
        """Handle backend setting change"""
        self.app_settings.set_backend_setting(backend_id, key, value)
        self.logger.info(f"Backend setting changed: {backend_id}.{key} = {value}")
        
        # Notify backend of setting change
        backend = self.package_manager.get_backend(backend_id)
        if backend:
            backend.on_settings_changed(key, value)
    
    def open_apt_sources(self):
        """Open /etc/apt/ folder in file manager"""
        self.logger.info("Opening APT sources folder")
        try:
            subprocess.run(['xdg-open', '/etc/apt/'], check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to open APT sources: {e}")
    
    def set_odrs_enabled(self, enabled):
        """Set ODRS enabled setting"""
        self.app_settings.set_odrs_enabled(enabled)
        self.logger.info(f"ODRS {'enabled' if enabled else 'disabled'}")
