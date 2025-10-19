from PyQt6.QtWidgets import QApplication
from config.app_config import AppConfig
from services.service_container import ServiceContainer
from services.theme_service import ThemeService
from services.logging_service import LoggingService
from cache import LMDBManager
from controllers.package_manager import PackageManager
from views.main_view import MainView

class ApplicationController:
    """Coordinate application lifecycle and service initialization"""
    
    def __init__(self, app: QApplication, config: AppConfig):
        self.app = app
        self.config = config
        self.container = ServiceContainer()
        self.main_view = None
    
    def initialize(self) -> None:
        """Initialize all services and components"""
        self._setup_theme()
        self._initialize_services()
        self._create_main_view()
        self._setup_dev_mode()
    
    def _setup_theme(self) -> None:
        """Set up theme service and application icon"""
        theme_service = ThemeService(self.app)
        theme_service.setup_application_icon()
        self.container.register('theme', theme_service)
    
    def _initialize_services(self) -> None:
        """Initialize core services"""
        # Logging service
        logging_service = LoggingService(stdout_log_level=self.config.stdout_log_level)
        self.container.register('logging', logging_service)
        
        # LMDB manager
        lmdb_manager = LMDBManager(logging_service=logging_service)
        self.container.register('lmdb', lmdb_manager)
        
        # Package manager
        package_manager = PackageManager(lmdb_manager, logging_service)
        self.container.register('package_manager', package_manager)
    
    def _create_main_view(self) -> None:
        """Create main view with dependency injection"""
        self.main_view = MainView(
            self.container.get('package_manager'),
            self.container.get('lmdb'),
            logging_service=self.container.get('logging'),
            dev_logging=self.config.dev_logging,
            stdout_log_level=self.config.stdout_log_level
        )
    
    def _setup_dev_mode(self) -> None:
        """Configure development mode features"""
        if self.config.dev_logging:
            self.main_view.setup_dev_mode(dev_logging=True)
    
    def show_main_window(self) -> None:
        """Show the main application window"""
        if self.main_view:
            self.main_view.show()
    
    def cleanup(self) -> None:
        """Clean up resources on application exit"""
        if self.container.has('lmdb'):
            self.container.get('lmdb').close()
