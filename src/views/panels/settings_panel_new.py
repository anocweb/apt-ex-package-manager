"""Settings panel controller with dynamic backend integration"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTreeWidget, QTreeWidgetItem, QGroupBox, QListWidgetItem)
from PyQt6.QtCore import pyqtSignal, Qt
from .base_panel import BasePanel
from utils.settings_widget_factory import SettingsWidgetFactory
from widgets.backend_preference_item import BackendPreferenceItem
import subprocess


class SettingsPanel(BasePanel):
    """Panel for application settings with dynamic backend integration"""
    
    default_repository_changed = pyqtSignal(str)
    
    def setup_ui(self):
        """Setup settings panel UI"""
        # Setup general settings
        self.setup_general_settings()
        
        # Setup backend preference radio buttons
        self.setup_backend_preference()
        
        # Load backend sections in priority order
        self.load_backend_sections()
    
    def connect_signals(self):
        """Connect signals"""
        if hasattr(self, 'odrsEnabledCheckbox'):
            self.odrsEnabledCheckbox.toggled.connect(self.set_odrs_enabled)
            self.odrsEnabledCheckbox.setChecked(self.app_settings.get_odrs_enabled())
        
        if hasattr(self, 'updateCheckEnabled'):
            self.updateCheckEnabled.toggled.connect(self.on_update_check_changed)
            self.updateCheckEnabled.setChecked(self.app_settings.get_update_check_enabled())
        
        if hasattr(self, 'updateIntervalCombo'):
            self.updateIntervalCombo.currentIndexChanged.connect(self.on_interval_changed)
        
        if hasattr(self, 'backendPriorityList'):
            self.backendPriorityList.model().rowsMoved.connect(self.on_backend_priority_changed)
    
    def get_title(self):
        """Return panel title"""
        return "Settings"
    
    def setup_general_settings(self):
        """Setup general settings section"""
        # Load ODRS setting
        if hasattr(self, 'odrsEnabledCheckbox'):
            self.odrsEnabledCheckbox.setChecked(self.app_settings.get_odrs_enabled())
        
        # Load update check settings
        if hasattr(self, 'updateCheckEnabled'):
            self.updateCheckEnabled.setChecked(self.app_settings.get_update_check_enabled())
        
        if hasattr(self, 'updateIntervalCombo'):
            # Map minutes to combo index
            interval_map = {60: 0, 120: 1, 240: 2, 360: 3, 720: 4, 1440: 5}
            current_interval = self.app_settings.get_update_check_interval()
            index = interval_map.get(current_interval, 2)  # Default to 4 hours
            self.updateIntervalCombo.setCurrentIndex(index)
    
    def setup_backend_preference(self):
        """Setup backend preference drag-and-drop list"""
        try:
            available_backends = self.package_manager.get_available_backends()
            if not available_backends:
                return
            
            # Get priority order
            priority_order = self.app_settings.get_backend_priority()
            if priority_order:
                ordered_backends = [bid for bid in priority_order if bid in available_backends]
                for bid in available_backends:
                    if bid not in ordered_backends:
                        ordered_backends.append(bid)
            else:
                ordered_backends = available_backends
            
            # Get enabled backends
            enabled_backends = self.app_settings.get('enabled_backends', ordered_backends)
            if not isinstance(enabled_backends, list):
                enabled_backends = ordered_backends
            
            # Populate list
            for backend_id in ordered_backends:
                backend = self.package_manager.get_backend(backend_id)
                if backend:
                    enabled = backend_id in enabled_backends
                    
                    # Get plugin status
                    status = self.package_manager.plugin_status.get(backend_id, {})
                    
                    widget = BackendPreferenceItem(backend_id, backend.display_name, enabled, status)
                    widget.enabled_changed.connect(self.on_backend_enabled_changed)
                    
                    item = QListWidgetItem()
                    item.setData(Qt.ItemDataRole.UserRole, backend_id)
                    item.setSizeHint(widget.sizeHint())
                    self.backendPriorityList.addItem(item)
                    self.backendPriorityList.setItemWidget(item, widget)
            
            # Adjust height to fit items
            if self.backendPriorityList.count() > 0:
                item_height = self.backendPriorityList.sizeHintForRow(0)
                total_height = item_height * self.backendPriorityList.count() + 10
                self.backendPriorityList.setFixedHeight(total_height)
        except Exception as e:
            self.logger.error(f"Error setting up backend preference: {e}")
    
    def on_backend_enabled_changed(self, backend_id, enabled):
        """Handle backend enabled/disabled"""
        try:
            enabled_backends = self.app_settings.get('enabled_backends', [])
            if not isinstance(enabled_backends, list):
                enabled_backends = []
            
            if enabled and backend_id not in enabled_backends:
                enabled_backends.append(backend_id)
            elif not enabled and backend_id in enabled_backends:
                enabled_backends.remove(backend_id)
            
            self.app_settings.set('enabled_backends', enabled_backends)
            self.logger.info(f"Backend {backend_id} {'enabled' if enabled else 'disabled'}")
            
            # Reload backend sections to show/hide settings
            self.load_backend_sections()
        except Exception as e:
            self.logger.error(f"Error updating backend enabled state: {e}")
    
    def on_backend_priority_changed(self):
        """Handle backend priority reordering"""
        try:
            priority_order = []
            for i in range(self.backendPriorityList.count()):
                item = self.backendPriorityList.item(i)
                backend_id = item.data(Qt.ItemDataRole.UserRole)
                priority_order.append(backend_id)
            
            self.app_settings.set_backend_priority(priority_order)
            self.logger.info(f"Backend priority updated: {priority_order}")
            
            # Set first enabled backend as default
            enabled_backends = self.app_settings.get('enabled_backends', priority_order)
            for backend_id in priority_order:
                if backend_id in enabled_backends:
                    self.app_settings.set_default_repository(backend_id)
                    self.default_repository_changed.emit(backend_id)
                    break
            
            # Reload backend sections
            self.load_backend_sections()
        except Exception as e:
            self.logger.error(f"Error updating backend priority: {e}")
    
    def load_backend_sections(self):
        """Load backend-specific settings sections in priority order"""
        try:
            layout = self.backendSectionsLayout
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            available_backends = self.package_manager.get_available_backends()
            if not available_backends:
                return
            
            # Get priority order and enabled backends
            priority_order = self.app_settings.get_backend_priority()
            if priority_order:
                ordered_backends = [bid for bid in priority_order if bid in available_backends]
                for bid in available_backends:
                    if bid not in ordered_backends:
                        ordered_backends.append(bid)
            else:
                ordered_backends = available_backends
            
            enabled_backends = self.app_settings.get('enabled_backends', ordered_backends)
            if not isinstance(enabled_backends, list):
                enabled_backends = ordered_backends
            
            # Create section for each backend
            for backend_id in ordered_backends:
                backend = self.package_manager.get_backend(backend_id)
                if backend:
                    is_enabled = backend_id in enabled_backends
                    section = self.create_backend_section(backend, is_enabled)
                    layout.addWidget(section)
        except Exception as e:
            self.logger.error(f"Error loading backend sections: {e}")
    
    def create_backend_section(self, backend, is_enabled=True):
        """Create settings section for a backend
        
        Args:
            backend: Backend controller instance
            is_enabled: Whether the backend is enabled
        
        Returns:
            QWidget containing backend settings
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Backend title
        title_text = backend.display_name
        if not is_enabled:
            title_text += " (disabled)"
        title_label = QLabel(title_text)
        if is_enabled:
            title_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        else:
            title_label.setStyleSheet("font-weight: bold; font-size: 18px; color: palette(mid);")
        layout.addWidget(title_label)
        
        # Only show settings if enabled
        if not is_enabled:
            return container
        
        # Check if backend provides custom widget
        custom_widget = backend.get_settings_widget(container)
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
                no_settings_label = QLabel("No configurable settings.")
                no_settings_label.setStyleSheet("color: palette(mid); font-style: italic;")
                layout.addWidget(no_settings_label)
        
        # Add repository management section if backend supports it
        if 'repositories' in backend.get_capabilities():
            repo_section = self.create_repository_section(backend)
            layout.addWidget(repo_section)
        
        return container
    
    def create_repository_section(self, backend):
        """Create repository management section for backend"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Sources label
        sources_label = QLabel("Sources")
        sources_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(sources_label)
        
        # Repository table (placeholder)
        repo_tree = QTreeWidget()
        repo_tree.setHeaderLabels(["Enabled", "URI", "Suite", "Components"])
        repo_tree.setRootIsDecorated(False)
        repo_tree.setMaximumHeight(150)
        
        # Add placeholder items for APT
        if backend.backend_id == 'apt':
            item = QTreeWidgetItem(["✓", "http://archive.ubuntu.com/ubuntu", "noble", "main restricted"])
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
    
    def on_update_check_changed(self, enabled):
        """Handle update check enabled change"""
        self.app_settings.set_update_check_enabled(enabled)
        self.logger.info(f"Update checks {'enabled' if enabled else 'disabled'}")
        if hasattr(self, 'updateIntervalWidget'):
            self.updateIntervalWidget.setEnabled(enabled)
    
    def on_interval_changed(self, index):
        """Handle update interval change"""
        interval_map = {0: 60, 1: 120, 2: 240, 3: 360, 4: 720, 5: 1440}
        minutes = interval_map.get(index, 240)
        self.app_settings.set_update_check_interval(minutes)
        self.logger.info(f"Update interval set to {minutes} minutes")
    
    def setup_daemon_controls_old(self):
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
    

