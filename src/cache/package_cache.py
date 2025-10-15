from typing import Dict, List, Optional
from models.package_cache_model import PackageCacheModel, PackageCache as PackageCacheData

class PackageCache:
    """Package cache interface"""
    
    def __init__(self):
        self.model = PackageCacheModel()
    
    def get_packages(self, backend: str) -> Optional[List[PackageCacheData]]:
        """Get cached packages for backend"""
        if not self.is_cache_valid(backend):
            return None
        return self.model.get_by_backend(backend)
    
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
        if backend:
            packages = self.model.get_by_backend(backend)
            for package in packages:
                self.model.delete(package.id)
        else:
            # Clear all packages
            import sqlite3
            with sqlite3.connect(self.model.db.db_path) as conn:
                conn.execute('DELETE FROM package_cache')
                conn.commit()
    
    def is_cache_valid(self, backend: str, max_age_hours: int = 24) -> bool:
        """Check if cache is still valid"""
        return self.model.db.is_package_cache_valid(backend, max_age_hours)