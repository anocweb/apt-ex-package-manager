from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime

@dataclass
class PackageData:
    """Package data structure for LMDB storage"""
    package_id: str
    name: str
    version: str
    description: str
    summary: Optional[str] = None
    section: Optional[str] = None
    architecture: Optional[str] = None
    size: Optional[int] = None
    installed_size: Optional[int] = None
    maintainer: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    source_url: Optional[str] = None
    icon_url: Optional[str] = None
    is_installed: bool = False
    metadata: Optional[Dict[str, Any]] = None
    last_updated: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if self.last_updated is None:
            data['last_updated'] = datetime.now().isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PackageData':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class CategoryData:
    """Category data structure for LMDB storage"""
    name: str
    parent: Optional[str] = None
    package_count: int = 0
    subcategories: Optional[List[str]] = None
    last_updated: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if self.last_updated is None:
            data['last_updated'] = datetime.now().isoformat()
        if self.subcategories is None:
            data['subcategories'] = []
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CategoryData':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class IndexData:
    """Index data structure for LMDB storage"""
    index_type: str  # 'name', 'section', 'installed'
    value: str
    package_ids: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndexData':
        """Create from dictionary"""
        return cls(**data)
    
    @property
    def key(self) -> str:
        """Generate index key"""
        return f"{self.index_type}:{self.value}"


@dataclass
class MetadataEntry:
    """Metadata entry for cache management"""
    key: str
    value: Any
    last_updated: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        if self.last_updated is None:
            data['last_updated'] = datetime.now().isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetadataEntry':
        """Create from dictionary"""
        return cls(**data)
