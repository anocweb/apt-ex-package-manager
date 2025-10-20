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
        import time
        start = time.time()
        print("[Worker] InstalledPackagesWorker.run() started")
        try:
            # Load first 20 packages
            print("[Worker] Loading initial batch (20 packages)")
            batch_start = time.time()
            initial_packages = self.apt_controller.get_installed_packages_list(
                self.lmdb_manager, limit=20, offset=0
            )
            print(f"[Worker] Initial batch loaded in {time.time() - batch_start:.3f}s")
            print(f"[Worker] Emitting initial_batch_signal with {len(initial_packages)} packages")
            emit_start = time.time()
            self.initial_batch_signal.emit(initial_packages)
            print(f"[Worker] Signal emitted in {time.time() - emit_start:.3f}s")
            
            # Load remaining packages in batches
            offset = 20
            batch_size = 50
            batch_num = 1
            while True:
                print(f"[Worker] Loading batch {batch_num} (offset={offset}, size={batch_size})")
                batch_start = time.time()
                batch = self.apt_controller.get_installed_packages_list(
                    self.lmdb_manager, limit=batch_size, offset=offset
                )
                print(f"[Worker] Batch {batch_num} loaded in {time.time() - batch_start:.3f}s ({len(batch)} packages)")
                if not batch:
                    print("[Worker] No more packages, stopping")
                    break
                print(f"[Worker] Emitting remaining_batch_signal")
                self.remaining_batch_signal.emit(batch)
                offset += batch_size
                batch_num += 1
            
            print(f"[Worker] InstalledPackagesWorker.run() completed in {time.time() - start:.3f}s")
        except Exception as e:
            print(f"[Worker] ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.error_signal.emit(str(e))
