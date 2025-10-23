"""Version parsing and comparison utilities"""
import re
from typing import Optional, Tuple

class VersionChecker:
    @staticmethod
    def parse_version(version_str: str) -> Tuple[int, ...]:
        """Parse version string into tuple of integers"""
        if not version_str:
            return (0,)
        
        # Extract numeric parts
        parts = re.findall(r'\d+', str(version_str))
        return tuple(int(p) for p in parts) if parts else (0,)
    
    @staticmethod
    def compare_versions(version1: str, version2: str) -> int:
        """Compare two versions. Returns: -1 (v1<v2), 0 (equal), 1 (v1>v2)"""
        v1 = VersionChecker.parse_version(version1)
        v2 = VersionChecker.parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        return 0
    
    @staticmethod
    def check_constraint(installed: str, constraint: str) -> bool:
        """Check if installed version satisfies constraint (e.g., '>=2.0.0')"""
        if not constraint or not installed:
            return True
        
        # Parse constraint
        match = re.match(r'([><=!~]+)(.+)', constraint.strip())
        if not match:
            return True
        
        operator, required = match.groups()
        cmp = VersionChecker.compare_versions(installed, required)
        
        if operator == '>=':
            return cmp >= 0
        elif operator == '>':
            return cmp > 0
        elif operator == '<=':
            return cmp <= 0
        elif operator == '<':
            return cmp < 0
        elif operator == '==':
            return cmp == 0
        elif operator == '!=':
            return cmp != 0
        
        return True
    
    @staticmethod
    def parse_pip_spec(spec: str) -> Tuple[str, Optional[str]]:
        """Parse pip-style spec like 'package>=1.0.0' into (package, constraint)"""
        match = re.match(r'([a-zA-Z0-9_-]+)([><=!~].*)?', spec.strip())
        if match:
            package, constraint = match.groups()
            return package, constraint
        return spec.strip(), None
