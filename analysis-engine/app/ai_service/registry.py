"""AI Provider Registry module.

Implements a thread-safe registry to map AIProvider enum types to their concrete
AIProviderClient client implementations.
"""

import threading
from typing import Dict, List, Union

from app.ai_service.enums import AIProvider
from app.ai_service.exceptions import AIProviderError
from app.ai_service.provider import AIProviderClient


class AIProviderRegistry:
    """Thread-safe registry for registering and resolving AIProviderClient implementations."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._providers: Dict[AIProvider, AIProviderClient] = {}

    def register(self, provider: Union[AIProvider, str], client: AIProviderClient) -> None:
        """Registers a client implementation under the specified provider.

        Raises AIProviderError if a client is already registered for this provider.
        """
        prov = AIProvider(provider) if isinstance(provider, str) else provider
        with self._lock:
            if prov in self._providers:
                raise AIProviderError(f"AI Provider '{prov.value}' is already registered.")
            self._providers[prov] = client

    def unregister(self, provider: Union[AIProvider, str]) -> None:
        """Removes a registered provider client from the registry.

        Raises AIProviderError if the provider is not currently registered.
        """
        prov = AIProvider(provider) if isinstance(provider, str) else provider
        with self._lock:
            if prov not in self._providers:
                raise AIProviderError(f"AI Provider '{prov.value}' is not registered.")
            del self._providers[prov]

    def get(self, provider: Union[AIProvider, str]) -> AIProviderClient:
        """Resolves and returns the registered client client for the provider.

        Raises AIProviderError if the provider client does not exist.
        """
        prov = AIProvider(provider) if isinstance(provider, str) else provider
        with self._lock:
            client = self._providers.get(prov)
            if client is None:
                raise AIProviderError(f"AI Provider '{prov.value}' is not registered.")
            return client

    def contains(self, provider: Union[AIProvider, str]) -> bool:
        """Checks if a client is registered under the specified provider."""
        prov = AIProvider(provider) if isinstance(provider, str) else provider
        with self._lock:
            return prov in self._providers

    def list_providers(self) -> List[AIProvider]:
        """Returns a sorted list of all currently registered AIProvider keys."""
        with self._lock:
            return sorted(self._providers.keys(), key=lambda x: x.value)

    def clear(self) -> None:
        """Removes all registered clients from the registry."""
        with self._lock:
            self._providers.clear()

    def __len__(self) -> int:
        """Returns the number of registered provider implementations."""
        with self._lock:
            return len(self._providers)

    def __contains__(self, provider: Union[AIProvider, str]) -> bool:
        """Support for 'provider in registry' syntax."""
        return self.contains(provider)
