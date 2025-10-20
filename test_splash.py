#!/usr/bin/env python3
"""Test splash screen display"""

import sys
import time
from PyQt6.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, 'src')

from views.splash_screen import SplashScreen

def main():
    app = QApplication(sys.argv)
    
    # Create and show splash
    splash = SplashScreen()
    splash.show()
    
    # Simulate startup sequence
    stages = [
        (5, "Starting up...", ""),
        (10, "Initializing services...", ""),
        (15, "Loading package database...", ""),
        (30, "Caching packages...", "Cached 1,000 / 5,000 packages"),
        (50, "Caching packages...", "Cached 2,500 / 5,000 packages"),
        (70, "Caching packages...", "Cached 3,500 / 5,000 packages"),
        (85, "Caching packages...", "Cached 5,000 / 5,000 packages"),
        (90, "Updating installed status...", ""),
        (98, "Loading user interface...", ""),
        (100, "Ready", "Loaded 5,000 packages"),
    ]
    
    for progress, status, detail in stages:
        splash.update_progress(progress, status, detail)
        time.sleep(0.5)  # Simulate work
    
    print("✓ Splash screen test complete!")
    splash.close()

if __name__ == '__main__':
    main()
