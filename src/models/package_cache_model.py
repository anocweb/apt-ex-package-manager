from dataclasses import dataclass
from typing import Optional

@dataclass
class PackageSummary:
    """Lightweight package summary for category display"""
    name: str
    description: str
    backend: str
    rating: Optional[float] = None
    review_count: Optional[int] = None

# Alias for compatibility
PackageCache = PackageSummary
