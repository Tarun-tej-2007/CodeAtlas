"""Unit tests for the AIService application facade."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from app.ai_service import (
    AIModelType,
    AIProvider,
    AIProviderClient,
    AIProviderRegistry,
    AIRequest,
    AIResponse,
    AIService,
    ResponseStatus,
)
from app.ai_service.exceptions import AIProviderError


class TestAIService(unittest.TestCase):
    """Verifies facade delegation to registry and mock provider client implementations."""

    def setUp(self) -> None:
        self.registry = AIProviderRegistry()
        self.service = AIService(self.registry)

        # Mock clients
        self.openai_client = MagicMock(spec=AIProviderClient)
        self.gemini_client = MagicMock(spec=AIProviderClient)

        self.registry.register(AIProvider.OPENAI, self.openai_client)
        self.registry.register(AIProvider.GEMINI, self.gemini_client)

    def test_successful_request_delegation(self) -> None:
        req = AIRequest(id="req-1", model_type=AIModelType.FAST, prompt="Hi")
        expected_resp = AIResponse(
            id="resp-1", request_id="req-1", text_content="OpenAI text", status=ResponseStatus.SUCCESS
        )
        self.openai_client.send_request.return_value = expected_resp

        # Act
        resp = self.service.send_request(AIProvider.OPENAI, req)

        # Assert delegation occurred
        self.openai_client.send_request.assert_called_once_with(req)
        self.gemini_client.send_request.assert_not_called()
        self.assertEqual(resp, expected_resp)

    def test_unknown_provider_raises_error(self) -> None:
        req = AIRequest(id="req-1", model_type=AIModelType.FAST, prompt="Hi")
        with self.assertRaises(AIProviderError):
            self.service.send_request(AIProvider.ANTHROPIC, req)

    def test_health_check_delegation(self) -> None:
        self.openai_client.health_check.return_value = True
        self.gemini_client.health_check.return_value = False

        self.assertTrue(self.service.health_check(AIProvider.OPENAI))
        self.assertFalse(self.service.health_check(AIProvider.GEMINI))
        self.assertFalse(self.service.health_check(AIProvider.ANTHROPIC))  # Unregistered

        self.openai_client.health_check.assert_called_once()
        self.gemini_client.health_check.assert_called_once()

    def test_provider_listing_and_existence(self) -> None:
        providers = self.service.list_providers()
        self.assertEqual(providers, (AIProvider.GEMINI, AIProvider.OPENAI))

        self.assertTrue(self.service.has_provider(AIProvider.OPENAI))
        self.assertTrue(self.service.has_provider("openai"))
        self.assertFalse(self.service.has_provider(AIProvider.ANTHROPIC))

    def test_exception_propagation(self) -> None:
        req = AIRequest(id="req-1", model_type=AIModelType.FAST, prompt="Hi")
        self.openai_client.send_request.side_effect = AIProviderError("API Quota exceeded")

        with self.assertRaises(AIProviderError) as context:
            self.service.send_request(AIProvider.OPENAI, req)

        self.assertIn("Quota exceeded", str(context.exception))

    def test_stateless_concurrent_behavior(self) -> None:
        req_openai = AIRequest(id="req-op", model_type=AIModelType.FAST, prompt="OpenAI Query")
        req_gemini = AIRequest(id="req-gem", model_type=AIModelType.FAST, prompt="Gemini Query")

        resp_openai = AIResponse(
            id="resp-op", request_id="req-op", text_content="OpenAI Resp", status=ResponseStatus.SUCCESS
        )
        resp_gemini = AIResponse(
            id="resp-gem", request_id="req-gem", text_content="Gemini Resp", status=ResponseStatus.SUCCESS
        )

        self.openai_client.send_request.return_value = resp_openai
        self.gemini_client.send_request.return_value = resp_gemini

        def run_openai():
            return self.service.send_request(AIProvider.OPENAI, req_openai)

        def run_gemini():
            return self.service.send_request(AIProvider.GEMINI, req_gemini)

        # Thread Pool verification
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures_op = [executor.submit(run_openai) for _ in range(10)]
            futures_gem = [executor.submit(run_gemini) for _ in range(10)]

            results_op = [f.result() for f in futures_op]
            results_gem = [f.result() for f in futures_gem]

        for r in results_op:
            self.assertEqual(r, resp_openai)
        for r in results_gem:
            self.assertEqual(r, resp_gemini)


if __name__ == "__main__":
    unittest.main()
