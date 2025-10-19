"""Worker thread for loading installed packages"""
from PyQt6.QtCore import QThread, pyqtSignal


class InstalledPackagesWorker(QThread):
    """Worker thread for loading installed packages"""
    
    initial_batch_signal = pyqtSignal(list)
    remaining_batch_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, apt_controller, lmdb_manager):
        super().__init__()
        self.apt_controller = apt_controller
        self.lmdb_manager = lmdb_manager
    
    def run(self):
        try:
            # Load first 20 packages
            initial_packages = self.apt_controller.get_installed_packages_list(
                self.lmdb_manager, limit=20, offset=0
            )
            self.initial_batch_signal.emit(initial_packages)
            
            # Load remaining packages in batches
            offset = 20
            batch_size = 50
            while True:
                batch = self.apt_controller.get_installed_packages_list(
                    self.lmdb_manager, limit=batch_size, offset=offset
                )
                if not batch:
                    break
                self.remaining_batch_signal.emit(batch)
                offset += batch_size
        except Exception as e:
            self.error_signal.emit(str(e))
