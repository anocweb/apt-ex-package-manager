import json
from typing import List, Optional
from datetime import datetime, timedelta
from cache.lmdb_manager import LMDBManager
from cache.data_structures import CategoryData

class CategoryCacheModel:
    """Model for managing category cache in LMDB"""
    
    def __init__(self, lmdb_manager: LMDBManager, backend: str = 'apt'):
        self.lmdb = lmdb_manager
        self.backend = backend.lower()
        self.db_name = f'categories_{self.backend}'
    
    def add_category(self, category: CategoryData) -> bool:
        """Add or update category in cache"""
        try:
            self.lmdb.put(self.db_name, category.name, category.to_dict())
            return True
        except Exception:
            return False
    
    def get_category(self, name: str) -> Optional[CategoryData]:
        """Get category by name"""
        data = self.lmdb.get(self.db_name, name)
        return CategoryData.from_dict(data) if data else None
    
    def delete_category(self, name: str) -> bool:
        """Delete category from cache"""
        return self.lmdb.delete(self.db_name, name)
    
    def get_all_categories(self) -> List[CategoryData]:
        """Get all categories"""
        categories = []
        db = self.lmdb.get_db(self.db_name)
        
        with self.lmdb.transaction() as txn:
            cursor = txn.cursor(db=db)
            for key, value in cursor:
                categories.append(CategoryData.from_dict(json.loads(value.decode())))
        
        return categories
    
    def get_root_categories(self) -> List[CategoryData]:
        """Get categories without parent"""
        all_categories = self.get_all_categories()
        return [cat for cat in all_categories if cat.parent is None]
    
    def get_subcategories(self, parent_name: str) -> List[CategoryData]:
        """Get subcategories of a parent category"""
        parent = self.get_category(parent_name)
        if not parent or not parent.subcategories:
            return []
        
        subcats = []
        for subcat_name in parent.subcategories:
            subcat = self.get_category(subcat_name)
            if subcat:
                subcats.append(subcat)
        
        return subcats
    
    def update_package_count(self, name: str, count: int) -> bool:
        """Update package count for category"""
        category = self.get_category(name)
        if not category:
            return False
        
        category.package_count = count
        category.last_updated = datetime.now().isoformat()
        return self.add_category(category)
    
    def clear_cache(self):
        """Clear all categories for this backend"""
        self.lmdb.clear_db(self.db_name)
    
    def is_cache_valid(self, max_age_hours: int = 24) -> bool:
        """Check if cache is still valid"""
        categories = self.get_all_categories()
        if not categories:
            return False
        
        last_updated = datetime.fromisoformat(categories[0].last_updated)
        age = datetime.now() - last_updated
        return age < timedelta(hours=max_age_hours)
