import sys
import argparse
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from views.main_view import MainView
from controllers.package_manager import PackageManager

def main():
    parser = argparse.ArgumentParser(description='Apt-Ex Package Manager')
    parser.add_argument('--dev-outline', action='store_true', help='Enable development widget outlines')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    
    # Set application icon based on theme
    def get_icon_path():
        base_path = os.path.join(os.path.dirname(__file__), 'icons')
        # Check if dark theme is active
        palette = app.palette()
        is_dark = palette.color(palette.ColorRole.Window).lightness() < 128
        
        if is_dark:
            dark_icon = os.path.join(base_path, 'app-icon-dark.svg')
            if os.path.exists(dark_icon):
                return dark_icon
        
        # Fallback to light icon
        return os.path.join(base_path, 'app-icon.svg')
    
    icon_path = get_icon_path()
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
        # Add multiple sizes to ensure proper scaling
        icon.addFile(icon_path, QSize(16, 16))
        icon.addFile(icon_path, QSize(32, 32))
        icon.addFile(icon_path, QSize(48, 48))
        icon.addFile(icon_path, QSize(64, 64))
        app.setWindowIcon(icon)
    
    if args.dev_outline:
        app.setStyleSheet("* { border: 1px solid red; }")
    
    package_manager = PackageManager()
    main_view = MainView(package_manager)
    main_view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 