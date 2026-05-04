"""
Providers package - API provider management
"""

from typing import Optional, Dict, Any


class ProviderRegistry:
    """Registry for API providers"""

    def __init__(self):
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.active_provider: Optional[str] = None

    def register_provider(self, name: str, config: Dict[str, Any]):
        """Register an API provider"""
        self.providers[name] = config
        if self.active_provider is None:
            self.active_provider = name

    def get_provider(self, name: str) -> Optional[Dict[str, Any]]:
        """Get provider configuration"""
        return self.providers.get(name)

    def set_active(self, name: str) -> bool:
        """Set active provider"""
        if name in self.providers:
            self.active_provider = name
            return True
        return False

    def get_active(self) -> Optional[Dict[str, Any]]:
        """Get active provider configuration"""
        if self.active_provider:
            return self.providers.get(self.active_provider)
        return None


registry = ProviderRegistry()
