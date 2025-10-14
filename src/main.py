import sys
import argparse
from PyQt6.QtWidgets import QApplication
from views.main_view import MainView
from controllers.package_manager import PackageManager

def main():
    parser = argparse.ArgumentParser(description='Apt-Ex Package Manager')
    parser.add_argument('--dev-outline', action='store_true', help='Enable development widget outlines')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    
    if args.dev_outline:
        app.setStyleSheet("* { border: 1px solid red; }")
    
    package_manager = PackageManager()
    main_view = MainView(package_manager)
    main_view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 