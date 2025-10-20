import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from cache.lmdb_manager import LMDBManager
from cache.data_structures import PackageData, IndexData

class PackageCacheModel:
    """Model for managing package cache in LMDB"""
    
    def __init__(self, lmdb_manager: LMDBManager, backend: str = 'apt'):
        self.lmdb = lmdb_manager
        self.backend = backend.lower()
        self.db_name = f'packages_{self.backend}'
        self.indexes_db = LMDBManager.DB_INDEXES
    
    def add_package(self, package_data: PackageData) -> bool:
        """Add or update package in cache"""
        try:
            self.lmdb.put(self.db_name, package_data.package_id, package_data.to_dict())
            self._update_indexes(package_data)
            return True
        except Exception:
            return False
    
    def add_packages_bulk(self, packages: List[PackageData], update_indexes: bool = False) -> int:
        """Add multiple packages in a single transaction
        
        Args:
            packages: List of PackageData objects to add
            update_indexes: Whether to update indexes (slow, skip for bulk operations)
            
        Returns:
            Number of packages successfully added
        """
        count = 0
        db = self.lmdb.get_db(self.db_name)
        
        try:
            with self.lmdb.transaction(write=True) as txn:
                for package in packages:
                    txn.put(
                        package.package_id.encode(),
                        json.dumps(package.to_dict()).encode(),
                        db=db
                    )
                    count += 1
            
            # Optionally update indexes (skip during initial bulk load)
            if update_indexes:
                for package in packages:
                    self._update_indexes(package)
            
            return count
        except Exception:
            return count
    
    def rebuild_indexes(self) -> None:
        """Rebuild all indexes from cached packages"""
        # Clear existing indexes
        self._clear_backend_indexes()
        
        # Collect all index data first
        section_indexes = {}  # section -> [package_ids]
        installed_packages = []
        
        all_packages = self.get_all_packages()
        for package in all_packages:
            # Section index
            if package.section:
                if package.section not in section_indexes:
                    section_indexes[package.section] = []
                section_indexes[package.section].append(package.package_id)
            
            # Installed index
            if package.is_installed:
                installed_packages.append(package.package_id)
        
        # Write all indexes in bulk
        indexes_db = self.lmdb.get_db(self.indexes_db)
        with self.lmdb.transaction(write=True) as txn:
            # Write section indexes
            for section, package_ids in section_indexes.items():
                index_key = f"section:{self.backend}:{section}"
                index_data = {
                    'index_type': 'section',
                    'value': section,
                    'package_ids': package_ids
                }
                txn.put(index_key.encode(), json.dumps(index_data).encode(), db=indexes_db)
            
            # Write installed index
            if installed_packages:
                index_key = f"installed:{self.backend}:1"
                index_data = {
                    'index_type': 'installed',
                    'value': '1',
                    'package_ids': installed_packages
                }
                txn.put(index_key.encode(), json.dumps(index_data).encode(), db=indexes_db)
    
    def get_package(self, package_id: str) -> Optional[PackageData]:
        """Get package by ID"""
        data = self.lmdb.get(self.db_name, package_id)
        return PackageData.from_dict(data) if data else None
    
    def delete_package(self, package_id: str) -> bool:
        """Delete package from cache"""
        package = self.get_package(package_id)
        if package:
            self._remove_from_indexes(package)
        return self.lmdb.delete(self.db_name, package_id)
    
    def get_all_packages(self, limit: Optional[int] = None, offset: int = 0) -> List[PackageData]:
        """Get all packages with pagination"""
        packages = []
        db = self.lmdb.get_db(self.db_name)
        
        with self.lmdb.transaction() as txn:
            cursor = txn.cursor(db=db)
            
            # Skip offset
            if cursor.first():
                for _ in range(offset):
                    if not cursor.next():
                        break
                
                # Collect packages
                count = 0
                for key, value in cursor:
                    if limit and count >= limit:
                        break
                    packages.append(PackageData.from_dict(json.loads(value.decode())))
                    count += 1
        
        return packages
    
    def search_packages(self, query: str) -> List[PackageData]:
        """Search packages by name or description"""
        query_lower = query.lower()
        results = []
        db = self.lmdb.get_db(self.db_name)
        
        with self.lmdb.transaction() as txn:
            cursor = txn.cursor(db=db)
            for key, value in cursor:
                pkg_data = json.loads(value.decode())
                name = pkg_data.get('name', '').lower()
                desc = pkg_data.get('description', '').lower()
                
                if query_lower in name or query_lower in desc:
                    results.append(PackageData.from_dict(pkg_data))
        
        return results
    
    def get_packages_by_section(self, section: str) -> List[PackageData]:
        """Get packages by section using index"""
        index_key = f"section:{self.backend}:{section}"
        index_data = self.lmdb.get(self.indexes_db, index_key)
        
        if not index_data:
            return []
        
        package_ids = index_data.get('package_ids', [])
        packages = []
        
        for pkg_id in package_ids:
            pkg = self.get_package(pkg_id)
            if pkg:
                packages.append(pkg)
        
        return packages
    
    def get_installed_packages(self) -> List[PackageData]:
        """Get installed packages using index"""
        index_key = f"installed:{self.backend}:1"
        index_data = self.lmdb.get(self.indexes_db, index_key)
        
        if not index_data:
            return []
        
        package_ids = index_data.get('package_ids', [])
        packages = []
        
        for pkg_id in package_ids:
            pkg = self.get_package(pkg_id)
            if pkg:
                packages.append(pkg)
        
        return packages
    
    def update_installed_status(self, package_id: str, is_installed: bool) -> bool:
        """Update package installation status"""
        pkg = self.get_package(package_id)
        if not pkg:
            return False
        
        pkg.is_installed = is_installed
        pkg.last_updated = datetime.now().isoformat()
        return self.add_package(pkg)
    
    def update_installed_status_bulk(self, installed_names: set) -> int:
        """Update installed status for all packages in bulk
        
        Args:
            installed_names: Set of package names that are installed
            
        Returns:
            Number of packages updated
        """
        count = 0
        db = self.lmdb.get_db(self.db_name)
        timestamp = datetime.now().isoformat()
        
        # Update all packages in single transaction
        with self.lmdb.transaction(write=True) as txn:
            cursor = txn.cursor(db=db)
            for key, value in cursor:
                pkg_data = json.loads(value.decode())
                pkg_name = pkg_data.get('name')
                is_installed = pkg_name in installed_names
                
                # Only update if status changed
                if pkg_data.get('is_installed') != is_installed:
                    pkg_data['is_installed'] = is_installed
                    pkg_data['last_updated'] = timestamp
                    txn.put(key, json.dumps(pkg_data).encode(), db=db)
                    count += 1
        
        return count
    
    def clear_cache(self):
        """Clear all packages for this backend"""
        self.lmdb.clear_db(self.db_name)
        self._clear_backend_indexes()
    
    def is_cache_empty(self) -> bool:
        """Check if cache is empty"""
        packages = self.get_all_packages(limit=1)
        return len(packages) == 0
    
    def _update_indexes(self, package: PackageData):
        """Update search indexes for package"""
        # Section index
        if package.section:
            self._add_to_index('section', package.section, package.package_id)
        
        # Installed index
        if package.is_installed:
            self._add_to_index('installed', '1', package.package_id)
    
    def _add_to_index(self, index_type: str, value: str, package_id: str):
        """Add package to index"""
        index_key = f"{index_type}:{self.backend}:{value}"
        index_data = self.lmdb.get(self.indexes_db, index_key)
        
        if index_data:
            package_ids = index_data.get('package_ids', [])
            if package_id not in package_ids:
                package_ids.append(package_id)
        else:
            package_ids = [package_id]
        
        self.lmdb.put(self.indexes_db, index_key, {
            'index_type': index_type,
            'value': value,
            'package_ids': package_ids
        })
    
    def _remove_from_indexes(self, package: PackageData):
        """Remove package from all indexes"""
        if package.section:
            self._remove_from_index('section', package.section, package.package_id)
        
        if package.is_installed:
            self._remove_from_index('installed', '1', package.package_id)
    
    def _remove_from_index(self, index_type: str, value: str, package_id: str):
        """Remove package from index"""
        index_key = f"{index_type}:{self.backend}:{value}"
        index_data = self.lmdb.get(self.indexes_db, index_key)
        
        if index_data:
            package_ids = index_data.get('package_ids', [])
            if package_id in package_ids:
                package_ids.remove(package_id)
                
                if package_ids:
                    self.lmdb.put(self.indexes_db, index_key, {
                        'index_type': index_type,
                        'value': value,
                        'package_ids': package_ids
                    })
                else:
                    self.lmdb.delete(self.indexes_db, index_key)
    
    def _clear_backend_indexes(self):
        """Clear all indexes for this backend"""
        db = self.lmdb.get_db(self.indexes_db)
        prefix = f"{self.backend}:".encode()
        
        with self.lmdb.transaction(write=True) as txn:
            cursor = txn.cursor(db=db)
            if cursor.set_range(prefix):
                keys_to_delete = []
                for key, _ in cursor:
                    if not key.startswith(prefix):
                        break
                    keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    txn.delete(key, db=db)
