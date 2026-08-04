"""AI Provider Client Interface module.

Defines the abstract interface client that concrete provider engines implement.
"""

from abc import ABC, abstractmethod

from app.ai_service.models import AIProviderConfig, AIRequest, AIResponse


class AIProviderClient(ABC):
    """Abstract base class establishing the contract for custom AI provider integrations."""

    @abstractmethod
    def send_request(self, request: AIRequest) -> AIResponse:
        """Sends a structured request block to the target AI provider model.

        Must be implemented by concrete subclasses. Returns a parsed AIResponse DTO.
        """
        pass

    @abstractmethod
    def validate_configuration(self, config: AIProviderConfig) -> bool:
        """Validates provider setup parameters without conducting live requests."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Runs a shallow connectivity query to verify that the provider API is accessible."""
        pass
