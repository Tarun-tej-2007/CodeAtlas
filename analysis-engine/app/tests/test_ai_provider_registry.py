"""Unit tests for the AI Provider Registry."""

import unittest
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

from app.ai_service.enums import AIProvider, AIModelType, ResponseStatus
from app.ai_service.exceptions import AIProviderError
from app.ai_service.models import AIProviderConfig, AIRequest, AIResponse
from app.ai_service.provider import AIProviderClient
from app.ai_service.registry import AIProviderRegistry


class DummyClient(AIProviderClient):
    """Mock client implementation to verify registry mapping."""

    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    def send_request(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            id="resp-1",
            request_id=request.id,
            text_content="dummy",
            status=ResponseStatus.SUCCESS
        )

    def validate_configuration(self, config: AIProviderConfig) -> bool:
        return True

    def health_check(self) -> bool:
        return True


class TestAIProviderRegistry(unittest.TestCase):
    """Verifies thread-safe provider registrations, lookups, and lifecycle operations."""

    def setUp(self) -> None:
        self.registry = AIProviderRegistry()
        self.gemini_client = DummyClient(AIProvider.GEMINI)
        self.openai_client = DummyClient(AIProvider.OPENAI)
        self.anthropic_client = DummyClient(AIProvider.ANTHROPIC)

    def test_successful_registration_and_retrieval(self) -> None:
        self.registry.register(AIProvider.GEMINI, self.gemini_client)
        
        # Test exact retrieval
        client = self.registry.get(AIProvider.GEMINI)
        self.assertEqual(client, self.gemini_client)

        # Test string normalization retrieval
        client_str = self.registry.get("gemini")
        self.assertEqual(client_str, self.gemini_client)

    def test_duplicate_registration_raises_error(self) -> None:
        self.registry.register(AIProvider.GEMINI, self.gemini_client)
        with self.assertRaises(AIProviderError):
            self.registry.register(AIProvider.GEMINI, self.openai_client)

    def test_unknown_provider_raises_error(self) -> None:
        with self.assertRaises(AIProviderError):
            self.registry.get(AIProvider.OPENAI)

        with self.assertRaises(AIProviderError):
            self.registry.unregister(AIProvider.OPENAI)

    def test_contains_and_contains_operator(self) -> None:
        self.assertFalse(self.registry.contains(AIProvider.GEMINI))
        self.assertFalse("gemini" in self.registry)

        self.registry.register(AIProvider.GEMINI, self.gemini_client)
        self.assertTrue(self.registry.contains(AIProvider.GEMINI))
        self.assertTrue("gemini" in self.registry)

    def test_len(self) -> None:
        self.assertEqual(len(self.registry), 0)
        self.registry.register(AIProvider.GEMINI, self.gemini_client)
        self.assertEqual(len(self.registry), 1)
        self.registry.register(AIProvider.OPENAI, self.openai_client)
        self.assertEqual(len(self.registry), 2)

    def test_unregister(self) -> None:
        self.registry.register(AIProvider.GEMINI, self.gemini_client)
        self.assertEqual(len(self.registry), 1)

        self.registry.unregister(AIProvider.GEMINI)
        self.assertEqual(len(self.registry), 0)
        self.assertFalse(AIProvider.GEMINI in self.registry)

    def test_clear(self) -> None:
        self.registry.register(AIProvider.GEMINI, self.gemini_client)
        self.registry.register(AIProvider.OPENAI, self.openai_client)
        self.assertEqual(len(self.registry), 2)

        self.registry.clear()
        self.assertEqual(len(self.registry), 0)

    def test_deterministic_provider_listing(self) -> None:
        # Register in unordered sequence
        self.registry.register(AIProvider.OPENAI, self.openai_client)
        self.registry.register(AIProvider.GEMINI, self.gemini_client)
        self.registry.register(AIProvider.ANTHROPIC, self.anthropic_client)

        providers = self.registry.list_providers()
        # Verify alphabetical deterministic sorting by value (anthropic, gemini, openai)
        self.assertEqual(
            providers,
            [AIProvider.ANTHROPIC, AIProvider.GEMINI, AIProvider.OPENAI]
        )

    def test_multiple_registry_instances_isolation(self) -> None:
        reg1 = AIProviderRegistry()
        reg2 = AIProviderRegistry()

        reg1.register(AIProvider.GEMINI, self.gemini_client)
        
        self.assertEqual(len(reg1), 1)
        self.assertEqual(len(reg2), 0)
        self.assertFalse(AIProvider.GEMINI in reg2)

    def test_thread_safety_stress_test(self) -> None:
        registry = AIProviderRegistry()
        barrier = threading.Barrier(3)  # Coordinate parallel threads

        def worker_gemini():
            barrier.wait()
            try:
                registry.register(AIProvider.GEMINI, self.gemini_client)
            except AIProviderError:
                pass

        def worker_openai():
            barrier.wait()
            try:
                registry.register(AIProvider.OPENAI, self.openai_client)
            except AIProviderError:
                pass

        def worker_anthropic():
            barrier.wait()
            try:
                registry.register(AIProvider.ANTHROPIC, self.anthropic_client)
            except AIProviderError:
                pass

        # Execute concurrent mutations
        with ThreadPoolExecutor(max_workers=3) as executor:
            f1 = executor.submit(worker_gemini)
            f2 = executor.submit(worker_openai)
            f3 = executor.submit(worker_anthropic)
            f1.result()
            f2.result()
            f3.result()

        # Registry should have precisely 3 registered providers without state corruption
        self.assertEqual(len(registry), 3)
        self.assertEqual(
            registry.list_providers(),
            [AIProvider.ANTHROPIC, AIProvider.GEMINI, AIProvider.OPENAI]
        )


if __name__ == "__main__":
    unittest.main()
