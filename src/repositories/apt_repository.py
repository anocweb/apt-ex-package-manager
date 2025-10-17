import subprocess
from typing import List
from .base_repository import BaseRepository, RepositorySource
from cache.category_cache import CategoryCache

class AptRepository(BaseRepository):
    """APT repository implementation"""
    
    @property
    def name(self) -> str:
        return 'apt'
    
    @property
    def display_name(self) -> str:
        return 'APT'
    
    @property
    def is_available(self) -> bool:
        try:
            import apt
            return True
        except ImportError:
            return False
    
    def get_sources(self) -> List[RepositorySource]:
        """Get all APT repository sources"""
        if not self.is_available:
            return []
        
        try:
            import apt
            sources = []
            source_list = apt.SourcesList()
            
            for source in source_list:
                if source.type == 'deb':  # Only include binary repositories
                    sources.append(RepositorySource(
                        name=f"{source.uri} - {source.dist}",
                        url=source.uri,
                        enabled=not source.disabled,
                        scope='system',
                        source_type='apt',
                        dist=source.dist,
                        comps=source.comps,
                        file=source.file,
                        comment=source.comment
                    ))
            
            return sources
        except Exception:
            return self._fallback_get_sources()
    
    def _fallback_get_sources(self) -> List[RepositorySource]:
        """Fallback method using apt-cache policy"""
        try:
            # Safe: hardcoded command with no user input
            result = subprocess.run(['apt-cache', 'policy'], 
                                  capture_output=True, text=True, check=True)
            sources = []
            
            for line in result.stdout.split('\n'):
                if line.strip().startswith('http'):
                    url = line.strip().split()[0]
                    sources.append(RepositorySource(
                        name=url,
                        url=url,
                        enabled=True,
                        scope='system',
                        source_type='apt'
                    ))
            
            return sources
        except subprocess.CalledProcessError:
            return []
    
    def add_source(self, name: str, url: str, scope: str = 'system') -> bool:
        """Add APT source (requires elevated privileges)"""
        return False  # Not implemented - requires complex PPA handling
    
    def remove_source(self, name: str, scope: str = 'system') -> bool:
        """Remove APT source (requires elevated privileges)"""
        return False  # Not implemented - requires file modification
    
    def enable_source(self, name: str, scope: str = 'system') -> bool:
        """Enable APT source (requires elevated privileges)"""
        return False  # Not implemented - requires file modification
    
    def disable_source(self, name: str, scope: str = 'system') -> bool:
        """Disable APT source (requires elevated privileges)"""
        return False  # Not implemented - requires file modification
    
    def can_add_sources(self) -> bool:
        return False  # Requires elevated privileges
    
    def can_remove_sources(self) -> bool:
        return False  # Requires elevated privileges
    
    def can_toggle_sources(self) -> bool:
        return False  # Requires elevated privileges
    
    def supports_user_scope(self) -> bool:
        return False
    
    def supports_system_scope(self) -> bool:
        return True
    
    def get_categories(self):
        """Get package categories from sections"""
        if not self.is_available:
            return {}
        
        from ..controllers.apt_controller import APTController
        apt_controller = APTController()
        return apt_controller.get_section_details()
    
    def _collect_apt_sections(self) -> List[str]:
        """Collect categories from APT sections"""
        try:
            import apt
            cache = apt.Cache()
            sections = set()
            
            for package in cache:
                if hasattr(package.candidate, 'section') and package.candidate.section:
                    sections.add(package.candidate.section)
            
            return sorted(list(sections))
        except Exception:
            return []