from cache.category_cache import CategoryCache
from cache.package_cache import PackageCache

class CacheManager:
    """Centralized cache management with expiration handling"""
    
    def __init__(self, connection_manager, logging_service=None):
        self.logging_service = logging_service
        self.logger = logging_service.get_logger('cache.manager') if logging_service else None
        self.category_cache = CategoryCache(connection_manager, logging_service)
        self.package_cache = PackageCache(connection_manager, logging_service)
    
    def is_cache_expired(self, backend: str) -> bool:
        """Check if any cache is expired for the backend"""
        category_expired = not self.category_cache.is_cache_valid(backend)
        package_expired = not self.package_cache.is_cache_valid(backend)
        
        if self.logger:
            self.logger.debug(f"Cache status for {backend} - categories: {'expired' if category_expired else 'valid'}, packages: {'expired' if package_expired else 'valid'}")
        
        return category_expired or package_expired
    
    def needs_category_update(self, backend: str) -> bool:
        """Check if category cache needs update"""
        return not self.category_cache.is_cache_valid(backend)
    
    def needs_package_update(self, backend: str) -> bool:
        """Check if package cache needs update"""
        return not self.package_cache.is_cache_valid(backend)
    
    def get_categories(self, backend: str):
        """Get categories from cache"""
        return self.category_cache.get_categories(backend)
    
    def set_categories(self, backend: str, categories):
        """Set categories in cache"""
        self.category_cache.set_categories(backend, categories)
    
    def get_packages(self, backend: str):
        """Get packages from cache"""
        return self.package_cache.get_packages(backend)
    
    def clear_cache(self, backend: str = None):
        """Clear all caches for backend"""
        if self.logger:
            self.logger.info(f"Clearing all caches for {backend or 'all backends'}")
        self.category_cache.clear_cache(backend)
        self.package_cache.clear_cache(backend)