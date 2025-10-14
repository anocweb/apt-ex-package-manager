import sys
from PyQt6.QtWidgets import QApplication
from views.main_view import MainView

def main():
    app = QApplication(sys.argv)
    main_view = MainView()
    main_view.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()