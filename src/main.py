import sys
from PyQt6.QtWidgets import QApplication
from config.app_config import AppConfig
from controllers.application_controller import ApplicationController

def main():
    config = AppConfig.parse_arguments()
    app = QApplication(sys.argv)
    
    if config.dev_outline:
        app.setStyleSheet("* { border: 1px solid red; }")
    
    app_controller = ApplicationController(app, config)
    app_controller.initialize()
    app_controller.show_main_window()
    
    try:
        sys.exit(app.exec())
    finally:
        app_controller.cleanup()

if __name__ == "__main__":
    main() 