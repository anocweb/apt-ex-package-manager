"""Worker thread for package install/remove operations"""
from PyQt6.QtCore import QThread, pyqtSignal


class PackageOperationWorker(QThread):
    """Worker thread for package operations"""
    
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)
    
    def __init__(self, backend, operation, package_name):
        super().__init__()
        self.backend = backend
        self.operation = operation
        self.package_name = package_name
    
    def run(self):
        try:
            if self.operation == 'install':
                result = self.backend.install_package(self.package_name)
            elif self.operation == 'remove':
                result = self.backend.remove_package(self.package_name)
            elif self.operation == 'update':
                result = self.backend.update_package(self.package_name)
            elif self.operation == 'update_all':
                result = self.backend.update_all_packages()
            else:
                result = False
            
            self.finished.emit(result, self.package_name)
        except Exception as e:
            self.error.emit(str(e))
