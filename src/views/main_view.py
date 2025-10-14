from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6 import uic

class MainView(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        uic.loadUi('src/ui/main_window.ui', self)
        self.setup_ui()

    def setup_ui(self):
        # Connect UI elements to controller methods
        self.install_button.clicked.connect(self.install_package)
        self.remove_button.clicked.connect(self.remove_package)
        self.update_button.clicked.connect(self.update_package_list)

    def install_package(self):
        package_name = self.package_name_input.text()
        self.controller.install_package(package_name)
        self.update_ui()

    def remove_package(self):
        package_name = self.package_name_input.text()
        self.controller.remove_package(package_name)
        self.update_ui()

    def update_package_list(self):
        self.controller.update_package_list()
        self.update_ui()

    def update_ui(self):
        # Update the UI with the latest package information
        packages = self.controller.get_packages()
        self.package_list_widget.clear()
        for package in packages:
            self.package_list_widget.addItem(f"{package.name} - {package.version}: {package.description}")