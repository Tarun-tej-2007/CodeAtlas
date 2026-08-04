"""Unit tests for the OpenAI Provider client."""

import unittest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.ai_service.enums import AIModelType, AIProvider, ResponseStatus
from app.ai_service.exceptions import AIProviderError
from app.ai_service.models import AIProviderConfig, AIRequest, AIResponse, AIUsage
from app.ai_service.providers.openai_provider import OpenAIProvider


class TestOpenAIProvider(unittest.TestCase):
    """Verifies client lazy-init, SDK parameter mapping, exceptions conversions, and usage parsing."""

    @patch("openai.OpenAI")
    def test_lazy_client_creation(self, mock_openai_class) -> None:
        config = AIProviderConfig(provider=AIProvider.OPENAI, api_key="sk-test", timeout_seconds=15)
        provider = OpenAIProvider(config)

        # Client should not be initialized on construction
        mock_openai_class.assert_not_called()

        # Trigger client generation
        client = provider._get_client()
        self.assertIsNotNone(client)
        mock_openai_class.assert_called_once_with(
            api_key="sk-test",
            base_url=None,
            timeout=15,
            max_retries=0
        )

    def test_invalid_configuration(self) -> None:
        # Pydantic validates empty string min_length constraint
        with self.assertRaises(ValidationError):
            AIProviderConfig(provider=AIProvider.OPENAI, api_key="")

        # Whitespace-only bypasses Pydantic but is caught by provider init check
        config_space = AIProviderConfig(provider=AIProvider.OPENAI, api_key="   ")
        with self.assertRaises(AIProviderError):
            OpenAIProvider(config_space)

    @patch("openai.OpenAI")
    def test_send_request_translation(self, mock_openai_class) -> None:
        # Arrange mock client and completions
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_choice = MagicMock()
        mock_choice.message.content = "Generated Python Code"

        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 120
        mock_usage.completion_tokens = 80
        mock_usage.total_tokens = 200

        mock_completion = MagicMock()
        mock_completion.id = "chatcmpl-test-123"
        mock_completion.choices = [mock_choice]
        mock_completion.usage = mock_usage

        mock_client.chat.completions.create.return_value = mock_completion

        # Act
        config = AIProviderConfig(provider=AIProvider.OPENAI, api_key="sk-test")
        provider = OpenAIProvider(config)

        request = AIRequest(
            id="req-123",
            model_type=AIModelType.BALANCED,
            prompt="Write a function",
            temperature=0.5,
            max_output_tokens=500
        )
        response = provider.send_request(request)

        # Assert SDK parameters
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Write a function"}],
            temperature=0.5,
            max_tokens=500
        )

        # Assert DTO translations
        self.assertEqual(response.request_id, "req-123")
        self.assertEqual(response.text_content, "Generated Python Code")
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertEqual(response.usage.prompt_tokens, 120)
        self.assertEqual(response.usage.completion_tokens, 80)
        self.assertEqual(response.usage.total_tokens, 200)

    @patch("openai.OpenAI")
    def test_send_request_graceful_missing_usage(self, mock_openai_class) -> None:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_choice = MagicMock()
        mock_choice.message.content = "Success without usage"

        mock_completion = MagicMock()
        mock_completion.id = "chatcmpl-no-usage"
        mock_completion.choices = [mock_choice]
        mock_completion.usage = None  # Missing usage block

        mock_client.chat.completions.create.return_value = mock_completion

        config = AIProviderConfig(provider=AIProvider.OPENAI, api_key="sk-test")
        provider = OpenAIProvider(config)
        request = AIRequest(id="req-1", model_type=AIModelType.FAST, prompt="Hi")

        response = provider.send_request(request)
        self.assertEqual(response.status, ResponseStatus.SUCCESS)
        self.assertIsNone(response.usage)

    @patch("openai.OpenAI")
    def test_exception_mapping(self, mock_openai_class) -> None:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Configure client creation to raise an error
        mock_client.chat.completions.create.side_effect = RuntimeError("OpenAI connection timeout")

        config = AIProviderConfig(provider=AIProvider.OPENAI, api_key="sk-test")
        provider = OpenAIProvider(config)
        request = AIRequest(id="req-1", model_type=AIModelType.FAST, prompt="Hi")

        # Runtime exceptions must be caught and chained into AIProviderError
        with self.assertRaises(AIProviderError) as context:
            provider.send_request(request)

        self.assertIn("completion request failed", str(context.exception))
        self.assertIsInstance(context.exception.__cause__, RuntimeError)

    @patch("openai.OpenAI")
    def test_health_check_connectivity(self, mock_openai_class) -> None:
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        config = AIProviderConfig(provider=AIProvider.OPENAI, api_key="sk-test")
        provider = OpenAIProvider(config)

        # Successful listing means healthy connection
        mock_client.models.list.return_value = MagicMock()
        self.assertTrue(provider.health_check())

        # Unsuccessful listing means unhealthy connection
        mock_client.models.list.side_effect = RuntimeError("API key revoked")
        self.assertFalse(provider.health_check())

    def test_model_resolution_overrides(self) -> None:
        # Default mapping
        config_default = AIProviderConfig(provider=AIProvider.OPENAI, api_key="sk-test")
        prov_default = OpenAIProvider(config_default)
        self.assertEqual(prov_default._resolve_model(AIModelType.FAST), "gpt-4o-mini")
        self.assertEqual(prov_default._resolve_model(AIModelType.BALANCED), "gpt-4o")
        self.assertEqual(prov_default._resolve_model(AIModelType.POWERFUL), "gpt-4-turbo")

        # Config overrides
        config_override = AIProviderConfig(
            provider=AIProvider.OPENAI,
            api_key="sk-test",
            extra_params={
                "model_fast": "custom-fast-model",
                "model_balanced": "custom-balanced-model",
                "model_powerful": "custom-powerful-model",
            }
        )
        prov_override = OpenAIProvider(config_override)
        self.assertEqual(prov_override._resolve_model(AIModelType.FAST), "custom-fast-model")
        self.assertEqual(prov_override._resolve_model(AIModelType.BALANCED), "custom-balanced-model")
        self.assertEqual(prov_override._resolve_model(AIModelType.POWERFUL), "custom-powerful-model")

    @patch("openai.OpenAI")
    def test_thread_safe_lazy_initialization(self, mock_openai_class) -> None:
        import threading
        from concurrent.futures import ThreadPoolExecutor

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        config = AIProviderConfig(provider=AIProvider.OPENAI, api_key="sk-test")
        provider = OpenAIProvider(config)

        barrier = threading.Barrier(10)

        def worker():
            barrier.wait()
            return provider._get_client()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker) for _ in range(10)]
            results = [f.result() for f in futures]

        # All threads should resolve the exact same client instance
        first_client = results[0]
        for c in results:
            self.assertEqual(c, first_client)

        # Constructor of the OpenAI client class must be executed exactly once
        mock_openai_class.assert_called_once()


if __name__ == "__main__":
    unittest.main()
