import lmdb
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

class LMDBManager:
    """LMDB database manager for caching package data"""
    
    # Database names
    DB_PACKAGES_APT = 'packages_apt'
    DB_PACKAGES_FLATPAK = 'packages_flatpak'
    DB_PACKAGES_APPIMAGE = 'packages_appimage'
    DB_CATEGORIES_APT = 'categories_apt'
    DB_CATEGORIES_FLATPAK = 'categories_flatpak'
    DB_CATEGORIES_APPIMAGE = 'categories_appimage'
    DB_INDEXES = 'indexes'
    DB_METADATA = 'metadata'
    
    def __init__(self, db_path: str = None, logging_service=None):
        self.logger = logging_service.get_logger('db.lmdb') if logging_service else None
        self.db_path = self._get_db_path(db_path)
        
        # Create directory if it doesn't exist
        os.makedirs(self.db_path, exist_ok=True)
        
        # Open LMDB environment with 8 named databases
        self.env = lmdb.open(
            self.db_path,
            max_dbs=8,
            map_size=1024 * 1024 * 1024,  # 1GB initial size
            sync=True,
            writemap=True
        )
        
        # Open all named databases
        self._dbs = {}
        self._init_databases()
        
        if self.logger:
            self.logger.info(f"LMDB initialized at {self.db_path}")
    
    def _get_db_path(self, custom_path: Optional[str]) -> str:
        """Determine database path based on environment"""
        if custom_path:
            return custom_path
        
        # Check if running from source (development)
        src_dir = Path(__file__).parent.parent.parent
        data_dir = src_dir / 'data'
        
        if src_dir.name == 'apt-ex-package-manager' and (src_dir / 'src').exists():
            # Development mode
            data_dir.mkdir(exist_ok=True)
            return str(data_dir / 'cache.lmdb')
        
        # Production mode - use XDG data directory
        xdg_data = os.environ.get('XDG_DATA_HOME')
        if xdg_data:
            base_dir = Path(xdg_data)
        else:
            base_dir = Path.home() / '.local' / 'share'
        
        app_data_dir = base_dir / 'apt-ex-package-manager'
        app_data_dir.mkdir(parents=True, exist_ok=True)
        return str(app_data_dir / 'cache.lmdb')
    
    def _init_databases(self):
        """Initialize all named databases"""
        db_names = [
            self.DB_PACKAGES_APT,
            self.DB_PACKAGES_FLATPAK,
            self.DB_PACKAGES_APPIMAGE,
            self.DB_CATEGORIES_APT,
            self.DB_CATEGORIES_FLATPAK,
            self.DB_CATEGORIES_APPIMAGE,
            self.DB_INDEXES,
            self.DB_METADATA
        ]
        
        with self.env.begin(write=True) as txn:
            for db_name in db_names:
                self._dbs[db_name] = self.env.open_db(db_name.encode(), txn=txn)
    
    def get_db(self, db_name: str):
        """Get named database handle"""
        return self._dbs.get(db_name)
    
    @contextmanager
    def transaction(self, write: bool = False):
        """Context manager for LMDB transactions"""
        txn = self.env.begin(write=write)
        try:
            yield txn
            if write:
                txn.commit()
        except Exception:
            txn.abort()
            raise
    
    def put(self, db_name: str, key: str, value: Dict[str, Any]):
        """Store data in specified database"""
        db = self.get_db(db_name)
        with self.transaction(write=True) as txn:
            txn.put(key.encode(), json.dumps(value).encode(), db=db)
    
    def get(self, db_name: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from specified database"""
        db = self.get_db(db_name)
        with self.transaction() as txn:
            data = txn.get(key.encode(), db=db)
            return json.loads(data.decode()) if data else None
    
    def delete(self, db_name: str, key: str) -> bool:
        """Delete data from specified database"""
        db = self.get_db(db_name)
        with self.transaction(write=True) as txn:
            return txn.delete(key.encode(), db=db)
    
    def scan(self, db_name: str, prefix: str = None) -> List[Dict[str, Any]]:
        """Scan database with optional prefix filter"""
        db = self.get_db(db_name)
        results = []
        
        with self.transaction() as txn:
            cursor = txn.cursor(db=db)
            
            if prefix:
                prefix_bytes = prefix.encode()
                if cursor.set_range(prefix_bytes):
                    for key, value in cursor:
                        if not key.startswith(prefix_bytes):
                            break
                        results.append(json.loads(value.decode()))
            else:
                for key, value in cursor:
                    results.append(json.loads(value.decode()))
        
        return results
    
    def clear_db(self, db_name: str):
        """Clear all entries in a database"""
        db = self.get_db(db_name)
        with self.transaction(write=True) as txn:
            txn.drop(db, delete=False)
    
    def close(self):
        """Close LMDB environment"""
        if self.env:
            self.env.close()
            if self.logger:
                self.logger.info("LMDB environment closed")
