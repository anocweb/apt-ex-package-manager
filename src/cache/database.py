import sqlite3
import os
from pathlib import Path
from typing import Optional

class DatabaseManager:
    """SQLite database manager for caching package data"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            cache_dir = Path.home() / '.cache' / 'apt-ex-package-manager'
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = cache_dir / 'cache.db'
        
        self.db_path = str(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            # Category cache table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS category_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backend TEXT NOT NULL,
                    name TEXT NOT NULL,
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
                    backend TEXT NOT NULL,
                    package_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    version TEXT,
                    description TEXT,
                    summary TEXT,
                    section TEXT,
                    architecture TEXT,
                    size INTEGER,
                    installed_size INTEGER,
                    maintainer TEXT,
                    homepage TEXT,
                    license TEXT,
                    source_url TEXT,
                    icon_url TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(backend, package_id)
                )
            ''')
            
            # Package metadata table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS package_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_cache_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT,
                    FOREIGN KEY (package_cache_id) REFERENCES package_cache (id) ON DELETE CASCADE,
                    UNIQUE(package_cache_id, key)
                )
            ''')
            
            conn.commit()
    

    
    def is_cache_valid(self, backend: str, max_age_hours: int = 24) -> bool:
        """Check if cache is still valid"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT COUNT(*) FROM category_cache 
                WHERE backend = ? 
                AND datetime(last_updated) > datetime('now', '-{} hours')
            '''.format(max_age_hours), (backend,))
            
            count = cursor.fetchone()[0]
            return count > 0
    
    def is_package_cache_valid(self, backend: str, max_age_hours: int = 24) -> bool:
        """Check if package cache is still valid"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT COUNT(*) FROM package_cache 
                WHERE backend = ? 
                AND datetime(last_updated) > datetime('now', '-{} hours')
            '''.format(max_age_hours), (backend,))
            
            count = cursor.fetchone()[0]
            return count > 0