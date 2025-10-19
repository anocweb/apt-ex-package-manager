"""Category list panel controller"""
from PyQt6.QtWidgets import QTreeWidgetItem
from .base_panel import BasePanel


class CategoryListPanel(BasePanel):
    """Panel for browsing all categories"""
    
    def on_show(self):
        """Populate categories when shown"""
        self.populate_categories()
    
    def get_title(self):
        """Return panel title"""
        return "Browse Categories"
    
    def populate_categories(self):
        """Populate the category tree"""
        self.categoryTree.clear()
        
        # Get cached categories
        section_details = self.lmdb_manager.get_categories('apt') if self.lmdb_manager else {}
        
        if section_details is None:
            section_details = {}
        
        for section, data in sorted(section_details.items()):
            if isinstance(data, dict):
                total_packages = sum(data.values())
                section_item = QTreeWidgetItem([f"📁 {section} ({total_packages} packages)"])
                self.categoryTree.addTopLevelItem(section_item)
                
                for subcategory, count in sorted(data.items()):
                    subcat_item = QTreeWidgetItem([f"📄 {subcategory} ({count} packages)"])
                    section_item.addChild(subcat_item)
            else:
                section_item = QTreeWidgetItem([f"📁 {section} ({data} packages)"])
                self.categoryTree.addTopLevelItem(section_item)
        
        self.categoryTree.expandAll()
