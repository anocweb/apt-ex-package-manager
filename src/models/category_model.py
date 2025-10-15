from typing import List, Optional, Dict
from dataclasses import dataclass
from cache.database import DatabaseManager

@dataclass
class Category:
    """Category data model"""
    id: Optional[int] = None
    backend: str = ""
    name: str = ""
    parent_id: Optional[int] = None
    package_count: int = 0
    last_updated: Optional[str] = None

class CategoryModel:
    """CRUD operations for category cache"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def create(self, category: Category) -> int:
        """Create a new category"""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO category_cache (backend, name, parent_id, package_count)
                VALUES (?, ?, ?, ?)
            ''', (category.backend, category.name, category.parent_id, category.package_count))
            conn.commit()
            return cursor.lastrowid
    
    def read(self, category_id: int) -> Optional[Category]:
        """Read a category by ID"""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, backend, name, parent_id, package_count, last_updated
                FROM category_cache WHERE id = ?
            ''', (category_id,))
            row = cursor.fetchone()
            
            if row:
                return Category(*row)
            return None
    
    def update(self, category: Category) -> bool:
        """Update an existing category"""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute('''
                UPDATE category_cache 
                SET backend = ?, name = ?, parent_id = ?, package_count = ?
                WHERE id = ?
            ''', (category.backend, category.name, category.parent_id, 
                  category.package_count, category.id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete(self, category_id: int) -> bool:
        """Delete a category and its children"""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            # Delete children first
            conn.execute('DELETE FROM category_cache WHERE parent_id = ?', (category_id,))
            # Delete the category
            cursor = conn.execute('DELETE FROM category_cache WHERE id = ?', (category_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_by_backend(self, backend: str) -> List[Category]:
        """Get all categories for a backend"""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, backend, name, parent_id, package_count, last_updated
                FROM category_cache WHERE backend = ?
                ORDER BY parent_id, name
            ''', (backend,))
            
            return [Category(*row) for row in cursor.fetchall()]
    
    def get_children(self, parent_id: int) -> List[Category]:
        """Get child categories of a parent"""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, repository, name, parent_id, package_count, last_updated
                FROM category_cache WHERE parent_id = ?
                ORDER BY name
            ''', (parent_id,))
            
            return [Category(*row) for row in cursor.fetchall()]
    
    def get_root_categories(self, backend: str) -> List[Category]:
        """Get root categories (no parent) for a backend"""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, backend, name, parent_id, package_count, last_updated
                FROM category_cache WHERE backend = ? AND parent_id IS NULL
                ORDER BY name
            ''', (backend,))
            
            return [Category(*row) for row in cursor.fetchall()]