from typing import List
from .base_repository import BaseRepository, RepositorySource

class AppImageRepository(BaseRepository):
    """AppImage repository implementation"""
    
    @property
    def name(self) -> str:
        return 'appimage'
    
    @property
    def display_name(self) -> str:
        return 'AppImage'
    
    @property
    def is_available(self) -> bool:
        # AppImage doesn't require system installation
        return True
    
    def get_sources(self) -> List[RepositorySource]:
        """Get AppImage sources (placeholder - no standard repository system)"""
        # AppImage doesn't have a standard repository system
        # This could be extended to support AppImageHub or custom catalogs
        return []
    
    def add_source(self, name: str, url: str, scope: str = 'user') -> bool:
        """Add AppImage source (not implemented)"""
        # Could be implemented to support custom AppImage catalogs
        return False
    
    def remove_source(self, name: str, scope: str = 'user') -> bool:
        """Remove AppImage source (not implemented)"""
        return False
    
    def enable_source(self, name: str, scope: str = 'user') -> bool:
        """Enable AppImage source (not implemented)"""
        return False
    
    def disable_source(self, name: str, scope: str = 'user') -> bool:
        """Disable AppImage source (not implemented)"""
        return False
    
    def can_add_sources(self) -> bool:
        return False  # No standard repository system
    
    def can_remove_sources(self) -> bool:
        return False
    
    def can_toggle_sources(self) -> bool:
        return False
    
    def supports_user_scope(self) -> bool:
        return True
    
    def supports_system_scope(self) -> bool:
        return False