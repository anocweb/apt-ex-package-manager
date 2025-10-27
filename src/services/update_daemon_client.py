"""
D-Bus client for communicating with update daemon
"""

from PyQt6.QtCore import QObject, pyqtSignal

try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False


class UpdateDaemonClient(QObject):
    """Client for communicating with update daemon via D-Bus"""
    
    updates_available = pyqtSignal(int)
    check_completed = pyqtSignal()
    
    def __init__(self, logging_service=None):
        super().__init__()
        self.logger = logging_service.get_logger('daemon_client') if logging_service else None
        self.daemon = None
        self.bus = None
        
        if DBUS_AVAILABLE:
            self._connect()
    
    def _connect(self):
        """Connect to daemon D-Bus service"""
        try:
            DBusGMainLoop(set_as_default=True)
            self.bus = dbus.SessionBus()
            
            # Get daemon object
            self.daemon = self.bus.get_object(
                'org.aptex.UpdateChecker',
                '/org/aptex/UpdateChecker'
            )
            
            # Connect to signals
            self.bus.add_signal_receiver(
                self._on_updates_available,
                signal_name='UpdatesAvailable',
                dbus_interface='org.aptex.UpdateChecker'
            )
            
            self.bus.add_signal_receiver(
                self._on_check_completed,
                signal_name='CheckCompleted',
                dbus_interface='org.aptex.UpdateChecker'
            )
            
            if self.logger:
                self.logger.info("Connected to update daemon")
        except dbus.DBusException as e:
            if self.logger:
                self.logger.warning(f"Failed to connect to daemon: {e}")
            self.daemon = None
    
    def _on_updates_available(self, count):
        """Handle UpdatesAvailable signal"""
        self.updates_available.emit(count)
    
    def _on_check_completed(self):
        """Handle CheckCompleted signal"""
        self.check_completed.emit()
    
    def is_available(self) -> bool:
        """Check if daemon is available"""
        return DBUS_AVAILABLE and self.daemon is not None
    
    def check_now(self) -> bool:
        """Trigger immediate update check"""
        if not self.is_available():
            return False
        
        try:
            self.daemon.CheckNow(dbus_interface='org.aptex.UpdateChecker')
            if self.logger:
                self.logger.debug("Triggered update check")
            return True
        except dbus.DBusException as e:
            if self.logger:
                self.logger.error(f"Failed to trigger check: {e}")
            return False
    
    def get_update_count(self) -> int:
        """Get current update count"""
        if not self.is_available():
            return 0
        
        try:
            count = self.daemon.GetUpdateCount(dbus_interface='org.aptex.UpdateChecker')
            return int(count)
        except dbus.DBusException as e:
            if self.logger:
                self.logger.error(f"Failed to get update count: {e}")
            return 0
    
    def get_last_check_time(self) -> str:
        """Get last check timestamp"""
        if not self.is_available():
            return ""
        
        try:
            timestamp = self.daemon.GetLastCheckTime(dbus_interface='org.aptex.UpdateChecker')
            return str(timestamp)
        except dbus.DBusException as e:
            if self.logger:
                self.logger.error(f"Failed to get last check time: {e}")
            return ""
    
    def set_check_interval(self, minutes: int) -> bool:
        """Set check interval"""
        if not self.is_available():
            return False
        
        try:
            self.daemon.SetCheckInterval(minutes, dbus_interface='org.aptex.UpdateChecker')
            if self.logger:
                self.logger.debug(f"Set check interval to {minutes} minutes")
            return True
        except dbus.DBusException as e:
            if self.logger:
                self.logger.error(f"Failed to set check interval: {e}")
            return False
