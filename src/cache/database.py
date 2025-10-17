import sqlite3
import os
from pathlib import Path
from typing import Optional
from cache.connection_manager import SQLiteConnectionManager

class DatabaseManager:
    """SQLite database manager for caching package data"""
    
    def __init__(self, db_path: str = None, logging_service=None):
        if db_path is None:
            cache_dir = Path.home() / '.cache' / 'apt-ex-package-manager'
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = cache_dir / 'cache.db'
        
        self.db_path = str(db_path)
        self.connection_manager = SQLiteConnectionManager(self.db_path, logging_service=logging_service)
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        with self.connection_manager.connection() as conn:
            # Category cache table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS category_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backend TEXT(20) NOT NULL,
                    name TEXT(100) NOT NULL,
                    parent_id INTEGER,
                    package_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES category_cache (id),
                    UNIQUE(backend, name, parent_id)
                )
            ''')
            
            # Package cache table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS package_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backend TEXT(20) NOT NULL,
                    package_id TEXT(100) NOT NULL,
                    name TEXT(100) NOT NULL,
                    version TEXT(50),
                    description TEXT(1000),
                    summary TEXT(200),
                    section TEXT(50),
                    architecture TEXT(20),
                    size INTEGER,
                    installed_size INTEGER,
                    maintainer TEXT(100),
                    homepage TEXT(200),
                    license TEXT(50),
                    source_url TEXT(200),
                    icon_url TEXT(200),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(backend, package_id)
                )
            ''')
            
            # Package metadata table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS package_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_cache_id INTEGER NOT NULL,
                    key TEXT(50) NOT NULL,
                    value TEXT(500),
                    FOREIGN KEY (package_cache_id) REFERENCES package_cache (id) ON DELETE CASCADE,
                    UNIQUE(package_cache_id, key)
                )
            ''')
            
            # Section counts cache table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS section_counts (
                    backend TEXT(20) NOT NULL,
                    section TEXT(50) NOT NULL,
                    count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (backend, section)
                )
            ''')
            
            # Create performance indexes
            self._create_indexes(conn)
            conn.commit()
    
    def _create_indexes(self, conn):
        """Create performance indexes"""
        indexes = [
            # Category indexes
            'CREATE INDEX IF NOT EXISTS idx_category_backend ON category_cache(backend)',
            'CREATE INDEX IF NOT EXISTS idx_category_parent ON category_cache(parent_id)',
            'CREATE INDEX IF NOT EXISTS idx_category_updated ON category_cache(last_updated)',
            
            # Package indexes
            'CREATE INDEX IF NOT EXISTS idx_package_backend ON package_cache(backend)',
            'CREATE INDEX IF NOT EXISTS idx_package_name ON package_cache(name)',
            'CREATE INDEX IF NOT EXISTS idx_package_section ON package_cache(section)',
            'CREATE INDEX IF NOT EXISTS idx_package_updated ON package_cache(last_updated)',
            'CREATE INDEX IF NOT EXISTS idx_package_search ON package_cache(name, description)',
            'CREATE INDEX IF NOT EXISTS idx_package_backend_updated ON package_cache(backend, last_updated)',
            
            # Metadata indexes
            'CREATE INDEX IF NOT EXISTS idx_metadata_package ON package_metadata(package_cache_id)',
            'CREATE INDEX IF NOT EXISTS idx_metadata_key ON package_metadata(key)',
            
            # Section counts indexes
            'CREATE INDEX IF NOT EXISTS idx_section_counts_backend ON section_counts(backend)',
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
    

    
    def is_cache_valid(self, backend: str, max_age_hours: int = 24) -> bool:
        """Check if cache is still valid"""
        try:
            with self.connection_manager.connection() as conn:
                cursor = conn.execute('''
                    SELECT 1 FROM category_cache 
                    WHERE backend = ? 
                    AND datetime(last_updated) > datetime('now', '-{} hours')
                    LIMIT 1
                '''.format(max_age_hours), (backend,))
                
                return cursor.fetchone() is not None
        except sqlite3.Error:
            return False
    
    def is_package_cache_valid(self, backend: str, max_age_hours: int = 24) -> bool:
        """Check if package cache is still valid"""
        try:
            with self.connection_manager.connection() as conn:
                cursor = conn.execute('''
                    SELECT 1 FROM package_cache 
                    WHERE backend = ? 
                    AND datetime(last_updated) > datetime('now', '-{} hours')
                    LIMIT 1
                '''.format(max_age_hours), (backend,))
                
                return cursor.fetchone() is not None
        except sqlite3.Error:
            return False
    
    def close(self):
        """Close connection manager"""
        self.connection_manager.close_all()