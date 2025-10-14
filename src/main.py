import sys
from PyQt6.QtWidgets import QApplication
from views.main_view import MainView
from controllers.package_manager import PackageManager

def main():
    app = QApplication(sys.argv)
    package_manager = PackageManager()
    main_view = MainView(package_manager)
    main_view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 