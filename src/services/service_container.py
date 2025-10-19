from typing import Any, Optional

class ServiceContainer:
    """Centralized service registry for dependency injection"""
    
    def __init__(self):
        self._services = {}
    
    def register(self, name: str, service: Any) -> None:
        """Register a service with a name"""
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        """Get a service by name"""
        if name not in self._services:
            raise KeyError(f"Service '{name}' not found in container")
        return self._services[name]
    
    def has(self, name: str) -> bool:
        """Check if a service exists"""
        return name in self._services
    
    def get_optional(self, name: str) -> Optional[Any]:
        """Get a service by name, return None if not found"""
        return self._services.get(name)
    
    def clear(self) -> None:
        """Clear all services"""
        self._services.clear()
