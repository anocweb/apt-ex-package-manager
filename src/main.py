import sys
import argparse
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from views.main_view import MainView
from controllers.package_manager import PackageManager
from cache.database import DatabaseManager

def main():
    parser = argparse.ArgumentParser(description='Apt-Ex Package Manager')
    parser.add_argument('--dev-outline', action='store_true', help='Enable development widget outlines')
    parser.add_argument('--dev-logging', action='store_true', help='Automatically open logging window')
    parser.add_argument('--stdout-log-level', default='WARNING', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Maximum log level to show on stdout (default: WARNING)')
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
    
    try:
        icon_path = get_icon_path()
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            icon.addFile(icon_path, QSize(16, 16))
            icon.addFile(icon_path, QSize(32, 32))
            icon.addFile(icon_path, QSize(48, 48))
            icon.addFile(icon_path, QSize(64, 64))
            app.setWindowIcon(icon)
    except Exception:
        pass
    
    if args.dev_outline:
        app.setStyleSheet("* { border: 1px solid red; }")
    
    # Initialize logging service first
    from services.logging_service import LoggingService
    logging_service = LoggingService(stdout_log_level=args.stdout_log_level)
    
    # Initialize database manager with connection pooling at startup
    db_manager = DatabaseManager(logging_service=logging_service)
    
    package_manager = PackageManager(db_manager.connection_manager, logging_service)
    main_view = MainView(package_manager, db_manager.connection_manager, logging_service=logging_service, dev_logging=args.dev_logging, stdout_log_level=args.stdout_log_level)
    
    # Auto-open log window if --dev-logging is specified
    if args.dev_logging:
        from views.log_view import LogView
        main_view.log_window = LogView(main_view.logging_service)
        # Position and show log window first
        main_pos = main_view.pos()
        main_view.log_window.move(main_pos.x() + 50, main_pos.y() + 50)
        main_view.log_window.show()
    
    # Show main window last so it appears in front
    main_view.show()
    
    try:
        sys.exit(app.exec())
    finally:
        # Clean up database connections on exit
        db_manager.close()

if __name__ == "__main__":
    main() 