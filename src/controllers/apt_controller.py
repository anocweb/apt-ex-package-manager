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
    
    def get_categories_from_sections(self) -> List[str]:
        """Collect categories from APT sections"""
        try:
            import apt
            cache = apt.Cache()
            sections: Set[str] = set()
            
            for package in cache:
                if hasattr(package.candidate, 'section') and package.candidate.section:
                    sections.add(package.candidate.section)
            
            return sorted(list(sections))
        except ImportError:
            return []
        except Exception:
            return []
    
    def get_section_to_sidebar_mapping(self) -> dict:
        """Map APT sections to sidebar categories"""
        return {
            'games': ['games'],
            'graphics': ['graphics'],
            'internet': ['net', 'web', 'mail'],
            'multimedia': ['sound', 'video'],
            'office': ['editors', 'text', 'doc'],
            'development': ['devel', 'libdevel', 'python', 'perl'],
            'system': ['admin', 'base', 'kernel', 'shells'],
            'utilities': ['utils', 'misc', 'otherosfs'],
            'education': ['education', 'science'],
            'accessibility': ['accessibility'],
            'all': []  # Special case for all packages
        }
    
    def get_packages_by_sidebar_category(self, sidebar_category: str) -> List[Package]:
        """Get packages for a sidebar category by mapping to APT sections"""
        mapping = self.get_section_to_sidebar_mapping()
        apt_sections = mapping.get(sidebar_category, [])
        
        if sidebar_category == 'all':
            # Return all packages
            return self.get_installed_packages()
        
        all_packages = []
        for section in apt_sections:
            packages = self.get_packages_by_section(section)
            all_packages.extend(packages)
        
        return all_packages
    
    def get_packages_by_section(self, section: str) -> List[Package]:
        """Get packages that belong to a specific APT section"""
        try:
            import apt
            cache = apt.Cache()
            packages = []
            
            for package in cache:
                if hasattr(package.candidate, 'section') and package.candidate.section == section:
                    packages.append(Package(
                        name=package.name,
                        version=package.candidate.version if package.candidate else "unknown",
                        description=package.candidate.summary if package.candidate else ""
                    ))
            
            return packages
        except ImportError:
            return []
        except Exception:
            return []
    
    def get_section_details(self) -> dict:
        """Get section information parsed into hierarchical categories"""
        try:
            import apt
            cache = apt.Cache()
            section_details = {}
            
            for package in cache:
                if hasattr(package.candidate, 'section') and package.candidate.section:
                    section = package.candidate.section
                    
                    if '/' in section:
                        # Parse hierarchical sections like "games/action"
                        parts = section.split('/', 1)
                        main_category = parts[0]
                        subcategory = parts[1]
                        
                        if main_category not in section_details:
                            section_details[main_category] = {}
                        if subcategory not in section_details[main_category]:
                            section_details[main_category][subcategory] = 0
                        section_details[main_category][subcategory] += 1
                    else:
                        # Flat section
                        if section not in section_details:
                            section_details[section] = 0
                        section_details[section] += 1
            
            return section_details
        except ImportError:
            return {}
        except Exception:
            return {}