"""Unit tests for the AI Service Domain Foundation."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.ai_service import (
    AIProvider,
    AIModelType,
    RequestPriority,
    ResponseStatus,
    AIServiceError,
    AIProviderError,
    AIRequestError,
    AIResponseError,
    AIUsage,
    AIProviderConfig,
    AIRequest,
    AIResponse,
    AIProviderClient,
)


class MockProviderClient(AIProviderClient):
    """Concrete mock client to verify abstract interface compatibility."""

    def __init__(self, key: str = "mock-key") -> None:
        self.key = key

    def send_request(self, request: AIRequest) -> AIResponse:
        usage = AIUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        return AIResponse(
            id="resp-1",
            request_id=request.id,
            text_content=f"Processed: {request.prompt}",
            status=ResponseStatus.SUCCESS,
            usage=usage
        )

    def validate_configuration(self, config: AIProviderConfig) -> bool:
        return config.api_key == self.key

    def health_check(self) -> bool:
        return True


class TestAIServiceDomainFoundation(unittest.TestCase):
    """Verifies AI service DTO serialization, validation rules, exceptions, and contracts."""

    def test_enums(self) -> None:
        self.assertEqual(AIProvider.GEMINI, "gemini")
        self.assertEqual(AIModelType.FAST, "fast")
        self.assertEqual(RequestPriority.HIGH, "high")
        self.assertEqual(ResponseStatus.SUCCESS, "success")

    def test_exceptions_hierarchy(self) -> None:
        with self.assertRaises(AIServiceError):
            raise AIProviderError("Connection timeout")

        with self.assertRaises(AIServiceError):
            raise AIRequestError("Empty request prompt")

    def test_model_validation_and_bounds(self) -> None:
        # Invalid temperature (max allowed is 2.0)
        with self.assertRaises(ValidationError):
            AIRequest(
                id="req-1",
                model_type=AIModelType.BALANCED,
                prompt="Hello",
                temperature=2.5
            )

        # Invalid token bounds
        with self.assertRaises(ValidationError):
            AIUsage(prompt_tokens=-1, completion_tokens=10, total_tokens=9)

    def test_serialization(self) -> None:
        config = AIProviderConfig(
            provider=AIProvider.GEMINI,
            api_key="secret-key",
            timeout_seconds=60
        )
        dump = config.model_dump()
        self.assertEqual(dump["provider"], "gemini")
        self.assertEqual(dump["api_key"], "secret-key")

        json_str = config.model_dump_json()
        self.assertIn('"provider":"gemini"', json_str)

    def test_immutability(self) -> None:
        usage = AIUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        with self.assertRaises((ValidationError, TypeError)):
            usage.prompt_tokens = 20  # type: ignore

    def test_abstract_interface_boundaries(self) -> None:
        # Class cannot be instantiated directly due to abstract methods
        with self.assertRaises(TypeError):
            AIProviderClient()  # type: ignore

        client = MockProviderClient(key="valid-key")
        self.assertTrue(client.health_check())

        config = AIProviderConfig(provider=AIProvider.GEMINI, api_key="valid-key")
        self.assertTrue(client.validate_configuration(config))

        req = AIRequest(id="req-1", model_type=AIModelType.FAST, prompt="Hi")
        res = client.send_request(req)
        self.assertEqual(res.text_content, "Processed: Hi")
        self.assertEqual(res.status, ResponseStatus.SUCCESS)

    def test_repeated_execution_determinism(self) -> None:
        client = MockProviderClient()
        req = AIRequest(id="req-1", model_type=AIModelType.FAST, prompt="Hi")
        
        res1 = client.send_request(req)
        res2 = client.send_request(req)
        self.assertEqual(res1, res2)

    def test_thread_safety_and_concurrency(self) -> None:
        client = MockProviderClient()
        req = AIRequest(id="req-1", model_type=AIModelType.FAST, prompt="Hi")

        def run_query():
            return client.send_request(req)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_query) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for r in results:
            self.assertEqual(r, first)


if __name__ == "__main__":
    unittest.main()
