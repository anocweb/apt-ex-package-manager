from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal

class PackageListItem(QFrame):
    """Reusable KDE Discover-style package list item widget"""
    
    install_requested = pyqtSignal(str)  # Emits package name when install is clicked
    
    def __init__(self, package, parent=None):
        super().__init__(parent)
        self.package = package
        self.setup_ui()
    
    def setup_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)  # Enable stylesheet backgrounds
        self.setFrameStyle(QFrame.Shape.Box)
        
        # Check if dev outline is active
        from PyQt6.QtWidgets import QApplication
        app_stylesheet = QApplication.instance().styleSheet()
        dev_outline = "border: 1px solid red" in app_stylesheet
        
        if dev_outline:
            self.setStyleSheet("""
                QFrame {
                    background-color: palette(base);
                    border: 1px solid red;
                    border-radius: 8px;
                    padding: 8px;
                }
                QFrame:hover {
                    background-color: palette(alternate-base);
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: palette(base);
                    border: 1px solid palette(mid);
                    border-radius: 8px;
                    padding: 8px;
                }
                QFrame:hover {
                    background-color: palette(alternate-base);
                }
            """)
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(12)
        
        # Icon placeholder
        icon_label = QLabel("📦")
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if dev_outline:
            icon_label.setStyleSheet("font-size: 24px; background-color: palette(button); border-radius: 8px; border: 1px solid red;")
        else:
            icon_label.setStyleSheet("font-size: 24px; background-color: palette(button); border-radius: 8px;")
        main_layout.addWidget(icon_label)
        
        # Content area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        # Package name
        name = getattr(self.package, 'name', '') or getattr(self.package, 'package_id', 'Unknown Package')
        name_label = QLabel(name)
        if dev_outline:
            name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: palette(window-text); background: transparent; border: 1px solid red; padding: 0px;")
        else:
            name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: palette(window-text); background: transparent; border: none; padding: 0px;")
        name_label.setMinimumHeight(20)
        name_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        content_layout.addWidget(name_label)
        
        # Package description
        description = getattr(self.package, 'description', '') or getattr(self.package, 'summary', '') or 'No description available'
        desc_label = QLabel(description)
        
        # Calculate font metrics for 2 lines
        font_metrics = desc_label.fontMetrics()
        line_height = font_metrics.height()
        two_line_height = line_height * 2
        
        # Elide text if it exceeds 2 lines
        available_width = 200  # Approximate available width
        elided_text = font_metrics.elidedText(description, Qt.TextElideMode.ElideRight, available_width * 2)
        desc_label.setText(elided_text)
        if dev_outline:
            desc_label.setStyleSheet("font-size: 12px; color: palette(window-text); background: transparent; border: 1px solid red; padding: 0px;")
        else:
            desc_label.setStyleSheet("font-size: 12px; color: palette(window-text); background: transparent; border: none; padding: 0px;")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        desc_label.setMaximumHeight(36)
        desc_label.setMinimumHeight(36)
        desc_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        content_layout.addWidget(desc_label)
        
        # Rating placeholder
        rating_label = QLabel('<span style="color: #FFD700;">★★★★</span><span style="color: #B8860B;">☆</span><span style="color: palette(window-text);"> 4.2 ratings</span>')
        if dev_outline:
            rating_label.setStyleSheet("font-size: 11px; background: transparent; border: 1px solid red; padding: 0px;")
        else:
            rating_label.setStyleSheet("font-size: 11px; background: transparent; border: none; padding: 0px;")
        rating_label.setMinimumHeight(18)
        rating_label.setTextFormat(Qt.TextFormat.RichText)
        rating_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        content_layout.addWidget(rating_label)
        
        main_layout.addLayout(content_layout)
        
        # Right side layout for backend label and install button
        right_layout = QVBoxLayout()
        
        # Backend label
        backend = getattr(self.package, 'backend', 'apt')
        backend_label = QLabel(backend.upper())
        if dev_outline:
            backend_label.setStyleSheet("font-size: 10px; color: palette(window-text); background: transparent; border: 1px solid red; padding: 2px;")
        else:
            backend_label.setStyleSheet("font-size: 10px; color: palette(window-text); background: transparent; border: none; padding: 2px;")
        backend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        backend_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        right_layout.addWidget(backend_label)
        
        # Add stretch to push install button to bottom
        right_layout.addStretch()
        
        # Install button
        install_btn = QPushButton("⬇ Install")
        install_btn.setFixedSize(80, 32)
        if dev_outline:
            install_btn.setStyleSheet("""
                QPushButton {
                    background-color: palette(highlight);
                    color: palette(highlighted-text);
                    border: 1px solid red;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: palette(dark);
                }
            """)
        else:
            install_btn.setStyleSheet("""
                QPushButton {
                    background-color: palette(highlight);
                    color: palette(highlighted-text);
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: palette(dark);
                }
            """)
        package_name = getattr(self.package, 'name', '') or getattr(self.package, 'package_id', '')
        install_btn.clicked.connect(lambda: self.install_requested.emit(package_name))
        right_layout.addWidget(install_btn)
        
        main_layout.addLayout(right_layout)