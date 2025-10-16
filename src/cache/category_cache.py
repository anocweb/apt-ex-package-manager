from typing import Dict, List, Optional
from models.category_model import CategoryModel, Category

class CategoryCache:
    """Model-based cache system for package categories from different packaging systems"""
    
    def __init__(self, logger=None):
        self.model = CategoryModel()
        self.logger = logger
    
    def log(self, message):
        """Log message if logger is available"""
        if self.logger:
            self.logger.info(message)
    
    def get_categories(self, system: str) -> Optional[Dict]:
        """Get cached categories for packaging system"""
        if hasattr(self, 'logger') and self.logger:
            self.logger.debug(f"Getting categories for {system}")
        if not self.is_cache_valid(system):
            self.log(f"Category cache expired for {system}")
            return None
        
        categories = self.model.get_by_backend(system)
        if not categories:
            self.log(f"No cached categories found for {system}")
            return None
        
        self.log(f"Retrieved {len(categories)} cached categories for {system}")
        
        # Convert to hierarchical dict structure
        result = {}
        category_map = {cat.id: cat for cat in categories}
        
        for category in categories:
            if category.parent_id is None:
                # Root category
                result[category.name] = category.package_count
            else:
                # Child category
                parent = category_map.get(category.parent_id)
                if parent:
                    if parent.name not in result or not isinstance(result[parent.name], dict):
                        result[parent.name] = {}
                    result[parent.name][category.name] = category.package_count
        
        return result
    
    def set_categories(self, system: str, categories: Dict):
        """Cache categories for packaging system"""
        if hasattr(self, 'logger') and self.logger:
            self.logger.debug(f"Setting categories for {system}")
        self.log(f"Caching {len(categories)} categories for {system}")
        # Clear existing categories for this system
        self.clear_cache(system)
        
        # Insert new categories
        for category_name, data in categories.items():
            if isinstance(data, dict):
                # Create parent category
                parent = Category(
                    backend=system,
                    name=category_name,
                    package_count=sum(data.values())
                )
                parent_id = self.model.create(parent)
                
                # Create child categories
                for child_name, count in data.items():
                    child = Category(
                        backend=system,
                        name=child_name,
                        parent_id=parent_id,
                        package_count=count
                    )
                    self.model.create(child)
            else:
                # Flat category
                category = Category(
                    backend=system,
                    name=category_name,
                    package_count=data
                )
                self.model.create(category)
    
    def clear_cache(self, system: Optional[str] = None):
        """Clear cache for specific system or all systems"""
        if hasattr(self, 'logger') and self.logger:
            self.logger.debug(f"Clearing cache for {system or 'all systems'}")
        if system:
            categories = self.model.get_by_backend(system)
            count = len([c for c in categories if c.parent_id is None])
            for category in categories:
                if category.parent_id is None:  # Only delete roots, children cascade
                    self.model.delete(category.id)
            self.log(f"Cleared {count} cached categories for {system}")
        else:
            # Clear all - delete all root categories (children cascade)
            import sqlite3
            with sqlite3.connect(self.model.db.db_path) as conn:
                conn.execute('DELETE FROM category_cache WHERE parent_id IS NULL')
                conn.commit()
            self.log("Cleared all cached categories")
    
    def is_cache_valid(self, system: str, max_age_hours: int = 24) -> bool:
        """Check if cache is still valid"""
        return self.model.db.is_cache_valid(system, max_age_hours)