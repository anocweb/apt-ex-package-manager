from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QTextEdit, QPushButton, QWidget, QHBoxLayout, QApplication
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import Qt
from typing import List
import logging

class LogView(QMainWindow):
    """Independent log view window with colored log levels"""
    
    def __init__(self, logging_service):
        super().__init__()
        self.logging_service = logging_service
        self.setWindowTitle("Application Logs")
        self.resize(700, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(self.log_text.font())
        layout.addWidget(self.log_text)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Copy logs button
        copy_button = QPushButton("Copy Logs")
        copy_button.clicked.connect(self.copy_logs)
        button_layout.addWidget(copy_button)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Connect to logging service signal for real-time updates
        self.logging_service.log_updated.connect(self.populate_logs)
        
        # Populate logs
        self.populate_logs()
    

    
    def populate_logs(self):
        """Populate log view with colored entries"""
        self.log_text.clear()
        
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
            messages = self.logging_service._log_messages
        else:
            # Fallback to basic messages
            messages = []
        
        # Reverse messages to show newest first
        for message in reversed(messages):
            # Extract log level from message
            level = 'INFO'  # Default
            for lvl in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']:
                if lvl in message:
                    level = lvl
                    break
            
            # Set text color based on level
            format = QTextCharFormat()
            format.setForeground(colors.get(level, colors['INFO']))
            
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(message + "\n", format)
        
        # Scroll to top to show newest entries
        self.log_text.moveCursor(QTextCursor.MoveOperation.Start)
    
    def copy_logs(self):
        """Copy all log messages to clipboard"""
        if hasattr(self.logging_service, '_log_messages'):
            log_text = "\n".join(reversed(self.logging_service._log_messages))
            clipboard = QApplication.clipboard()
            clipboard.setText(log_text)
    
    def closeEvent(self, event):
        """Disconnect from logging service when window is closed"""
        self.logging_service.log_updated.disconnect(self.populate_logs)
        event.accept()