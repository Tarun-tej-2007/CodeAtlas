"""Unit tests for the AIHealthMonitor component."""

import unittest
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from app.ai_service import (
    AIProvider,
    AIProviderClient,
    AIProviderRegistry,
    AIHealthMonitor,
    ProviderHealthStatus,
    HealthSummary,
)
from app.ai_service.exceptions import AIProviderError


class TestAIHealthMonitor(unittest.TestCase):
    """Verifies aggregated health checks, error boundaries, determinism, and thread-safe execution."""

    def setUp(self) -> None:
        self.registry = AIProviderRegistry()
        self.monitor = AIHealthMonitor(self.registry)

        self.openai_client = MagicMock(spec=AIProviderClient)
        self.gemini_client = MagicMock(spec=AIProviderClient)

        self.registry.register(AIProvider.OPENAI, self.openai_client)
        self.registry.register(AIProvider.GEMINI, self.gemini_client)

    def test_healthy_provider(self) -> None:
        self.openai_client.health_check.return_value = True

        status = self.monitor.check_provider(AIProvider.OPENAI)
        self.assertEqual(status.provider, AIProvider.OPENAI)
        self.assertTrue(status.healthy)
        self.assertIsNone(status.error_message)
        self.assertEqual(status.checked_at.tzinfo, timezone.utc)

    def test_unhealthy_provider(self) -> None:
        self.openai_client.health_check.return_value = False

        status = self.monitor.check_provider(AIProvider.OPENAI)
        self.assertEqual(status.provider, AIProvider.OPENAI)
        self.assertFalse(status.healthy)
        self.assertIsNotNone(status.error_message)

    def test_exception_during_health_check(self) -> None:
        self.openai_client.health_check.side_effect = RuntimeError("Socket timeout")

        status = self.monitor.check_provider(AIProvider.OPENAI)
        self.assertEqual(status.provider, AIProvider.OPENAI)
        self.assertFalse(status.healthy)
        self.assertIn("Socket timeout", status.error_message)

    def test_unknown_provider(self) -> None:
        status = self.monitor.check_provider(AIProvider.ANTHROPIC)
        self.assertEqual(status.provider, AIProvider.ANTHROPIC)
        self.assertFalse(status.healthy)
        self.assertIn("not registered", status.error_message)

    def test_multiple_providers_and_deterministic_ordering(self) -> None:
        self.gemini_client.health_check.return_value = True
        self.openai_client.health_check.return_value = False

        summary = self.monitor.check_all()

        # Summary counts
        self.assertEqual(summary.healthy_count, 1)
        self.assertEqual(summary.unhealthy_count, 1)
        self.assertEqual(len(summary.results), 2)

        # Deterministic sorting (GEMINI, OPENAI)
        self.assertEqual(summary.results[0].provider, AIProvider.GEMINI)
        self.assertTrue(summary.results[0].healthy)

        self.assertEqual(summary.results[1].provider, AIProvider.OPENAI)
        self.assertFalse(summary.results[1].healthy)

    def test_availability_helper(self) -> None:
        self.openai_client.health_check.return_value = True
        self.gemini_client.health_check.return_value = False

        self.assertTrue(self.monitor.is_available(AIProvider.OPENAI))
        self.assertFalse(self.monitor.is_available(AIProvider.GEMINI))
        self.assertFalse(self.monitor.is_available(AIProvider.ANTHROPIC))

    def test_concurrent_health_checks(self) -> None:
        self.openai_client.health_check.return_value = True
        self.gemini_client.health_check.return_value = True

        def run_check():
            return self.monitor.check_all()

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_check) for _ in range(10)]
            results = [f.result() for f in futures]

        for s in results:
            self.assertEqual(s.healthy_count, 2)
            self.assertEqual(s.unhealthy_count, 0)
            self.assertTrue(s.results[0].healthy)
            self.assertTrue(s.results[1].healthy)


if __name__ == "__main__":
    unittest.main()
