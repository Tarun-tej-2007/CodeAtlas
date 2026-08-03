"""AI Service module.

Implements the AIService facade, delegating requests and health checks
to registered AI providers.
"""

from typing import Tuple, Union

from app.ai_service.enums import AIProvider
from app.ai_service.exceptions import AIProviderError
from app.ai_service.models import AIRequest, AIResponse
from app.ai_service.registry import AIProviderRegistry


class AIService:
    """Primary application facade coordinating request dispatch and health checks across AI providers."""

    def __init__(self, registry: AIProviderRegistry) -> None:
        """Initializes the service with a dependency-injected provider registry."""
        self.registry = registry

    def send_request(self, provider: Union[AIProvider, str], request: AIRequest) -> AIResponse:
        """Resolves the requested provider from the registry and delegates request execution."""
        prov = AIProvider(provider) if isinstance(provider, str) else provider
        client = self.registry.get(prov)
        return client.send_request(request)

    def health_check(self, provider: Union[AIProvider, str]) -> bool:
        """Delegates connection health check queries directly to the concrete provider implementation."""
        prov = AIProvider(provider) if isinstance(provider, str) else provider
        try:
            client = self.registry.get(prov)
            return client.health_check()
        except AIProviderError:
            return False

    def list_providers(self) -> Tuple[AIProvider, ...]:
        """Lists all registered providers in a deterministically sorted tuple."""
        return tuple(self.registry.list_providers())

    def has_provider(self, provider: Union[AIProvider, str]) -> bool:
        """Checks if a client is registered under the specified provider key."""
        prov = AIProvider(provider) if isinstance(provider, str) else provider
        return self.registry.contains(prov)
