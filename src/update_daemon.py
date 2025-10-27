#!/usr/bin/env python3
"""
Update Daemon - Background service for checking package updates
Runs independently of GUI and shows tray icon when updates available
"""

import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QObject, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon

try:
    import dbus
    import dbus.service
    import dbus.mainloop.glib
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False
    print("Warning: dbus-python not available. D-Bus interface disabled.")

from controllers.package_manager import PackageManager
from cache import LMDBManager
from services.logging_service import LoggingService
from settings.app_settings import AppSettings


class UpdateCheckWorker(QThread):
    """Worker thread for checking updates"""
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, package_manager):
        super().__init__()
        self.package_manager = package_manager
    
    def run(self):
        """Check for updates in background"""
        try:
            updates = self.package_manager.get_upgradable_packages()
            count = len(updates) if updates else 0
            self.finished.emit(count)
        except Exception as e:
            self.error.emit(str(e))


class UpdateCheckerDBus(dbus.service.Object if DBUS_AVAILABLE else object):
    """D-Bus service interface for update checker"""
    
    def __init__(self, daemon):
        if not DBUS_AVAILABLE:
            return
        
        bus_name = dbus.service.BusName(
            'org.aptex.UpdateChecker',
            bus=dbus.SessionBus()
        )
        super().__init__(bus_name, '/org/aptex/UpdateChecker')
        self.daemon = daemon
    
    @dbus.service.method('org.aptex.UpdateChecker')
    def CheckNow(self):
        """Trigger immediate update check"""
        self.daemon.check_for_updates()
    
    @dbus.service.method('org.aptex.UpdateChecker', out_signature='i')
    def GetUpdateCount(self):
        """Return current update count"""
        return self.daemon.update_count
    
    @dbus.service.method('org.aptex.UpdateChecker', out_signature='s')
    def GetLastCheckTime(self):
        """Return last check timestamp"""
        return self.daemon.last_check_time
    
    @dbus.service.method('org.aptex.UpdateChecker', in_signature='i')
    def SetCheckInterval(self, minutes):
        """Change check interval"""
        self.daemon.set_check_interval(minutes)
    
    @dbus.service.signal('org.aptex.UpdateChecker', signature='i')
    def UpdatesAvailable(self, count):
        """Signal emitted when updates found"""
        pass
    
    @dbus.service.signal('org.aptex.UpdateChecker')
    def CheckCompleted(self):
        """Signal emitted when check completes"""
        pass


class UpdateDaemon(QObject):
    """Main daemon class"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize Qt application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("Apt-Ex Update Checker")
        
        # State
        self.update_count = 0
        self.last_check_time = ""
        self.worker = None
        
        # Setup components
        self.setup_logging()
        self.setup_settings()
        self.setup_package_manager()
        self.setup_tray_icon()
        self.setup_update_timer()
        
        # Setup D-Bus if available
        if DBUS_AVAILABLE:
            self.setup_dbus()
        
        self.logger.info("Update daemon started")
        
        # Perform initial check
        QTimer.singleShot(5000, self.check_for_updates)
    
    def setup_logging(self):
        """Setup logging service"""
        log_dir = Path.home() / '.local' / 'share' / 'apt-ex-package-manager'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logging_service = LoggingService(
            app_name='apt-ex-daemon',
            stdout_log_level='INFO'
        )
        self.logging_service.enable_file_logging(str(log_dir))
        self.logger = self.logging_service.get_logger('daemon')
    
    def setup_settings(self):
        """Load settings"""
        self.settings = AppSettings()
    
    def setup_package_manager(self):
        """Initialize package manager"""
        try:
            lmdb_manager = LMDBManager()
            self.package_manager = PackageManager(lmdb_manager, self.logging_service)
            self.logger.info("Package manager initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize package manager: {e}")
            self.package_manager = None
    
    def setup_tray_icon(self):
        """Create system tray icon (initially hidden)"""
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon.fromTheme('system-software-update-available'))
        self.tray_icon.activated.connect(self.on_tray_clicked)
        
        # Create context menu
        menu = QMenu()
        
        self.status_action = menu.addAction('Checking for updates...')
        self.status_action.setEnabled(False)
        
        menu.addSeparator()
        
        open_action = menu.addAction('Open Updates')
        open_action.triggered.connect(self.launch_gui)
        
        check_action = menu.addAction('Check for Updates Now')
        check_action.triggered.connect(self.check_for_updates)
        
        menu.addSeparator()
        
        quit_action = menu.addAction('Quit Update Checker')
        quit_action.triggered.connect(self.quit_daemon)
        
        self.tray_icon.setContextMenu(menu)
        
        # Don't show yet - only when updates found
        self.logger.debug("Tray icon created (hidden)")
    
    def setup_update_timer(self):
        """Setup periodic update check timer"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.check_for_updates)
        
        # Get interval from settings (default 4 hours)
        interval_minutes = self.settings.get_update_check_interval()
        
        if interval_minutes > 0:
            self.update_timer.start(interval_minutes * 60 * 1000)
            self.logger.info(f"Update timer started (interval: {interval_minutes} minutes)")
        else:
            self.logger.info("Automatic update checks disabled (interval: Never)")
    
    def setup_dbus(self):
        """Setup D-Bus service"""
        try:
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            self.dbus_service = UpdateCheckerDBus(self)
            self.logger.info("D-Bus service registered")
        except Exception as e:
            self.logger.error(f"Failed to setup D-Bus: {e}")
    
    def check_for_updates(self):
        """Check for updates in background"""
        if not self.package_manager:
            self.logger.warning("Package manager not available")
            return
        
        if self.worker and self.worker.isRunning():
            self.logger.debug("Update check already in progress")
            return
        
        self.logger.info("Starting update check")
        self.status_action.setText('Checking for updates...')
        
        self.worker = UpdateCheckWorker(self.package_manager)
        self.worker.finished.connect(self.on_check_complete)
        self.worker.error.connect(self.on_check_error)
        self.worker.start()
    
    def on_check_complete(self, count):
        """Handle update check completion"""
        self.update_count = count
        self.last_check_time = datetime.now().isoformat()
        
        self.logger.info(f"Update check complete: {count} updates available")
        
        # Update settings
        self.settings.set_last_update_check(self.last_check_time)
        
        # Update tray icon
        self.update_tray_icon(count)
        
        # Emit D-Bus signals
        if DBUS_AVAILABLE and hasattr(self, 'dbus_service'):
            self.dbus_service.UpdatesAvailable(count)
            self.dbus_service.CheckCompleted()
    
    def on_check_error(self, error):
        """Handle update check error"""
        self.logger.error(f"Update check failed: {error}")
        self.status_action.setText('Check failed')
    
    def update_tray_icon(self, count):
        """Show/hide tray icon based on update count"""
        if count > 0:
            self.tray_icon.setToolTip(f'{count} update{"s" if count != 1 else ""} available')
            self.status_action.setText(f'{count} update{"s" if count != 1 else ""} available')
            if not self.tray_icon.isVisible():
                self.tray_icon.show()
                self.logger.info(f"Tray icon shown ({count} updates)")
        else:
            self.status_action.setText('System is up to date')
            if self.tray_icon.isVisible():
                self.tray_icon.hide()
                self.logger.info("Tray icon hidden (no updates)")
    
    def on_tray_clicked(self, reason):
        """Handle tray icon click"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.launch_gui()
    
    def launch_gui(self):
        """Launch main GUI application"""
        try:
            script_path = Path(__file__).parent / 'main.py'
            subprocess.Popen([sys.executable, str(script_path), '--show-updates'])
            self.logger.info("Launched GUI")
        except Exception as e:
            self.logger.error(f"Failed to launch GUI: {e}")
    
    def set_check_interval(self, minutes):
        """Change check interval"""
        if minutes == 0:
            # Never - stop timer
            self.update_timer.stop()
            self.logger.info("Automatic update checks disabled")
        else:
            if minutes < 30:
                minutes = 30
            self.update_timer.setInterval(minutes * 60 * 1000)
            if not self.update_timer.isActive():
                self.update_timer.start()
            self.logger.info(f"Check interval changed to {minutes} minutes")
        
        self.settings.set_update_check_interval(minutes)
    
    def quit_daemon(self):
        """Stop daemon and exit"""
        self.logger.info("Daemon shutting down")
        self.tray_icon.hide()
        self.app.quit()
    
    def run(self):
        """Run the daemon"""
        return self.app.exec()


def main():
    """Main entry point"""
    daemon = UpdateDaemon()
    sys.exit(daemon.run())


if __name__ == '__main__':
    main()
