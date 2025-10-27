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
        
        # Setup daemon controls
        self.setup_daemon_controls()
    
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
    
    def setup_daemon_controls(self):
        """Setup update daemon controls"""
        from PyQt6.QtWidgets import QCheckBox, QComboBox, QSpacerItem, QSizePolicy
        from utils.daemon_manager import DaemonManager
        
        # Create daemon section
        daemon_group = QGroupBox("Update Notifications")
        daemon_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 13px; }")
        daemon_layout = QVBoxLayout(daemon_group)
        
        # Enable checkbox
        self.daemon_enabled_checkbox = QCheckBox("Enable automatic update checks")
        self.daemon_enabled_checkbox.setChecked(self.app_settings.get_update_check_enabled())
        self.daemon_enabled_checkbox.toggled.connect(self.on_daemon_enabled_changed)
        daemon_layout.addWidget(self.daemon_enabled_checkbox)
        
        # Interval selector
        interval_container = QWidget()
        interval_layout = QHBoxLayout(interval_container)
        interval_layout.setContentsMargins(20, 0, 0, 0)
        interval_layout.addWidget(QLabel("Check interval:"))
        
        self.interval_combo = QComboBox()
        self.interval_combo.addItem("Every 30 minutes", 30)
        self.interval_combo.addItem("Every hour", 60)
        self.interval_combo.addItem("Every 2 hours", 120)
        self.interval_combo.addItem("Every 4 hours", 240)
        self.interval_combo.addItem("Every 12 hours", 720)
        self.interval_combo.addItem("Every 24 hours", 1440)
        self.interval_combo.addItem("Weekly", 10080)
        self.interval_combo.addItem("Biweekly", 20160)
        self.interval_combo.addItem("Monthly", 43200)
        self.interval_combo.addItem("Never", 0)
        
        current_interval = self.app_settings.get_update_check_interval()
        index = self.interval_combo.findData(current_interval)
        if index >= 0:
            self.interval_combo.setCurrentIndex(index)
        
        self.interval_combo.currentIndexChanged.connect(self.on_interval_changed)
        interval_layout.addWidget(self.interval_combo)
        interval_layout.addStretch()
        daemon_layout.addWidget(interval_container)
        
        # Daemon status
        status_container = QWidget()
        status_layout = QVBoxLayout(status_container)
        status_layout.setContentsMargins(0, 10, 0, 0)
        
        self.daemon_status_label = QLabel()
        self.daemon_status_label.setStyleSheet("font-weight: normal; font-size: 11px;")
        status_layout.addWidget(self.daemon_status_label)
        
        self.daemon_last_check_label = QLabel()
        self.daemon_last_check_label.setStyleSheet("font-weight: normal; font-size: 11px; color: gray;")
        status_layout.addWidget(self.daemon_last_check_label)
        
        daemon_layout.addWidget(status_container)
        
        # Control buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 5, 0, 0)
        
        self.check_now_btn = QPushButton("Check Now")
        self.check_now_btn.clicked.connect(self.on_check_now)
        button_layout.addWidget(self.check_now_btn)
        
        button_layout.addStretch()
        daemon_layout.addWidget(button_container)
        
        # Add to main layout (insert after ODRS section if it exists)
        main_layout = self.layout()
        if main_layout:
            # Find a good position to insert
            insert_index = 0
            for i in range(main_layout.count()):
                widget = main_layout.itemAt(i).widget()
                if widget and isinstance(widget, QGroupBox):
                    insert_index = i + 1
                    break
            main_layout.insertWidget(insert_index, daemon_group)
        
        # Update daemon status
        self.update_daemon_status()
        
        # Setup timer to update status periodically
        from PyQt6.QtCore import QTimer
        self.daemon_status_timer = QTimer()
        self.daemon_status_timer.timeout.connect(self.update_daemon_status)
        self.daemon_status_timer.start(5000)  # Update every 5 seconds
    
    def update_daemon_status(self):
        """Update daemon status display"""
        from utils.daemon_manager import DaemonManager
        from services.update_daemon_client import UpdateDaemonClient
        from datetime import datetime
        
        status = DaemonManager.get_status()
        
        # Check if daemon is actually running via D-Bus (more reliable)
        client = UpdateDaemonClient(self.logging_service)
        is_running = client.is_available()
        
        # Status label
        if is_running:
            self.daemon_status_label.setText("Daemon Status: ● Running")
            self.daemon_status_label.setStyleSheet("font-weight: normal; font-size: 11px; color: green;")
        else:
            self.daemon_status_label.setText("Daemon Status: ○ Stopped")
            self.daemon_status_label.setStyleSheet("font-weight: normal; font-size: 11px; color: red;")
        
        # Last check label
        last_check = self.app_settings.get_last_update_check()
        if last_check:
            try:
                check_time = datetime.fromisoformat(last_check)
                time_diff = datetime.now() - check_time
                if time_diff.total_seconds() < 60:
                    time_str = "just now"
                elif time_diff.total_seconds() < 3600:
                    minutes = int(time_diff.total_seconds() / 60)
                    time_str = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                elif time_diff.total_seconds() < 86400:
                    hours = int(time_diff.total_seconds() / 3600)
                    time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
                else:
                    days = int(time_diff.total_seconds() / 86400)
                    time_str = f"{days} day{'s' if days != 1 else ''} ago"
                self.daemon_last_check_label.setText(f"Last check: {time_str}")
            except:
                self.daemon_last_check_label.setText("Last check: Unknown")
        else:
            self.daemon_last_check_label.setText("Last check: Never")
        
        # Update button states
        self.check_now_btn.setEnabled(is_running)
    
    def on_daemon_enabled_changed(self, enabled):
        """Handle daemon enabled checkbox change"""
        self.app_settings.set_update_check_enabled(enabled)
        self.logger.info(f"Update checks {'enabled' if enabled else 'disabled'}")
    
    def on_interval_changed(self, index):
        """Handle interval change"""
        minutes = self.interval_combo.itemData(index)
        self.app_settings.set_update_check_interval(minutes)
        self.logger.info(f"Update check interval set to {minutes} minutes")
        
        # Update daemon if running
        try:
            from services.update_daemon_client import UpdateDaemonClient
            client = UpdateDaemonClient(self.logging_service)
            if client.is_available():
                client.set_check_interval(minutes)
        except:
            pass
    
    def on_check_now(self):
        """Trigger immediate update check"""
        try:
            from services.update_daemon_client import UpdateDaemonClient
            client = UpdateDaemonClient(self.logging_service)
            if client.is_available():
                client.check_now()
                self.logger.info("Triggered update check")
            else:
                self.logger.warning("Daemon not available")
        except Exception as e:
            self.logger.error(f"Failed to trigger check: {e}")
    

