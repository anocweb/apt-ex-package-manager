from typing import Dict, List, Optional
from models.package_cache_model import PackageCacheModel, PackageCache as PackageCacheData
from cache.connection_manager import SQLiteConnectionManager

class PackageCache:
    """Package cache interface"""
    
    def __init__(self, connection_manager: SQLiteConnectionManager, logging_service=None):
        self.model = PackageCacheModel(connection_manager)
        self.conn_mgr = connection_manager
        self.logger = logging_service.get_logger('cache.package') if logging_service else None
    
    def log(self, message):
        """Log message if logger is available"""
        if self.logger:
            self.logger.info(message)
    
    def get_packages(self, backend: str) -> Optional[List[PackageCacheData]]:
        """Get cached packages for backend"""
        if self.logger:
            self.logger.debug(f"Getting packages for {backend}")
        if not self.is_cache_valid(backend):
            self.log(f"Package cache expired for {backend}")
            return None
        packages = self.model.get_by_backend(backend)
        self.log(f"Retrieved {len(packages) if packages else 0} cached packages for {backend}")
        return packages
    
    def set_packages(self, backend: str, packages: List[Dict]):
        """Cache packages for backend using bulk insert"""
        # Clear existing packages for this backend
        self.clear_cache(backend)
        
        if not packages:
            return
        
        # Bulk insert for better performance
        with self.conn_mgr.transaction() as conn:
            # Prepare package data
            package_data = []
            
            for pkg_data in packages:
                package_values = (
                    pkg_data['backend'], pkg_data['package_id'], pkg_data['name'],
                    pkg_data.get('version'), pkg_data.get('description'), pkg_data.get('summary'),
                    pkg_data.get('section'), pkg_data.get('architecture'), pkg_data.get('size'),
                    pkg_data.get('installed_size'), pkg_data.get('maintainer'), pkg_data.get('homepage'),
                    pkg_data.get('license'), pkg_data.get('source_url'), pkg_data.get('icon_url')
                )
                package_data.append(package_values)
            
            # Bulk insert packages
            conn.executemany('''
                INSERT INTO package_cache 
                (backend, package_id, name, version, description, summary, section, 
                 architecture, size, installed_size, maintainer, homepage, license, 
                 source_url, icon_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', package_data)
        
        self.log(f"Bulk cached {len(packages)} packages for {backend}")
    
    def clear_cache(self, backend: Optional[str] = None):
        """Clear cache for specific backend or all backends"""
        if self.logger:
            self.logger.debug(f"Clearing package cache for {backend or 'all backends'}")
        
        with self.conn_mgr.connection() as conn:
            if backend:
                cursor = conn.execute('DELETE FROM package_cache WHERE backend = ?', (backend,))
                count = cursor.rowcount
                self.log(f"Cleared {count} cached packages for {backend}")
            else:
                cursor = conn.execute('DELETE FROM package_cache')
                count = cursor.rowcount
                self.log(f"Cleared {count} cached packages")
    
    def is_cache_valid(self, backend: str, max_age_hours: int = 24) -> bool:
        """Check if cache is still valid"""
        with self.conn_mgr.connection() as conn:
            cursor = conn.execute('''
                SELECT 1 FROM package_cache 
                WHERE backend = ? 
                AND last_updated > datetime('now', ? || ' hours')
                LIMIT 1
            ''', (backend, f'-{max_age_hours}'))
            
            return cursor.fetchone() is not None