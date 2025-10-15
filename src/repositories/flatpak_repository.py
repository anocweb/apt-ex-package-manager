import subprocess
from typing import List
from .base_repository import BaseRepository, RepositorySource

class FlatpakRepository(BaseRepository):
    """Flatpak repository implementation"""
    
    @property
    def name(self) -> str:
        return 'flatpak'
    
    @property
    def display_name(self) -> str:
        return 'Flatpak'
    
    @property
    def is_available(self) -> bool:
        try:
            subprocess.run(['flatpak', '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_sources(self) -> List[RepositorySource]:
        """Get all Flatpak repository sources"""
        if not self.is_available:
            return []
        
        sources = []
        sources.extend(self._get_sources_for_scope('user'))
        sources.extend(self._get_sources_for_scope('system'))
        return sources
    
    def _get_sources_for_scope(self, scope: str) -> List[RepositorySource]:
        """Get Flatpak sources for specific scope"""
        try:
            result = subprocess.run([
                'flatpak', 'remotes', f'--{scope}', '--show-details'
            ], capture_output=True, text=True, check=True)
            
            return self._parse_remotes(result.stdout, scope)
        except subprocess.CalledProcessError:
            return []
    
    def _parse_remotes(self, output: str, scope: str) -> List[RepositorySource]:
        """Parse flatpak remotes output"""
        sources = []
        current_remote = {}
        
        for line in output.strip().split('\n'):
            if not line:
                continue
                
            if not line.startswith(' '):
                # New remote name
                if current_remote:
                    sources.append(self._create_source_from_remote(current_remote, scope))
                current_remote = {'name': line.strip()}
            else:
                # Remote details
                parts = line.strip().split(': ', 1)
                if len(parts) == 2:
                    key, value = parts
                    current_remote[key.lower().replace(' ', '_')] = value
        
        if current_remote:
            sources.append(self._create_source_from_remote(current_remote, scope))
        
        return sources
    
    def _create_source_from_remote(self, remote: dict, scope: str) -> RepositorySource:
        """Create RepositorySource from remote data"""
        return RepositorySource(
            name=remote.get('name', 'Unknown'),
            url=remote.get('url', ''),
            enabled=remote.get('disabled', '').lower() != 'yes',
            scope=scope,
            source_type='flatpak',
            title=remote.get('title', ''),
            description=remote.get('description', ''),
            homepage=remote.get('homepage', ''),
            icon=remote.get('icon', '')
        )
    
    def add_source(self, name: str, url: str, scope: str = 'user') -> bool:
        """Add Flatpak remote"""
        try:
            subprocess.run([
                'flatpak', 'remote-add', f'--{scope}', name, url
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def remove_source(self, name: str, scope: str = 'user') -> bool:
        """Remove Flatpak remote"""
        try:
            subprocess.run([
                'flatpak', 'remote-delete', f'--{scope}', name
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def enable_source(self, name: str, scope: str = 'user') -> bool:
        """Enable Flatpak remote"""
        try:
            subprocess.run([
                'flatpak', 'remote-modify', f'--{scope}', '--enable', name
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def disable_source(self, name: str, scope: str = 'user') -> bool:
        """Disable Flatpak remote"""
        try:
            subprocess.run([
                'flatpak', 'remote-modify', f'--{scope}', '--disable', name
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def supports_user_scope(self) -> bool:
        return True
    
    def supports_system_scope(self) -> bool:
        return True