import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

class CategoryCache:
    """Cache system for package categories from different packaging systems"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
    
    def _get_cache_file(self, system: str) -> Path:
        """Get cache file path for specific packaging system"""
        return self.cache_dir / f".{system}-categories"
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache file is still valid"""
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                cache_time = datetime.fromisoformat(data.get('timestamp', ''))
                return datetime.now() - cache_time < self.cache_duration
        except (json.JSONDecodeError, ValueError, KeyError):
            return False
    
    def get_categories(self, system: str) -> Optional[List[str]]:
        """Get cached categories for packaging system"""
        cache_file = self._get_cache_file(system)
        
        if not self._is_cache_valid(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return data.get('categories', [])
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def set_categories(self, system: str, categories: List[str]):
        """Cache categories for packaging system"""
        cache_file = self._get_cache_file(system)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'categories': sorted(categories),
            'system': system
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass  # Fail silently if can't write cache
    
    def clear_cache(self, system: Optional[str] = None):
        """Clear cache for specific system or all systems"""
        if system:
            cache_file = self._get_cache_file(system)
            if cache_file.exists():
                cache_file.unlink()
        else:
            # Clear all cache files
            for cache_file in self.cache_dir.glob(".*-categories"):
                cache_file.unlink()
    
    def get_all_cached_systems(self) -> List[str]:
        """Get list of all systems with cached categories"""
        systems = []
        for cache_file in self.cache_dir.glob(".*-categories"):
            system = cache_file.name[1:-11]  # Remove leading dot and "-categories"
            if self._is_cache_valid(cache_file):
                systems.append(system)
        return systems
    
    def get_cache_info(self, system: str) -> Optional[Dict]:
        """Get cache information for system"""
        cache_file = self._get_cache_file(system)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return {
                    'system': system,
                    'timestamp': data.get('timestamp'),
                    'category_count': len(data.get('categories', [])),
                    'valid': self._is_cache_valid(cache_file)
                }
        except (json.JSONDecodeError, FileNotFoundError):
            return None