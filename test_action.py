#!/usr/bin/env python3

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QLineEdit Action Test")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Test 1: Action with text only (likely invisible)
        self.line1 = QLineEdit()
        self.line1.setPlaceholderText("Action with text only")
        action1 = QAction("~", self)
        action1.triggered.connect(lambda: print("Text action clicked"))
        self.line1.addAction(action1, QLineEdit.ActionPosition.TrailingPosition)
        layout.addWidget(self.line1)
        
        # Test 2: Action with icon (should be visible)
        self.line2 = QLineEdit()
        self.line2.setPlaceholderText("Action with icon")
        action2 = QAction(self)
        action2.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogApplyButton))
        action2.triggered.connect(lambda: print("Icon action clicked"))
        self.line2.addAction(action2, QLineEdit.ActionPosition.TrailingPosition)
        layout.addWidget(self.line2)
        
        # Test 3: Action with both text and icon
        self.line3 = QLineEdit()
        self.line3.setPlaceholderText("Action with text and icon")
        action3 = QAction("~", self)
        action3.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView))
        action3.triggered.connect(lambda: print("Text+Icon action clicked"))
        self.line3.addAction(action3, QLineEdit.ActionPosition.TrailingPosition)
        layout.addWidget(self.line3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())