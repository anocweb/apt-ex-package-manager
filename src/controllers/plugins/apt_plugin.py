from controllers.base_controller import BasePackageController
from models.package_model import Package
from typing import List, Set, Dict, Optional
from utils.apt_lock import APTLock

class APTPlugin(BasePackageController):
    """APT package management backend plugin"""
    
    def __init__(self, lmdb_manager=None, logging_service=None):
        self.lmdb_manager = lmdb_manager
        self.logger = logging_service.get_logger('apt') if logging_service else None
        self._apt_lock = None
    
    @property
    def backend_id(self) -> str:
        return 'apt'
    
    @property
    def display_name(self) -> str:
        return 'APT Packages'
    
    def is_available(self) -> bool:
        """Check if APT is available on system"""
        try:
            import apt
            return True
        except ImportError:
            return False
    
    def get_capabilities(self) -> Set[str]:
        return {'search', 'install', 'remove', 'list_installed', 'list_updates', 'categories'}
    
    def log(self, message):
        """Log message if logger is available"""
        if self.logger:
            self.logger.info(message)

    def install_package(self, package_name):
        if self.logger:
            self.logger.debug(f"APT install function called for {package_name}")
        
        try:
            import apt
            import subprocess
            
            cache = apt.Cache()
            if package_name not in cache:
                self.log(f"Package {package_name} not found")
                return False
            
            package = cache[package_name]
            if package.is_installed:
                self.log(f"Package {package_name} is already installed")
                return True
            
            # Use pkexec to run apt-get install with GUI password prompt
            cmd = ['pkexec', 'apt-get', 'install', '-y', package_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log(f"Successfully installed {package_name}")
                # Update cache
                if self.lmdb_manager:
                    from cache import PackageCacheModel
                    pkg_cache = PackageCacheModel(self.lmdb_manager, 'apt')
                    pkg_cache.update_installed_status(package_name, True)
                return True
            else:
                self.log(f"Failed to install {package_name}: {result.stderr}")
                return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error installing {package_name}: {e}")
            return False

    def remove_package(self, package_name):
        if self.logger:
            self.logger.debug(f"APT remove function called for {package_name}")
        
        try:
            import apt
            import subprocess
            
            cache = apt.Cache()
            if package_name not in cache:
                self.log(f"Package {package_name} not found")
                return False
            
            package = cache[package_name]
            if not package.is_installed:
                self.log(f"Package {package_name} is not installed")
                return True
            
            # Use pkexec to run apt-get remove with GUI password prompt
            cmd = ['pkexec', 'apt-get', 'remove', '-y', package_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log(f"Successfully removed {package_name}")
                # Update cache
                if self.lmdb_manager:
                    from cache import PackageCacheModel
                    pkg_cache = PackageCacheModel(self.lmdb_manager, 'apt')
                    pkg_cache.update_installed_status(package_name, False)
                return True
            else:
                self.log(f"Failed to remove {package_name}: {result.stderr}")
                return False
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error removing {package_name}: {e}")
            return False

    def search_packages(self, query):
        if self.logger:
            self.logger.debug(f"APT search function called with query: {query}")
        return [
            Package(f"package-{query}-1", "1.0", f"Sample package matching {query}", "apt"),
            Package(f"package-{query}-2", "2.0", f"Another package for {query}", "apt")
        ]

    def get_installed_packages(self, limit: int = None, offset: int = 0):
        if self.logger:
            self.logger.debug("Getting installed packages from APT")
        try:
            import apt
            cache = apt.Cache()
            packages = []
            
            for package in cache:
                if package.is_installed:
                    packages.append(Package(
                        name=package.name,
                        version=package.installed.version,
                        description=package.installed.summary if hasattr(package.installed, 'summary') else "",
                        backend="apt"
                    ))
            
            # Apply pagination
            if limit:
                return packages[offset:offset+limit]
            return packages[offset:]
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting installed packages: {e}")
            return []
    
    def get_installed_packages_list(self, lmdb_manager, limit: int = None, offset: int = 0) -> List[dict]:
        """Get list of installed packages with minimal info for display"""
        try:
            from cache import PackageCacheModel
            pkg_cache = PackageCacheModel(lmdb_manager, 'apt')
            packages = pkg_cache.get_installed_packages()
            
            if limit:
                packages = packages[offset:offset+limit]
            
            return [{
                'name': pkg.name,
                'version': pkg.version,
                'description': pkg.summary or pkg.description
            } for pkg in packages]
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading installed packages: {e}")
            return []
    
    def update_installed_status(self, lmdb_manager):
        """Update is_installed flag for all packages in cache"""
        self.log("Updating installed package status")
        try:
            import apt
            cache = apt.Cache()
            
            installed_names = set()
            for package in cache:
                if package.is_installed:
                    installed_names.add(package.name)
            
            self.log(f"Found {len(installed_names)} installed packages")
            
            from cache import PackageCacheModel
            pkg_cache = PackageCacheModel(lmdb_manager, 'apt')
            all_packages = pkg_cache.get_all_packages()
            
            for pkg in all_packages:
                is_installed = pkg.name in installed_names
                if pkg.is_installed != is_installed:
                    pkg_cache.update_installed_status(pkg.package_id, is_installed)
            
            self.log("Installed status updated")
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error updating installed status: {e}")
            return False
    
    def get_categories(self) -> List[str]:
        """Collect categories from APT sections"""
        try:
            import apt
            cache = apt.Cache()
            sections: Set[str] = set()
            
            for package in cache:
                if hasattr(package.candidate, 'section') and package.candidate.section:
                    sections.add(package.candidate.section)
            
            return sorted(list(sections))
        except:
            return []
    
    def get_sidebar_category_mapping(self) -> Dict[str, List[str]]:
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
            'accessibility': [],
            'all': []
        }
    
    def get_packages_by_category(self, sidebar_category: str) -> List[Package]:
        """Get packages for a sidebar category by mapping to APT sections"""
        mapping = self.get_sidebar_category_mapping()
        apt_sections = mapping.get(sidebar_category, [])
        
        if sidebar_category == 'all':
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
                if hasattr(package.candidate, 'section') and package.candidate.section:
                    pkg_section = package.candidate.section
                    if pkg_section == section or pkg_section.startswith(section + '/'):
                        packages.append(Package(
                            name=package.name,
                            version=package.candidate.version if package.candidate else "unknown",
                            description=package.candidate.summary if package.candidate else "",
                            backend="apt"
                        ))
            
            return packages
        except:
            return []
    
    def get_section_details(self) -> dict:
        """Get section information parsed into hierarchical categories"""
        self.log("Loading APT section details")
        try:
            import apt
            cache = apt.Cache()
            section_details = {}
            
            for package in cache:
                if hasattr(package.candidate, 'section') and package.candidate.section:
                    section = package.candidate.section
                    
                    if '/' in section:
                        parts = section.split('/', 1)
                        main_category = parts[0]
                        subcategory = parts[1]
                        
                        if main_category not in section_details:
                            section_details[main_category] = {}
                        if subcategory not in section_details[main_category]:
                            section_details[main_category][subcategory] = 0
                        section_details[main_category][subcategory] += 1
                    else:
                        if section not in section_details:
                            section_details[section] = 0
                        section_details[section] += 1
            
            self.log(f"Loaded {len(section_details)} APT sections")
            return section_details
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading APT sections: {e}")
            return {}
    
    def get_upgradable_packages(self) -> List[dict]:
        """Get list of packages with available updates"""
        self.log("Checking for package updates")
        try:
            import apt
            cache = apt.Cache()
            cache.open()
            cache.upgrade()
            
            updates = []
            for package in cache.get_changes():
                if package.marked_upgrade or package.marked_install:
                    update_info = {
                        'name': package.name,
                        'description': package.candidate.summary if package.candidate else '',
                        'current_version': package.installed.version if package.installed else 'Not installed',
                        'new_version': package.candidate.version if package.candidate else 'Unknown',
                        'is_security': self._is_security_update(package),
                        'backend': 'apt'
                    }
                    updates.append(update_info)
            
            self.log(f"Found {len(updates)} available updates")
            return updates
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking for updates: {e}")
            return []
    
    def _is_security_update(self, package) -> bool:
        """Check if package update is a security update"""
        try:
            if not package.candidate:
                return False
            
            for origin in package.candidate.origins:
                if 'security' in origin.archive.lower() or 'security' in origin.label.lower():
                    return True
            
            return False
        except:
            return False
    
    def get_package_details(self, package_name: str) -> Optional[Dict]:
        """Get detailed information for a specific package"""
        try:
            import apt
            cache = apt.Cache()
            
            if package_name not in cache:
                return None
            
            package = cache[package_name]
            candidate = package.candidate or package.installed
            
            if not candidate:
                return None
            
            details = {
                'backend': 'apt',
                'name': package.name,
                'version': candidate.version,
                'description': candidate.description or '',
                'summary': candidate.summary or '',
                'section': candidate.section or '',
                'architecture': candidate.architecture or '',
                'installed_size': getattr(candidate, 'installed_size', 0),
                'size': getattr(candidate, 'size', 0),
                'installed': package.is_installed
            }
            
            if hasattr(candidate, 'record') and candidate.record:
                record = candidate.record
                details['homepage'] = record.get('Homepage', '')
                details['maintainer'] = record.get('Maintainer', '')
                details['priority'] = record.get('Priority', '')
                details['source'] = record.get('Source', '')
                details['depends'] = record.get('Depends', '')
                details['recommends'] = record.get('Recommends', '')
                details['license'] = record.get('License', '')
            
            return details
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting package details for {package_name}: {e}")
            return None
    
    def get_all_packages_for_cache(self) -> List[Dict]:
        """Get all package details for caching"""
        self.log("Loading all APT packages for cache")
        try:
            import apt
            cache = apt.Cache()
            packages = []
            
            for package in cache:
                if package.candidate:
                    pkg_data = {
                        'backend': 'apt',
                        'package_id': package.name,
                        'name': package.name,
                        'version': package.candidate.version,
                        'description': package.candidate.description or '',
                        'summary': package.candidate.summary or '',
                        'section': package.candidate.section or '',
                        'architecture': package.candidate.architecture or '',
                        'size': getattr(package.candidate, 'size', 0),
                        'installed_size': getattr(package.candidate, 'installed_size', 0),
                        'maintainer': getattr(package.candidate.record, 'get', lambda x, y: '')('Maintainer', ''),
                        'homepage': getattr(package.candidate.record, 'get', lambda x, y: '')('Homepage', ''),
                        'metadata': {}
                    }
                    
                    if hasattr(package.candidate, 'record') and package.candidate.record:
                        record = package.candidate.record
                        if 'Depends' in record:
                            pkg_data['metadata']['depends'] = record['Depends']
                        if 'Conflicts' in record:
                            pkg_data['metadata']['conflicts'] = record['Conflicts']
                        if 'Priority' in record:
                            pkg_data['metadata']['priority'] = record['Priority']
                    
                    packages.append(pkg_data)
            
            self.log(f"Loaded {len(packages)} APT packages")
            return packages
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading APT packages: {e}")
            return []
