from typing import List, Optional
from dataclasses import dataclass
from cache import LMDBManager, CategoryCacheModel
from cache.data_structures import CategoryData

@dataclass
class Category:
    """Category data model"""
    name: str
    backend: str = "apt"
    parent: Optional[str] = None
    package_count: int = 0
    last_updated: Optional[str] = None

class CategoryModel:
    """CRUD operations for category cache"""
    
    def __init__(self, lmdb_manager: LMDBManager, backend: str = 'apt'):
        self.cache = CategoryCacheModel(lmdb_manager, backend)
        self.backend = backend
    
    def create(self, category: Category) -> bool:
        """Create a new category"""
        cat_data = CategoryData(
            name=category.name,
            parent=category.parent,
            package_count=category.package_count
        )
        return self.cache.add_category(cat_data)
    
    def read(self, name: str) -> Optional[Category]:
        """Read a category by name"""
        cat_data = self.cache.get_category(name)
        if cat_data:
            return Category(
                name=cat_data.name,
                backend=self.backend,
                parent=cat_data.parent,
                package_count=cat_data.package_count,
                last_updated=cat_data.last_updated
            )
        return None
    
    def update(self, category: Category) -> bool:
        """Update an existing category"""
        cat_data = CategoryData(
            name=category.name,
            parent=category.parent,
            package_count=category.package_count
        )
        return self.cache.add_category(cat_data)
    
    def delete(self, name: str) -> bool:
        """Delete a category"""
        return self.cache.delete_category(name)
    
    def get_by_backend(self, backend: str) -> List[Category]:
        """Get all categories for a backend"""
        cat_list = self.cache.get_all_categories()
        return [Category(
            name=cat.name,
            backend=backend,
            parent=cat.parent,
            package_count=cat.package_count,
            last_updated=cat.last_updated
        ) for cat in cat_list]
    
    def get_root_categories(self, backend: str) -> List[Category]:
        """Get root categories (no parent) for a backend"""
        cat_list = self.cache.get_root_categories()
        return [Category(
            name=cat.name,
            backend=backend,
            parent=cat.parent,
            package_count=cat.package_count,
            last_updated=cat.last_updated
        ) for cat in cat_list]
