from .apt_controller import APTController
from models.package_model import Package
from cache import LMDBManager

class PackageManager:
    def __init__(self, lmdb_manager: LMDBManager, logging_service=None):
        self.lmdb_manager = lmdb_manager
        self.logging_service = logging_service
        self.apt_controller = APTController(lmdb_manager, logging_service)
    
    def search_packages(self, query):
        return self.apt_controller.search_packages(query)
    
    def install_package(self, package_name):
        return self.apt_controller.install_package(package_name)
    
    def remove_package(self, package_name):
        return self.apt_controller.remove_package(package_name)
    
    def get_installed_packages(self):
        return self.apt_controller.get_installed_packages()