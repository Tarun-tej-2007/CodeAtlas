"""AI Health Monitor module.

Defines health status reporting models and the AIHealthMonitor component.
"""

from datetime import datetime, timezone
from typing import Optional, Tuple, Union
from pydantic import BaseModel, ConfigDict, Field

from app.ai_service.enums import AIProvider
from app.ai_service.registry import AIProviderRegistry


class ProviderHealthStatus(BaseModel):
    """Immutable status report for a single AI provider."""

    provider: AIProvider = Field(..., description="The queried AI provider.")
    healthy: bool = Field(..., description="True if the provider returned healthy status.")
    checked_at: datetime = Field(..., description="Timezone-aware UTC timestamp of the health check.")
    error_message: Optional[str] = Field(default=None, description="Concise error message if unhealthy.")

    model_config = ConfigDict(frozen=True)


class HealthSummary(BaseModel):
    """Aggregated health overview of all monitored providers."""

    results: Tuple[ProviderHealthStatus, ...] = Field(..., description="Deterministic sorted status results.")
    healthy_count: int = Field(..., description="Number of healthy providers.")
    unhealthy_count: int = Field(..., description="Number of unhealthy providers.")

    model_config = ConfigDict(frozen=True)


class AIHealthMonitor:
    """Stateless service responsible for querying connectivity of registered AI providers."""

    def __init__(self, registry: AIProviderRegistry) -> None:
        """Initializes the monitor with a provider registry."""
        self.registry = registry

    def check_provider(self, provider: Union[AIProvider, str]) -> ProviderHealthStatus:
        """Checks the connectivity of a single provider. Never propagates exceptions."""
        prov = AIProvider(provider) if isinstance(provider, str) else provider
        now = datetime.now(timezone.utc)
        try:
            client = self.registry.get(prov)
            is_healthy = client.health_check()
            err_msg = None if is_healthy else "Provider health check returned unhealthy."
            return ProviderHealthStatus(
                provider=prov,
                healthy=is_healthy,
                checked_at=now,
                error_message=err_msg,
            )
        except Exception as e:
            return ProviderHealthStatus(
                provider=prov,
                healthy=False,
                checked_at=now,
                error_message=str(e),
            )

    def check_all(self) -> HealthSummary:
        """Checks health status for all registered providers in deterministic order."""
        providers = self.registry.list_providers()
        results = []
        healthy_count = 0
        unhealthy_count = 0
        for p in providers:
            status = self.check_provider(p)
            results.append(status)
            if status.healthy:
                healthy_count += 1
            else:
                unhealthy_count += 1
        return HealthSummary(
            results=tuple(results),
            healthy_count=healthy_count,
            unhealthy_count=unhealthy_count,
        )

    def is_available(self, provider: Union[AIProvider, str]) -> bool:
        """Returns True if the provider has been registered and verified healthy."""
        prov = AIProvider(provider) if isinstance(provider, str) else provider
        status = self.check_provider(prov)
        return status.healthy
