from typing import List, Optional, Dict
from dataclasses import dataclass
from cache.connection_manager import SQLiteConnectionManager

@dataclass
class PackageSummary:
    """Lightweight package summary for category display"""
    name: str
    description: str
    backend: str
    rating: Optional[float] = None
    review_count: Optional[int] = None

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
    
    def get_summary_by_sections(self, backend: str, sections: List[str], include_rating: bool = False) -> List[PackageSummary]:
        """Get lightweight package summaries for category display"""
        with self.conn_mgr.connection() as conn:
            if not sections:
                # All packages
                base_query = '''
                    SELECT p.name, 
                           CASE 
                               WHEN LENGTH(COALESCE(p.description, p.summary, '')) > 100 
                               THEN SUBSTR(COALESCE(p.description, p.summary, ''), 1, 100) || '...'
                               ELSE COALESCE(p.description, p.summary, '')
                           END as description, 
                           p.backend
                    FROM package_cache p
                    WHERE p.backend = ?
                    ORDER BY p.name
                '''
                params = [backend]
            else:
                # Specific sections
                placeholders = ','.join('?' * len(sections))
                base_query = f'''
                    SELECT p.name, 
                           CASE 
                               WHEN LENGTH(COALESCE(p.description, p.summary, '')) > 100 
                               THEN SUBSTR(COALESCE(p.description, p.summary, ''), 1, 100) || '...'
                               ELSE COALESCE(p.description, p.summary, '')
                           END as description, 
                           p.backend
                    FROM package_cache p
                    WHERE p.backend = ? AND p.section IN ({placeholders})
                    ORDER BY p.name
                '''
                params = [backend] + sections
            
            if include_rating:
                # Join with ratings
                query = base_query.replace(
                    'p.backend\n                    FROM package_cache p',
                    'p.backend, r.rating, r.review_count\n                    FROM package_cache p LEFT JOIN rating_cache r ON p.name = r.app_id'
                )
            else:
                query = base_query
            
            cursor = conn.execute(query, params)
            
            summaries = []
            for row in cursor.fetchall():
                if include_rating and len(row) == 5:
                    summaries.append(PackageSummary(row[0], row[1], row[2], row[3], row[4]))
                else:
                    summaries.append(PackageSummary(row[0], row[1], row[2]))
            
            return summaries
    
    def count_by_section(self, backend: str, section: str) -> int:
        """Count packages by section/category"""
        with self.conn_mgr.connection() as conn:
            cursor = conn.execute('''
                SELECT COUNT(*) FROM package_cache 
                WHERE backend = ? AND section = ?
            ''', (backend, section))
            return cursor.fetchone()[0]
    
    def get_counts_by_sections(self, backend: str, sections: List[str]) -> Dict[str, int]:
        """Get package counts for multiple sections from cache"""
        if not sections:
            return {}
        
        with self.conn_mgr.connection() as conn:
            # Check if section_counts is populated
            cursor = conn.execute('SELECT COUNT(*) FROM section_counts WHERE backend = ?', (backend,))
            if cursor.fetchone()[0] == 0:
                # Fallback: compute and cache counts
                self.update_section_counts(backend)
            
            placeholders = ','.join('?' * len(sections))
            cursor = conn.execute(f'''
                SELECT section, count 
                FROM section_counts 
                WHERE backend = ? AND section IN ({placeholders})
            ''', [backend] + sections)
            
            return dict(cursor.fetchall())
    
    def update_section_counts(self, backend: str):
        """Update precomputed section counts"""
        with self.conn_mgr.transaction() as conn:
            # Delete old counts
            conn.execute('DELETE FROM section_counts WHERE backend = ?', (backend,))
            
            # Insert new counts
            conn.execute('''
                INSERT INTO section_counts (backend, section, count)
                SELECT backend, section, COUNT(*)
                FROM package_cache
                WHERE backend = ?
                GROUP BY backend, section
            ''', (backend,))
            
            # Update statistics for query optimizer
            conn.execute('ANALYZE section_counts')
    
    def delete_stale_packages(self, backend: str, max_age_minutes: int) -> int:
        """Delete packages older than specified age"""
        with self.conn_mgr.transaction('IMMEDIATE') as conn:
            cursor = conn.execute('''
                DELETE FROM package_cache 
                WHERE backend = ? 
                AND datetime(last_updated) < datetime('now', ? || ' minutes')
            ''', (backend, f'-{max_age_minutes}'))
            return cursor.rowcount
    
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