from PyQt6.QtWidgets import QApplication
from config.app_config import AppConfig
from services.service_container import ServiceContainer
from services.theme_service import ThemeService
from services.logging_service import LoggingService
from cache import LMDBManager, PackageCacheModel
from controllers.package_manager import PackageManager
from views.main_view import MainView
from views.splash_screen import SplashScreen

class ApplicationController:
    """Coordinate application lifecycle and service initialization"""
    
    def __init__(self, app: QApplication, config: AppConfig):
        self.app = app
        self.config = config
        self.container = ServiceContainer()
        self.main_view = None
        self.splash = None
    
    def initialize(self) -> None:
        """Initialize all services and components"""
        self._show_splash()
        self._setup_theme()
        self._initialize_services()
        self._populate_cache()
        self._create_main_view()
        self._setup_dev_mode()
    
    def _show_splash(self) -> None:
        """Show splash screen"""
        self.splash = SplashScreen()
        self.splash.show()
        self.splash.set_status("Starting up...")
    
    def _hide_splash(self) -> None:
        """Hide splash screen"""
        if self.splash:
            self.splash.finish(self.main_view)
            self.splash = None
    
    def _setup_theme(self) -> None:
        """Set up theme service and application icon"""
        if self.splash:
            self.splash.set_status("Setting up theme...")
        
        theme_service = ThemeService(self.app)
        theme_service.setup_application_icon()
        self.container.register('theme', theme_service)
    
    def _initialize_services(self) -> None:
        """Initialize core services"""
        if self.splash:
            self.splash.set_status("Initializing services...")
        
        # Logging service
        logging_service = LoggingService(stdout_log_level=self.config.stdout_log_level)
        self.container.register('logging', logging_service)
        
        # LMDB manager
        lmdb_manager = LMDBManager(logging_service=logging_service)
        self.container.register('lmdb', lmdb_manager)
        
        # Package manager
        if self.splash:
            self.splash.set_status("Discovering plugins...")
        package_manager = PackageManager(lmdb_manager, logging_service)
        self.container.register('package_manager', package_manager)
    
    def _populate_cache(self) -> None:
        """Populate cache before creating main view"""
        from controllers.apt_controller import APTController
        from cache import PackageData
        import time
        
        logging_service = self.container.get('logging')
        lmdb_manager = self.container.get('lmdb')
        
        logger = logging_service.get_logger('startup')
        
        start_time = time.time()
        print("\n=== Starting cache population ===")
        print("Checking cache status...")
        logger.info("=== Starting cache population ===")
        logger.info("Checking cache status...")
        
        if self.splash:
            self.splash.update_progress(5, "Checking cache status...")
        
        # Check if cache is empty
        pkg_cache = PackageCacheModel(lmdb_manager, 'apt')
        cache_is_empty = pkg_cache.is_cache_empty()
        
        check_time = time.time()
        if cache_is_empty:
            print("Cache is empty, building initial cache...")
            logger.info("Cache is empty, building initial cache...")
            if self.splash:
                self.splash.update_progress(10, "Building APT package cache...")
        else:
            print("Refreshing package cache...")
            logger.info("Refreshing package cache...")
            if self.splash:
                self.splash.update_progress(10, "Refreshing APT package cache...")
        elapsed = time.time() - check_time
        print(f"Cache check took: {elapsed:.2f}s")
        logger.info(f"Cache check took: {elapsed:.2f}s")
        
        # Update cache synchronously
        apt_controller = APTController(logging_service=logging_service)
        
        # Load packages
        load_start = time.time()
        print("Loading package details from APT...")
        logger.info("Loading package details from APT...")
        if self.splash:
            self.splash.update_progress(15, "Loading APT package database...")
        
        packages = apt_controller.get_all_packages_for_cache()
        load_time = time.time() - load_start
        print(f"Loaded {len(packages)} packages in {load_time:.2f}s")
        logger.info(f"Loaded {len(packages)} packages in {load_time:.2f}s")
        
        # Cache packages in batches using bulk insert with parallel processing
        cache_start = time.time()
        print("Caching packages...")
        logger.info("Caching packages...")
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        batch_size = 5000  # Larger batches for bulk insert
        total = len(packages)
        
        def prepare_batch(batch_data):
            """Prepare PackageData objects in parallel"""
            package_objects = []
            for pkg_data in batch_data:
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
                package_objects.append(package)
            return package_objects
        
        # Prepare batches
        batches = []
        for batch_start in range(0, total, batch_size):
            batch_end = min(batch_start + batch_size, total)
            batches.append((batch_start, packages[batch_start:batch_end]))
        
        # Process batches in parallel (data preparation)
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(prepare_batch, batch_data): batch_start 
                      for batch_start, batch_data in batches}
            
            completed = 0
            for future in as_completed(futures):
                batch_start = futures[future]
                package_objects = future.result()
                
                # Write to LMDB without index updates (single-threaded, serialized)
                pkg_cache.add_packages_bulk(package_objects, update_indexes=False)
                
                completed += len(package_objects)
                
                # Update progress (15% to 85% for caching)
                progress = 15 + int((completed / total) * 70)
                if self.splash:
                    self.splash.update_progress(
                        progress,
                        "Caching APT packages...",
                        f"Cached {completed:,} / {total:,} packages"
                    )
        
        cache_time = time.time() - cache_start
        print(f"Cached {total} packages in {cache_time:.2f}s ({total/cache_time:.0f} pkg/s)")
        logger.info(f"Cached {total} packages in {cache_time:.2f}s ({total/cache_time:.0f} pkg/s)")
        
        # Rebuild indexes after all packages cached
        index_start = time.time()
        print("Rebuilding indexes...")
        if self.splash:
            self.splash.update_progress(88, "Rebuilding indexes...")
        pkg_cache.rebuild_indexes()
        index_time = time.time() - index_start
        print(f"Rebuilt indexes in {index_time:.2f}s")
        logger.info(f"Rebuilt indexes in {index_time:.2f}s")
        
        # Update installed status
        status_start = time.time()
        print("Updating installed package status...")
        logger.info("Updating installed package status...")
        if self.splash:
            self.splash.update_progress(90, "Updating APT installed status...")
        
        apt_controller.update_installed_status(lmdb_manager)
        status_time = time.time() - status_start
        print(f"Updated installed status in {status_time:.2f}s")
        logger.info(f"Updated installed status in {status_time:.2f}s")
        
        total_time = time.time() - start_time
        print(f"=== Cache population complete in {total_time:.2f}s ===\n")
        logger.info(f"=== Cache population complete in {total_time:.2f}s ===")
        if self.splash:
            self.splash.update_progress(95, "APT cache ready", f"Loaded {total:,} packages")
    
    def _create_main_view(self) -> None:
        """Create main view with dependency injection"""
        if self.splash:
            self.splash.update_progress(98, "Loading user interface...")
        
        self.main_view = MainView(
            self.container.get('package_manager'),
            self.container.get('lmdb'),
            logging_service=self.container.get('logging'),
            dev_logging=self.config.dev_logging,
            stdout_log_level=self.config.stdout_log_level
        )
        
        if self.splash:
            self.splash.update_progress(100, "Ready")
    
    def _setup_dev_mode(self) -> None:
        """Configure development mode features"""
        if self.config.dev_logging:
            self.main_view.setup_dev_mode(dev_logging=True)
    
    def show_main_window(self) -> None:
        """Show the main application window"""
        if self.main_view:
            if self.splash:
                self.splash.finish(self.main_view)
                self.splash = None
            self.main_view.show()
    
    def cleanup(self) -> None:
        """Clean up resources on application exit"""
        if self.container.has('lmdb'):
            self.container.get('lmdb').close()
