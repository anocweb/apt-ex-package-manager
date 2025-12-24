"""Worker thread for cache updates"""
from PyQt6.QtCore import QThread, pyqtSignal


class CacheUpdateWorker(QThread):
    """Worker thread for updating package cache"""
    
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(str)
    count_signal = pyqtSignal(int, int)
    
    def __init__(self, update_categories, update_packages, update_installed, logging_service, lmdb_manager):
        super().__init__()
        self.update_categories = update_categories
        self.update_packages = update_packages
        self.update_installed = update_installed
        self.logging_service = logging_service
        self.lmdb_manager = lmdb_manager
    
    def run(self):
        try:
            from controllers.apt_controller import APTController
            apt_controller = APTController(logging_service=self.logging_service)
            
            if self.update_categories:
                self.logging_service.info("Starting category update")
                categories = apt_controller.get_section_details()
                self.lmdb_manager.set_categories('apt', categories)
                self.logging_service.info("Category cache updated")
            
            if self.update_packages:
                self.logging_service.info("Starting package update")
                self.progress_signal.emit("Loading package details")
                packages = apt_controller.get_all_packages_for_cache()
                
                total = len(packages)
                self.logging_service.info(f"Loaded {total} packages")
                self.progress_signal.emit(f"Caching {total} packages")
                
                batch_size = 100
                from cache import PackageCacheModel, PackageData
                
                for batch_start in range(0, total, batch_size):
                    batch_end = min(batch_start + batch_size, total)
                    batch = packages[batch_start:batch_end]
                    
                    pkg_cache = PackageCacheModel(self.lmdb_manager, 'apt')
                    
                    for pkg_data in batch:
                        package = PackageData(
                            package_id=pkg_data['package_id'],
                            name=pkg_data['name'],
                            version=pkg_data.get('version'),
                            description=pkg_data.get('description', ''),
                            summary=pkg_data.get('summary'),
                            section=pkg_data.get('section'),
                            architecture=pkg_data.get('architecture'),
                            size=pkg_data.get('size'),
                            installed_size=pkg_data.get('installed_size'),
                            maintainer=pkg_data.get('maintainer'),
                            homepage=pkg_data.get('homepage'),
                            metadata=pkg_data.get('metadata', {})
                        )
                        pkg_cache.add_package(package)
                    
                    self.count_signal.emit(batch_end, total)
            
            if self.update_installed or self.update_packages:
                self.logging_service.info("Updating installed package status")
                self.progress_signal.emit("Updating installed status")
                apt_controller.update_installed_status(self.lmdb_manager.lmdb_manager)
                self.logging_service.info("Installed status updated")
                
                # Rebuild indexes to update installed index
                self.logging_service.info("Rebuilding indexes")
                self.progress_signal.emit("Rebuilding indexes")
                from cache import PackageCacheModel
                pkg_cache = PackageCacheModel(self.lmdb_manager, 'apt')
                pkg_cache.rebuild_indexes()
                self.logging_service.info("Indexes rebuilt")
            
            self.finished_signal.emit()
            
        except Exception as e:
            self.logging_service.error(f"Worker failed: {e}")
            import traceback
            self.logging_service.error(traceback.format_exc())
            self.error_signal.emit(str(e))
