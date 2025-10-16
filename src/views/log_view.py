from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QScrollArea, QPushButton, QWidget, QHBoxLayout, QApplication, QComboBox, QLabel, QMenu, QLineEdit
from PyQt6.QtGui import QColor, QAction, QIcon
from PyQt6.QtCore import Qt, QTimer
import difflib
from typing import List
import logging
from settings.app_settings import AppSettings

from widgets.expandable_item import ExpandableItem

class LogView(QMainWindow):
    """Independent log view window with colored log levels"""
    
    def __init__(self, logging_service):
        super().__init__()
        self.logging_service = logging_service
        self.visible_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}  # All levels visible by default
        self.visible_loggers = set()  # Will be populated dynamically
        self.search_text = ""  # Search filter
        self.search_timer = QTimer()  # Delay timer for search
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self._populating_logs = False  # Recursion guard
        self.setWindowTitle("Application Logs")
        #self.resize(700, 500)
        self.setMinimumSize(700, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Combined filter and search controls on same line
        controls_layout = QHBoxLayout()
        
        # Left side - Filter controls
        controls_layout.addWidget(QLabel("Show levels:"))
        
        self.level_button = QPushButton("All Levels")
        self.level_menu = QMenu()
        self.level_actions = {}
        
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            action = QAction(level, self)
            action.setCheckable(True)
            action.setChecked(True)  # All checked by default
            action.triggered.connect(self.update_level_filter)
            self.level_actions[level] = action
            self.level_menu.addAction(action)
        
        self.level_button.setMenu(self.level_menu)
        controls_layout.addWidget(self.level_button)
        
        # Logger name filter dropdown
        controls_layout.addWidget(QLabel("Show loggers:"))
        self.logger_button = QPushButton("All Loggers")
        self.logger_menu = QMenu()
        self.logger_actions = {}
        self.logger_button.setMenu(self.logger_menu)
        controls_layout.addWidget(self.logger_button)
        
        # Stretch to push search to the right
        controls_layout.addStretch()
        
        # Right side - Search bar with embedded toggle action
        controls_layout.addWidget(QLabel("Search:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("type to filter...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.setMinimumWidth(200)
        
        # Embedded toggle action for exact/fuzzy matching
        self.match_toggle_action = QAction(self)
        self.match_toggle_action.setCheckable(True)
        self.match_toggle_action.triggered.connect(self.toggle_match_mode)
        
        # Load saved state
        settings = AppSettings()
        exact_match = settings.get("log_view/exact_match", False)
        self.match_toggle_action.setChecked(bool(exact_match))
        self.update_match_icon()
        
        self.search_input.addAction(self.match_toggle_action, QLineEdit.ActionPosition.TrailingPosition)
        
        controls_layout.addWidget(self.search_input)
        
        layout.addLayout(controls_layout)
        
        # Log scroll area with expandable items
        self.log_scroll = QScrollArea()
        self.log_container = QWidget()
        self.log_layout = QVBoxLayout(self.log_container)
        self.log_layout.setContentsMargins(0, 0, 0, 0)
        self.log_layout.setSpacing(1)
        
        self.log_scroll.setWidget(self.log_container)
        self.log_scroll.setWidgetResizable(True)
        layout.addWidget(self.log_scroll)
        
        # Store expandable items for selection
        self.expandable_items = []
        self.selected_items = []
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push buttons to the right
        
        # Copy logs button
        copy_button = QPushButton("Copy Output")
        copy_button.clicked.connect(self.copy_logs)
        copy_button.setMinimumWidth(copy_button.sizeHint().width() + 20)  # Add padding
        button_layout.addWidget(copy_button)
        
        # Save to file button
        save_button = QPushButton("Save Output")
        save_button.clicked.connect(self.save_to_file)
        save_button.setMinimumWidth(save_button.sizeHint().width() + 20)  # Add padding
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        
        # Connect to logging service signal for real-time updates
        self.logging_service.log_updated.connect(self.populate_logs)
        

        
        # Populate logs
        self.populate_logs()
        

        

    

    
    def populate_logs(self):
        """Populate log view with colored entries"""
        # Recursion guard - prevent infinite loop
        if self._populating_logs:
            return
        
        self._populating_logs = True
        try:
            # Clear existing items
            for item in self.expandable_items:
                item.setParent(None)
            self.expandable_items.clear()
            
            # Theme-aware color mapping for log levels
            palette = self.palette()
            is_dark = palette.color(palette.ColorRole.Window).lightness() < 128
            
            if is_dark:
                # Dark theme colors
                colors = {
                    'DEBUG': QColor(150, 150, 150),    # Light Gray
                    'INFO': QColor(220, 220, 220),     # Light Gray
                    'WARNING': QColor(255, 165, 0),    # Orange
                    'ERROR': QColor(255, 100, 100),    # Light Red
                    'CRITICAL': QColor(255, 50, 50)    # Bright Red
                }
            else:
                # Light theme colors
                colors = {
                    'DEBUG': QColor(100, 100, 100),    # Dark Gray
                    'INFO': QColor(0, 0, 0),           # Black
                    'WARNING': QColor(200, 100, 0),    # Dark Orange
                    'ERROR': QColor(200, 0, 0),        # Dark Red
                    'CRITICAL': QColor(139, 0, 0)      # Very Dark Red
                }
            
            # Get messages from logging service callback
            if hasattr(self.logging_service, '_log_messages'):
                log_entries = self.logging_service._log_messages
            else:
                # Fallback to basic messages
                log_entries = []
            
            # Extract messages for logger menu
            messages = []
            for entry in log_entries:
                if isinstance(entry, dict):
                    messages.append(entry['message'])
                else:
                    messages.append(entry)  # Backward compatibility
            
            # Update logger filter menu
            self.update_logger_menu(messages)
            
            # Reverse entries to show newest first
            for entry in reversed(log_entries):
                # Handle both old string format and new dict format
                if isinstance(entry, dict):
                    message = entry['message']
                    data = entry.get('data')
                else:
                    message = entry
                    data = None
                
                # Extract log level from message
                level = 'INFO'  # Default
                for lvl in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']:
                    if lvl in message:
                        level = lvl
                        break
                
                # Extract logger name from message
                logger_name = 'root'
                parts = message.split(' - ')
                if len(parts) >= 3:
                    logger_name = parts[1]
                
                # Skip message if level or logger is not visible
                if level not in self.visible_levels or (self.visible_loggers and logger_name not in self.visible_loggers):
                    continue
                
                # Skip message if it doesn't match search filter
                if self.search_text and not self.fuzzy_match(message, self.search_text):
                    continue
                
                # Create expandable item
                item = ExpandableItem(message, data, colors.get(level, colors['INFO']), self.logging_service)
                item.selection_changed.connect(self.on_item_selected)
                self.log_layout.addWidget(item)
                self.expandable_items.append(item)
            
            # Add stretch to push items to top
            self.log_layout.addStretch()
            

            
        finally:
            self._populating_logs = False
    
    def on_item_selected(self, selected_item):
        """Handle item selection with multi-select support"""
        # Check if Ctrl was held (multi-select mode)
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Multi-select: toggle selection
            if selected_item in self.selected_items:
                selected_item.set_selected(False)
                self.selected_items.remove(selected_item)
            else:
                selected_item.set_selected(True)
                self.selected_items.append(selected_item)
        else:
            # Single-select: clear others and select this one
            for item in self.selected_items:
                item.set_selected(False)
            self.selected_items.clear()
            selected_item.set_selected(True)
            self.selected_items.append(selected_item)
    
    def copy_logs(self):
        """Copy all visible log messages to clipboard"""
        visible_logs = self.get_visible_logs()
        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(visible_logs))
    

    
    def get_visible_logs(self):
        """Get currently visible log messages based on filters"""
        visible_logs = []
        for item in self.expandable_items:
            visible_logs.append(item.message)
        
        return visible_logs
    
    def save_to_file(self):
        """Save visible logs to file using save dialog"""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime
        import os
        
        # Generate default filename
        app_name = "apt-ex-manager"
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filtered_suffix = "_filtered" if self.search_text or len(self.visible_levels) < 5 or len(self.visible_loggers) < len(self.logging_service.registered_loggers) else ""
        default_filename = f"{app_name}_{timestamp}{filtered_suffix}.log"
        
        # Show save dialog
        home_dir = os.path.expanduser("~")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log File",
            os.path.join(home_dir, default_filename),
            "Log files (*.log);;Text files (*.txt);;All files (*)"
        )
        
        if file_path:
            try:
                visible_logs = self.get_visible_logs()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(visible_logs))
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Save Error", f"Failed to save file: {e}")
    
    def update_level_filter(self):
        """Update visible log levels based on menu action states"""
        self.visible_levels = set()
        checked_levels = []
        for level, action in self.level_actions.items():
            if action.isChecked():
                self.visible_levels.add(level)
                checked_levels.append(level)
        
        # Update button text
        if len(checked_levels) == 5:
            self.level_button.setText("All Levels")
        elif len(checked_levels) == 0:
            self.level_button.setText("No Levels")
        else:
            self.level_button.setText(f"{len(checked_levels)} Levels")
        
        self.populate_logs()  # Refresh display
    
    def update_logger_menu(self, messages):
        """Update logger menu with active loggers at top, inactive at bottom with separator"""
        # Extract unique logger names from messages (active loggers)
        active_loggers = set()
        for message in messages:
            parts = message.split(' - ')
            if len(parts) >= 3:
                active_loggers.add(parts[1])
        
        # Get all registered loggers from logging service
        all_loggers = self.logging_service.registered_loggers.copy()
        inactive_loggers = all_loggers - active_loggers
        
        # Store current check states before clearing
        current_states = {}
        for logger_name, action in self.logger_actions.items():
            current_states[logger_name] = action.isChecked()
        
        # Clear and rebuild menu
        self.logger_menu.clear()
        self.logger_actions.clear()
        
        # Add active loggers first
        for logger_name in sorted(active_loggers):
            action = QAction(logger_name, self)
            action.setCheckable(True)
            # Preserve previous state or default to True for new loggers
            action.setChecked(current_states.get(logger_name, True))
            action.triggered.connect(self.update_logger_filter)
            self.logger_actions[logger_name] = action
            self.logger_menu.addAction(action)
        
        # Add separator if there are both active and inactive loggers
        if active_loggers and inactive_loggers:
            self.logger_menu.addSeparator()
        
        # Add inactive loggers at bottom
        for logger_name in sorted(inactive_loggers):
            action = QAction(f"{logger_name} (no logs)", self)
            action.setCheckable(True)
            # Preserve previous state or default to True for new loggers
            action.setChecked(current_states.get(logger_name, True))
            action.triggered.connect(self.update_logger_filter)
            self.logger_actions[logger_name] = action
            self.logger_menu.addAction(action)
        
        # Update visible loggers set if empty (first time)
        if not self.visible_loggers:
            self.visible_loggers = all_loggers.copy()
    
    def update_logger_filter(self):
        """Update visible loggers based on menu action states"""
        self.visible_loggers = set()
        checked_loggers = []
        for logger_name, action in self.logger_actions.items():
            if action.isChecked():
                self.visible_loggers.add(logger_name)
                checked_loggers.append(logger_name)
        
        # Update button text
        if len(checked_loggers) == len(self.logger_actions):
            self.logger_button.setText("All Loggers")
        elif len(checked_loggers) == 0:
            self.logger_button.setText("No Loggers")
        else:
            self.logger_button.setText(f"{len(checked_loggers)} Loggers")
        
        self.populate_logs()  # Refresh display
    
    def on_search_text_changed(self):
        """Handle search text change with delay"""
        self.search_timer.stop()  # Stop any existing timer
        self.search_timer.start(200)  # Start 200ms delay
    
    def perform_search(self):
        """Perform the actual search after delay"""
        search_text = self.search_input.text().strip()
        
        # Require at least 2 characters or empty string (to clear search)
        if len(search_text) >= 2 or len(search_text) == 0:
            self.search_text = search_text
            self.populate_logs()  # Refresh display
    
    def fuzzy_match(self, text: str, search: str) -> bool:
        """Perform fuzzy or exact matching on text with word boundary support"""
        if not search:
            return True
        
        # Get threshold from settings
        settings = AppSettings()
        if not settings.settings.contains("log_view/fuzzy_threshold"):
            settings.set("log_view/fuzzy_threshold", 0.5)
        threshold = float(settings.get("log_view/fuzzy_threshold", 0.5))
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        search_lower = search.lower()
        
        # Check if exact match is enabled
        if self.match_toggle_action.isChecked():
            return search_lower in text_lower
        
        # Exact substring match (highest priority)
        if search_lower in text_lower:
            return True
        
        # Word boundary matching - check if search matches word beginnings
        import re
        words = re.findall(r'\b\w+', text_lower)
        for word in words:
            # Check if word starts with search term
            if word.startswith(search_lower):
                return True
            
            # Fuzzy match against individual words
            similarity = difflib.SequenceMatcher(None, search_lower, word).ratio()
            if similarity >= threshold:
                return True
        
        # Check similarity with entire text as fallback
        similarity = difflib.SequenceMatcher(None, search_lower, text_lower).ratio()
        return similarity >= threshold
    
    def update_match_icon(self):
        """Update icon and tooltip based on current mode"""
        if self.match_toggle_action.isChecked():
            # Exact match mode
            self.match_toggle_action.setIcon(QIcon.fromTheme("edit-find"))
            self.match_toggle_action.setToolTip("Exact matching (click for fuzzy)")
        else:
            # Fuzzy match mode
            self.match_toggle_action.setIcon(QIcon.fromTheme("view-filter"))
            self.match_toggle_action.setToolTip("Fuzzy matching (click for exact)")
    
    def toggle_match_mode(self):
        """Toggle between exact and fuzzy matching modes"""
        self.update_match_icon()
        
        # Save state to settings
        settings = AppSettings()
        settings.set("log_view/exact_match", self.match_toggle_action.isChecked())
        
        self.on_search_text_changed()  # Refresh search
    

    

    

    

    
    def closeEvent(self, event):
        """Disconnect from logging service when window is closed"""
        self.logging_service.log_updated.disconnect(self.populate_logs)
        event.accept()