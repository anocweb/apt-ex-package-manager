from typing import Dict, List, Optional
from models.package_cache_model import PackageCacheModel, PackageCache as PackageCacheData

class PackageCache:
    """Package cache interface"""
    
    def __init__(self, logger=None):
        self.model = PackageCacheModel()
        self.logger = logger
    
    def log(self, message):
        """Log message if logger is available"""
        if self.logger:
            self.logger.info(message)
    
    def get_packages(self, backend: str) -> Optional[List[PackageCacheData]]:
        """Get cached packages for backend"""
        if hasattr(self, 'logger') and self.logger:
            self.logger.debug(f"Getting packages for {backend}")
        if not self.is_cache_valid(backend):
            self.log(f"Package cache expired for {backend}")
            return None
        packages = self.model.get_by_backend(backend)
        self.log(f"Retrieved {len(packages) if packages else 0} cached packages for {backend}")
        return packages
    
    def set_packages(self, backend: str, packages: List[Dict]):
        """Cache packages for backend"""
        # Clear existing packages for this backend
        self.clear_cache(backend)
        
        # Insert new packages
        for pkg_data in packages:
            package = PackageCacheData(
                backend=pkg_data['backend'],
                package_id=pkg_data['package_id'],
                name=pkg_data['name'],
                version=pkg_data.get('version'),
                description=pkg_data.get('description'),
                summary=pkg_data.get('summary'),
                section=pkg_data.get('section'),
                architecture=pkg_data.get('architecture'),
                size=pkg_data.get('size'),
                installed_size=pkg_data.get('installed_size'),
                maintainer=pkg_data.get('maintainer'),
                homepage=pkg_data.get('homepage'),
                metadata=pkg_data.get('metadata', {})
            )
            self.model.create(package)
    
    def clear_cache(self, backend: Optional[str] = None):
        """Clear cache for specific backend or all backends"""
        if hasattr(self, 'logger') and self.logger:
            self.logger.debug(f"Clearing package cache for {backend or 'all backends'}")
        if backend:
            packages = self.model.get_by_backend(backend)
            count = len(packages)
            for package in packages:
                self.model.delete(package.id)
            self.log(f"Cleared {count} cached packages for {backend}")
        else:
            # Clear all packages
            import sqlite3
            with sqlite3.connect(self.model.db.db_path) as conn:
                conn.execute('DELETE FROM package_cache')
                conn.commit()
            self.log("Cleared all cached packages")
    
    def is_cache_valid(self, backend: str, max_age_hours: int = 24) -> bool:
        """Check if cache is still valid"""
        return self.model.db.is_package_cache_valid(backend, max_age_hours)