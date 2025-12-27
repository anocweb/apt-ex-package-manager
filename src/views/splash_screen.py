"""Splash screen for application startup"""
from PyQt6.QtWidgets import QSplashScreen, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from utils.path_resolver import PathResolver
import os


class SplashScreen(QSplashScreen):
    """Custom splash screen with progress bar and status updates"""
    
    def __init__(self):
        # Create a pixmap for the splash screen background
        pixmap = QPixmap(500, 300)
        pixmap.fill(QColor(45, 45, 45))  # Dark background
        
        super().__init__(pixmap, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
        
        # Disable click to dismiss
        self.setEnabled(False)
        
        # Force on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        # Setup UI elements
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup splash screen UI elements"""
        # Main widget and layout
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # App icon/logo
        self.icon_label = QLabel()
        icon_path = self._get_icon_path()
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, 
                                               Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText("📦")
            font = QFont()
            font.setPointSize(48)
            self.icon_label.setFont(font)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # App title
        self.title_label = QLabel("Apt-Ex Package Manager")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("color: white;")
        layout.addWidget(self.title_label)
        
        # Add stretch to push progress to bottom half
        layout.addStretch()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                background-color: #2a2a2a;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #3daee9;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #ccc; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Detail label
        self.detail_label = QLabel("")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setStyleSheet("color: #999; font-size: 11px;")
        layout.addWidget(self.detail_label)
        
        # Set widget geometry
        widget.setGeometry(0, 0, 500, 300)
        
    def _get_icon_path(self):
        """Get application icon path"""
        try:
            return PathResolver.get_icon_path('app-icon.svg')
        except FileNotFoundError:
            return None
    
    def update_progress(self, value: int, status: str = None, detail: str = None):
        """Update progress bar and status messages
        
        Args:
            value: Progress value (0-100)
            status: Main status message
            detail: Detail message (e.g., package count)
        """
        self.progress_bar.setValue(value)
        
        if status:
            self.status_label.setText(status)
        
        if detail:
            self.detail_label.setText(detail)
        
        # Force repaint
        self.repaint()
        
        # Process events to keep UI responsive
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
    
    def set_status(self, message: str):
        """Set status message"""
        self.status_label.setText(message)
        self.repaint()
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
