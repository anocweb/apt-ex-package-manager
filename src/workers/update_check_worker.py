"""Worker thread for checking package updates"""
from PyQt6.QtCore import QThread, pyqtSignal


class UpdateCheckWorker(QThread):
    """Worker thread for checking available updates"""
    
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, apt_controller):
        super().__init__()
        self.apt_controller = apt_controller
    
    def run(self):
        try:
            updates = self.apt_controller.get_upgradable_packages()
            self.finished_signal.emit(updates)
        except Exception as e:
            self.error_signal.emit(str(e))
