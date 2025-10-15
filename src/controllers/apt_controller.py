from models.package_model import Package
from typing import List, Set

class APTController:
    def __init__(self):
        pass

    def install_package(self, package_name):
        # Placeholder for APT install
        return True

    def remove_package(self, package_name):
        # Placeholder for APT remove
        return True

    def search_packages(self, query):
        # Mock search results
        return [
            Package(f"package-{query}-1", "1.0", f"Sample package matching {query}"),
            Package(f"package-{query}-2", "2.0", f"Another package for {query}")
        ]

    def get_installed_packages(self):
        # Mock installed packages
        return [
            Package("firefox", "100.0", "Web browser"),
            Package("vim", "8.2", "Text editor"),
            Package("git", "2.34", "Version control")
        ]
    
    def get_categories_from_debtags(self) -> List[str]:
        """Collect categories from debtags using Python apt library"""
        try:
            import apt
            cache = apt.Cache()
            categories: Set[str] = set()
            
            for package in cache:
                if hasattr(package.candidate, 'record') and package.candidate.record:
                    # Get debtags from package record
                    debtags = package.candidate.record.get('Tag', '')
                    if debtags:
                        # Parse debtags - format is "category::subcategory, category2::subcategory2"
                        for tag in debtags.split(','):
                            tag = tag.strip()
                            if '::' in tag:
                                category = tag.split('::')[0].strip()
                                if category:
                                    categories.add(category)
            
            return sorted(list(categories))
        except ImportError:
            return []
        except Exception:
            return []
    
    def get_packages_by_category(self, category: str) -> List[Package]:
        """Get packages that belong to a specific debtag category"""
        try:
            import apt
            cache = apt.Cache()
            packages = []
            
            for package in cache:
                if hasattr(package.candidate, 'record') and package.candidate.record:
                    debtags = package.candidate.record.get('Tag', '')
                    if debtags and category in debtags:
                        # Check if category matches exactly (not just substring)
                        for tag in debtags.split(','):
                            tag = tag.strip()
                            if tag.startswith(f"{category}::"):
                                packages.append(Package(
                                    name=package.name,
                                    version=package.candidate.version if package.candidate else "unknown",
                                    description=package.candidate.summary if package.candidate else ""
                                ))
                                break
            
            return packages
        except ImportError:
            return []
        except Exception:
            return []
    
    def get_category_details(self) -> dict:
        """Get detailed category information with subcategories from debtags"""
        try:
            import apt
            cache = apt.Cache()
            category_details = {}
            
            for package in cache:
                if hasattr(package.candidate, 'record') and package.candidate.record:
                    debtags = package.candidate.record.get('Tag', '')
                    if debtags:
                        for tag in debtags.split(','):
                            tag = tag.strip()
                            if '::' in tag:
                                parts = tag.split('::', 1)
                                category = parts[0].strip()
                                subcategory = parts[1].strip()
                                
                                if category not in category_details:
                                    category_details[category] = set()
                                category_details[category].add(subcategory)
            
            # Convert sets to sorted lists
            return {cat: sorted(list(subcats)) for cat, subcats in category_details.items()}
        except ImportError:
            return {}
        except Exception:
            return {}