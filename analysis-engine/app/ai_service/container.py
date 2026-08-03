"""AI composition container module.

Defines the AIContainer composition root that instantiates, registers, and wires
all AI subsystem components using dependency injection.
"""

from typing import Optional

from app.core.config import Settings, settings as global_settings
from app.ai_service.enums import AIProvider
from app.ai_service.models import AIProviderConfig
from app.ai_service.registry import AIProviderRegistry
from app.ai_service.providers.openai_provider import OpenAIProvider
from app.ai_service.service import AIService
from app.ai_service.health import AIHealthMonitor
from app.ai_service.prompts import AIPromptEngine
from app.ai_service.context import AIContextManager
from app.ai_service.pipeline import AIRequestPipeline
from app.ai_service.response_processor import AIResponseProcessor


class AIContainer:
    """Composition root container encapsulating registries, engines, and wired AI services."""

    def __init__(self, app_settings: Optional[Settings] = None) -> None:
        """Wires up all domain engines, registries, providers, and request pipelines."""
        self.settings = app_settings or global_settings

        # 1. Instantiate registry and stateless engines
        self.registry = AIProviderRegistry()
        self.prompt_engine = AIPromptEngine()
        self.context_manager = AIContextManager()
        self.response_processor = AIResponseProcessor()

        # 2. Bootstrap provider clients
        self._bootstrap_providers()

        # 3. Instantiate facade and orchestration pipelines
        self.ai_service = AIService(self.registry)
        self.health_monitor = AIHealthMonitor(self.registry)
        self.request_pipeline = AIRequestPipeline(
            context_manager=self.context_manager,
            prompt_engine=self.prompt_engine,
            ai_service=self.ai_service,
        )

    def _bootstrap_providers(self) -> None:
        """Configures and registers provider implementations based on settings."""
        # OpenAI Provider Bootstrapping
        openai_key = self.settings.OPENAI_API_KEY
        if openai_key and len(openai_key.strip()) > 0:
            config = AIProviderConfig(
                provider=AIProvider.OPENAI,
                api_key=openai_key,
                endpoint=self.settings.OPENAI_API_ENDPOINT or None,
                timeout_seconds=self.settings.OPENAI_TIMEOUT_SECONDS,
                max_retries=self.settings.OPENAI_MAX_RETRIES,
            )
            openai_provider = OpenAIProvider(config)
            self.registry.register(AIProvider.OPENAI, openai_provider)


def create_ai_services(app_settings: Optional[Settings] = None) -> AIContainer:
    """Factory helper to construct and return a wired AIContainer instance."""
    return AIContainer(app_settings=app_settings)
