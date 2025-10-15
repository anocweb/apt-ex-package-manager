from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class RepositorySource:
    """Unified repository source representation"""
    def __init__(self, name: str, url: str, enabled: bool = True, 
                 scope: str = 'system', source_type: str = 'unknown', **kwargs):
        self.name = name
        self.url = url
        self.enabled = enabled
        self.scope = scope
        self.source_type = source_type
        self.metadata = kwargs

class BaseRepository(ABC):
    """Base class for repository implementations"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Repository system name (e.g., 'apt', 'flatpak')"""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for UI"""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this repository system is available on the system"""
        pass
    
    @abstractmethod
    def get_sources(self) -> List[RepositorySource]:
        """Get all repository sources"""
        pass
    
    @abstractmethod
    def add_source(self, name: str, url: str, scope: str = 'user') -> bool:
        """Add a new repository source"""
        pass
    
    @abstractmethod
    def remove_source(self, name: str, scope: str = 'user') -> bool:
        """Remove a repository source"""
        pass
    
    @abstractmethod
    def enable_source(self, name: str, scope: str = 'user') -> bool:
        """Enable a repository source"""
        pass
    
    @abstractmethod
    def disable_source(self, name: str, scope: str = 'user') -> bool:
        """Disable a repository source"""
        pass
    
    def can_add_sources(self) -> bool:
        """Whether this repository type supports adding sources"""
        return True
    
    def can_remove_sources(self) -> bool:
        """Whether this repository type supports removing sources"""
        return True
    
    def can_toggle_sources(self) -> bool:
        """Whether this repository type supports enabling/disabling sources"""
        return True
    
    def supports_user_scope(self) -> bool:
        """Whether this repository type supports user-level sources"""
        return False
    
    def supports_system_scope(self) -> bool:
        """Whether this repository type supports system-level sources"""
        return True