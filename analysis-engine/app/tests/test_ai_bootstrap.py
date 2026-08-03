"""Integration and bootstrap tests for the AI container composition root."""

import unittest

from app.core.config import Settings
from app.ai_service import (
    AIProvider,
    AIProviderRegistry,
    AIService,
    AIHealthMonitor,
    AIPromptEngine,
    AIContextManager,
    AIRequestPipeline,
    AIResponseProcessor,
    AIContainer,
    create_ai_services,
)


class TestAIBootstrap(unittest.TestCase):
    """Verifies dependency injection resolution, container state separation, and bootstrapping details."""

    def setUp(self) -> None:
        # Create a clean mock Settings object to control provider variables
        self.settings = Settings()
        self.settings.OPENAI_API_KEY = "sk-integration-test-key"
        self.settings.OPENAI_API_ENDPOINT = "https://mock.api.openai.com/v1"
        self.settings.OPENAI_TIMEOUT_SECONDS = 15
        self.settings.OPENAI_MAX_RETRIES = 0

    def test_complete_dependency_graph_creation(self) -> None:
        # Act: Instantiate composition root
        container = create_ai_services(self.settings)

        # Assert all objects constructed correctly
        self.assertIsInstance(container, AIContainer)
        self.assertIsInstance(container.registry, AIProviderRegistry)
        self.assertIsInstance(container.prompt_engine, AIPromptEngine)
        self.assertIsInstance(container.context_manager, AIContextManager)
        self.assertIsInstance(container.response_processor, AIResponseProcessor)
        self.assertIsInstance(container.ai_service, AIService)
        self.assertIsInstance(container.health_monitor, AIHealthMonitor)
        self.assertIsInstance(container.request_pipeline, AIRequestPipeline)

        # Assert dependency wiring
        self.assertEqual(container.ai_service.registry, container.registry)
        self.assertEqual(container.health_monitor.registry, container.registry)
        self.assertEqual(container.request_pipeline.context_manager, container.context_manager)
        self.assertEqual(container.request_pipeline.prompt_engine, container.prompt_engine)
        self.assertEqual(container.request_pipeline.ai_service, container.ai_service)

    def test_provider_registration(self) -> None:
        container = create_ai_services(self.settings)

        # Provider should be registered because key was configured
        self.assertTrue(container.registry.contains(AIProvider.OPENAI))

        # Check configuration parameters was correctly passed to the provider
        provider_client = container.registry.get(AIProvider.OPENAI)
        self.assertEqual(provider_client.config.api_key, "sk-integration-test-key")
        self.assertEqual(provider_client.config.endpoint, "https://mock.api.openai.com/v1")
        self.assertEqual(provider_client.config.timeout_seconds, 15)

    def test_no_registration_when_key_empty(self) -> None:
        self.settings.OPENAI_API_KEY = ""
        container = create_ai_services(self.settings)

        # Provider should NOT be registered
        self.assertFalse(container.registry.contains(AIProvider.OPENAI))

    def test_bootstrap_instances_isolation(self) -> None:
        container1 = create_ai_services(self.settings)
        container2 = create_ai_services(self.settings)

        self.assertIsNot(container1, container2)
        self.assertIsNot(container1.registry, container2.registry)
        self.assertIsNot(container1.ai_service, container2.ai_service)

    def test_deterministic_bootstrap(self) -> None:
        container1 = create_ai_services(self.settings)
        container2 = create_ai_services(self.settings)

        # Registered providers and ordering must match
        self.assertEqual(
            container1.registry.list_providers(),
            container2.registry.list_providers()
        )


if __name__ == "__main__":
    unittest.main()
