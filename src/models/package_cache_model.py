from typing import List, Optional, Dict
from dataclasses import dataclass
from cache.connection_manager import SQLiteConnectionManager

@dataclass
class PackageCache:
    """Package cache data model"""
    id: Optional[int] = None
    backend: str = ""
    package_id: str = ""
    name: str = ""
    version: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    section: Optional[str] = None
    architecture: Optional[str] = None
    size: Optional[int] = None
    installed_size: Optional[int] = None
    maintainer: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    source_url: Optional[str] = None
    icon_url: Optional[str] = None
    last_updated: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

class PackageCacheModel:
    """CRUD operations for package cache"""
    
    def __init__(self, connection_manager: SQLiteConnectionManager):
        self.conn_mgr = connection_manager
    
    def create(self, package: PackageCache) -> int:
        """Create a new package with metadata"""
        with self.conn_mgr.transaction() as conn:
            # Insert package
            cursor = conn.execute('''
                INSERT INTO package_cache 
                (backend, package_id, name, version, description, summary, section, 
                 architecture, size, installed_size, maintainer, homepage, license, 
                 source_url, icon_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (package.backend, package.package_id, package.name, package.version,
                  package.description, package.summary, package.section, package.architecture,
                  package.size, package.installed_size, package.maintainer, package.homepage,
                  package.license, package.source_url, package.icon_url))
            
            package_cache_id = cursor.lastrowid
            
            # Insert metadata
            if package.metadata:
                for key, value in package.metadata.items():
                    conn.execute('''
                        INSERT INTO package_metadata (package_cache_id, key, value)
                        VALUES (?, ?, ?)
                    ''', (package_cache_id, key, value))
            
            return package_cache_id
    
    def read(self, package_cache_id: int) -> Optional[PackageCache]:
        """Read a package by ID with metadata"""
        with self.conn_mgr.connection() as conn:
            # Get package
            cursor = conn.execute('''
                SELECT id, backend, package_id, name, version, description, summary, 
                       section, architecture, size, installed_size, maintainer, homepage, 
                       license, source_url, icon_url, last_updated
                FROM package_cache WHERE id = ?
            ''', (package_cache_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            package = PackageCache(*row)
            
            # Get metadata
            metadata_cursor = conn.execute('''
                SELECT key, value FROM package_metadata WHERE package_cache_id = ?
            ''', (package_cache_id,))
            
            package.metadata = dict(metadata_cursor.fetchall())
            return package
    
    def update(self, package: PackageCache) -> bool:
        """Update an existing package and metadata"""
        with self.conn_mgr.transaction() as conn:
            # Update package
            cursor = conn.execute('''
                UPDATE package_cache 
                SET backend = ?, package_id = ?, name = ?, version = ?, description = ?, 
                    summary = ?, section = ?, architecture = ?, size = ?, installed_size = ?, 
                    maintainer = ?, homepage = ?, license = ?, source_url = ?, icon_url = ?
                WHERE id = ?
            ''', (package.backend, package.package_id, package.name, package.version,
                  package.description, package.summary, package.section, package.architecture,
                  package.size, package.installed_size, package.maintainer, package.homepage,
                  package.license, package.source_url, package.icon_url, package.id))
            
            # Update metadata
            if package.metadata:
                # Clear existing metadata
                conn.execute('DELETE FROM package_metadata WHERE package_cache_id = ?', (package.id,))
                
                # Insert new metadata
                for key, value in package.metadata.items():
                    conn.execute('''
                        INSERT INTO package_metadata (package_cache_id, key, value)
                        VALUES (?, ?, ?)
                    ''', (package.id, key, value))
            
            return cursor.rowcount > 0
    
    def delete(self, package_cache_id: int) -> bool:
        """Delete a package (metadata cascades)"""
        with self.conn_mgr.connection() as conn:
            cursor = conn.execute('DELETE FROM package_cache WHERE id = ?', (package_cache_id,))
            return cursor.rowcount > 0
    
    def get_by_backend(self, backend: str) -> List[PackageCache]:
        """Get all packages for a backend"""
        with self.conn_mgr.connection() as conn:
            # Get all packages first
            cursor = conn.execute('''
                SELECT id, backend, package_id, name, version, description, summary, 
                       section, architecture, size, installed_size, maintainer, homepage, 
                       license, source_url, icon_url, last_updated
                FROM package_cache WHERE backend = ?
                ORDER BY name
            ''', (backend,))
            
            packages = []
            package_ids = []
            for row in cursor.fetchall():
                package = PackageCache(*row)
                package.metadata = {}
                packages.append(package)
                package_ids.append(package.id)
            
            # Get all metadata in one query if there are packages
            if package_ids:
                placeholders = ','.join('?' * len(package_ids))
                metadata_cursor = conn.execute(f'''
                    SELECT package_cache_id, key, value 
                    FROM package_metadata 
                    WHERE package_cache_id IN ({placeholders})
                ''', package_ids)
                
                # Group metadata by package ID
                metadata_by_id = {}
                for pkg_id, key, value in metadata_cursor.fetchall():
                    if pkg_id not in metadata_by_id:
                        metadata_by_id[pkg_id] = {}
                    metadata_by_id[pkg_id][key] = value
                
                # Assign metadata to packages
                for package in packages:
                    package.metadata = metadata_by_id.get(package.id, {})
            
            return packages
    
    def search(self, backend: str, query: str) -> List[PackageCache]:
        """Search packages by name or description with optimized ranking"""
        with self.conn_mgr.connection() as conn:
            # Optimized search with ranking: exact name match first, then prefix, then contains
            cursor = conn.execute('''
                SELECT id, backend, package_id, name, version, description, summary, 
                       section, architecture, size, installed_size, maintainer, homepage, 
                       license, source_url, icon_url, last_updated,
                       CASE 
                           WHEN name = ? THEN 1
                           WHEN name LIKE ? THEN 2
                           WHEN name LIKE ? THEN 3
                           WHEN description LIKE ? THEN 4
                           ELSE 5
                       END as rank
                FROM package_cache 
                WHERE backend = ? AND (
                    name LIKE ? OR 
                    description LIKE ?
                )
                ORDER BY rank, name
                LIMIT 100
            ''', (query, f'{query}%', f'%{query}%', f'%{query}%', backend, f'%{query}%', f'%{query}%'))
            
            packages = []
            package_ids = []
            for row in cursor.fetchall():
                # Exclude rank column from PackageCache constructor
                package = PackageCache(*row[:-1])
                package.metadata = {}
                packages.append(package)
                package_ids.append(package.id)
            
            # Get metadata efficiently
            if package_ids:
                placeholders = ','.join('?' * len(package_ids))
                metadata_cursor = conn.execute(f'''
                    SELECT package_cache_id, key, value 
                    FROM package_metadata 
                    WHERE package_cache_id IN ({placeholders})
                ''', package_ids)
                
                # Group metadata by package ID
                metadata_by_id = {}
                for pkg_id, key, value in metadata_cursor.fetchall():
                    if pkg_id not in metadata_by_id:
                        metadata_by_id[pkg_id] = {}
                    metadata_by_id[pkg_id][key] = value
                
                # Assign metadata to packages
                for package in packages:
                    package.metadata = metadata_by_id.get(package.id, {})
            
            return packages
    
    def get_by_section(self, backend: str, section: str) -> List[PackageCache]:
        """Get packages by section/category"""
        with self.conn_mgr.connection() as conn:
            # Get all packages in section first
            cursor = conn.execute('''
                SELECT id, backend, package_id, name, version, description, summary, 
                       section, architecture, size, installed_size, maintainer, homepage, 
                       license, source_url, icon_url, last_updated
                FROM package_cache 
                WHERE backend = ? AND section = ?
                ORDER BY name
            ''', (backend, section))
            
            packages = []
            package_ids = []
            for row in cursor.fetchall():
                package = PackageCache(*row)
                package.metadata = {}
                packages.append(package)
                package_ids.append(package.id)
            
            # Get all metadata in one query if there are packages
            if package_ids:
                placeholders = ','.join('?' * len(package_ids))
                metadata_cursor = conn.execute(f'''
                    SELECT package_cache_id, key, value 
                    FROM package_metadata 
                    WHERE package_cache_id IN ({placeholders})
                ''', package_ids)
                
                # Group metadata by package ID
                metadata_by_id = {}
                for pkg_id, key, value in metadata_cursor.fetchall():
                    if pkg_id not in metadata_by_id:
                        metadata_by_id[pkg_id] = {}
                    metadata_by_id[pkg_id][key] = value
                
                # Assign metadata to packages
                for package in packages:
                    package.metadata = metadata_by_id.get(package.id, {})
            
            return packages