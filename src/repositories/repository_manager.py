from typing import List, Dict, Optional
from .base_repository import BaseRepository, RepositorySource
from .apt_repository import AptRepository
from .flatpak_repository import FlatpakRepository
from .appimage_repository import AppImageRepository

class RepositoryManager:
    """Manages all repository implementations"""
    
    def __init__(self):
        self._repositories: Dict[str, BaseRepository] = {}
        self._load_repositories()
    
    def _load_repositories(self):
        """Load all available repository implementations"""
        # Register repository implementations
        repositories = [
            AptRepository(),
            FlatpakRepository(),
            AppImageRepository()
        ]
        
        # Only include available repositories
        for repo in repositories:
            if repo.is_available:
                self._repositories[repo.name] = repo
    
    def get_available_repositories(self) -> List[BaseRepository]:
        """Get all available repository implementations"""
        return list(self._repositories.values())
    
    def get_repository(self, name: str) -> Optional[BaseRepository]:
        """Get specific repository implementation"""
        return self._repositories.get(name)
    
    def get_all_sources(self) -> Dict[str, List[RepositorySource]]:
        """Get sources from all repositories"""
        all_sources = {}
        
        for repo_name, repo in self._repositories.items():
            try:
                sources = repo.get_sources()
                all_sources[repo_name] = sources
            except Exception:
                all_sources[repo_name] = []
        
        return all_sources
    
    def get_sources_for_repository(self, repo_name: str) -> List[RepositorySource]:
        """Get sources for specific repository"""
        repo = self.get_repository(repo_name)
        if repo:
            try:
                return repo.get_sources()
            except Exception:
                return []
        return []
    
    def add_source(self, repo_name: str, name: str, url: str, scope: str = 'user') -> bool:
        """Add source to specific repository"""
        repo = self.get_repository(repo_name)
        if repo and repo.can_add_sources():
            return repo.add_source(name, url, scope)
        return False
    
    def remove_source(self, repo_name: str, name: str, scope: str = 'user') -> bool:
        """Remove source from specific repository"""
        repo = self.get_repository(repo_name)
        if repo and repo.can_remove_sources():
            return repo.remove_source(name, scope)
        return False
    
    def enable_source(self, repo_name: str, name: str, scope: str = 'user') -> bool:
        """Enable source in specific repository"""
        repo = self.get_repository(repo_name)
        if repo and repo.can_toggle_sources():
            return repo.enable_source(name, scope)
        return False
    
    def disable_source(self, repo_name: str, name: str, scope: str = 'user') -> bool:
        """Disable source in specific repository"""
        repo = self.get_repository(repo_name)
        if repo and repo.can_toggle_sources():
            return repo.disable_source(name, scope)
        return False
    
    def is_repository_available(self, repo_name: str) -> bool:
        """Check if repository is available"""
        return repo_name in self._repositories
    
    def get_repository_capabilities(self, repo_name: str) -> Dict[str, bool]:
        """Get capabilities of specific repository"""
        repo = self.get_repository(repo_name)
        if repo:
            return {
                'can_add_sources': repo.can_add_sources(),
                'can_remove_sources': repo.can_remove_sources(),
                'can_toggle_sources': repo.can_toggle_sources(),
                'supports_user_scope': repo.supports_user_scope(),
                'supports_system_scope': repo.supports_system_scope()
            }
        return {}
    
    def refresh_all(self):
        """Refresh all repository data"""
        # Repository data is fetched fresh each time get_sources() is called
        # This method can be extended for caching if needed
        pass