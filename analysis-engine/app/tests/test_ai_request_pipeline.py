"""Unit tests for the AIRequestPipeline component."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority, ResponseStatus
from app.ai_service.exceptions import AIProviderError
from app.ai_service.models import AIRequest, AIResponse, AIUsage
from app.ai_service.context import AIContext, ContextSection, AIContextManager
from app.ai_service.prompts import AIPromptEngine, PromptTemplate, RenderedPrompt
from app.ai_service.service import AIService
from app.ai_service.pipeline import AIRequestPipeline


class TestAIRequestPipeline(unittest.TestCase):
    """Verifies orchestration pipeline delegation, parameter building, error routing, and concurrency safety."""

    def setUp(self) -> None:
        self.context_manager = MagicMock(spec=AIContextManager)
        self.prompt_engine = MagicMock(spec=AIPromptEngine)
        self.ai_service = MagicMock(spec=AIService)

        self.pipeline = AIRequestPipeline(
            self.context_manager,
            self.prompt_engine,
            self.ai_service
        )

        self.sec = ContextSection(name="sec-1", content="Context Section Content")
        self.context = AIContext(
            title="Pipeline Context",
            description="Testing context",
            metadata={"run": 1},
            sections=(self.sec,)
        )

    def test_successful_execution_and_delegation(self) -> None:
        # Arrange mock outputs
        rendered = RenderedPrompt(template_name="test-tmpl", prompt="Rendered: Context Section Content / Extra Val")
        self.prompt_engine.render.return_value = rendered

        expected_response = AIResponse(
            id="resp-123",
            request_id="req-123",
            text_content="Final completion result",
            status=ResponseStatus.SUCCESS,
            usage=AIUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        )
        self.ai_service.send_request.return_value = expected_response

        # Act
        variables = {"extra": "Extra Val"}
        response = self.pipeline.execute(
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            template_name="test-tmpl",
            context=self.context,
            variables=variables,
            priority=RequestPriority.HIGH,
            temperature=0.7,
            max_tokens=300
        )

        # Assert delegation outputs
        expected_merged_vars = {
            "extra": "Extra Val",
            "sec-1": "Context Section Content"
        }
        self.prompt_engine.render.assert_called_once_with("test-tmpl", expected_merged_vars)

        # Verify request parameters
        self.ai_service.send_request.assert_called_once()
        called_arg = self.ai_service.send_request.call_args[0][1]
        self.assertIsInstance(called_arg, AIRequest)
        self.assertIn("pipeline-req-", called_arg.id)
        self.assertEqual(called_arg.model_type, AIModelType.BALANCED)
        self.assertEqual(called_arg.prompt, "Rendered: Context Section Content / Extra Val")
        self.assertEqual(called_arg.priority, RequestPriority.HIGH)
        self.assertEqual(called_arg.temperature, 0.7)
        self.assertEqual(called_arg.max_output_tokens, 300)

        self.assertEqual(response, expected_response)

    def test_context_immutability_is_preserved(self) -> None:
        rendered = RenderedPrompt(template_name="test-tmpl", prompt="Some prompt")
        self.prompt_engine.render.return_value = rendered

        # Act
        self.pipeline.execute(
            provider=AIProvider.OPENAI,
            model_type=AIModelType.FAST,
            template_name="test-tmpl",
            context=self.context,
            variables={},
        )

        # Assert context content was not mutated
        self.assertEqual(self.context.title, "Pipeline Context")
        self.assertEqual(len(self.context.sections), 1)
        self.assertEqual(self.context.sections[0].name, "sec-1")

    def test_exception_propagation(self) -> None:
        self.prompt_engine.render.side_effect = AIProviderError("Template not found")

        with self.assertRaises(AIProviderError):
            self.pipeline.execute(
                provider=AIProvider.OPENAI,
                model_type=AIModelType.FAST,
                template_name="bad-tmpl",
                context=self.context,
                variables={},
            )

    def test_multiple_pipeline_instances_isolation(self) -> None:
        pipeline1 = AIRequestPipeline(self.context_manager, self.prompt_engine, self.ai_service)
        pipeline2 = AIRequestPipeline(self.context_manager, self.prompt_engine, self.ai_service)
        self.assertIsNot(pipeline1, pipeline2)

    def test_concurrent_execution_safety(self) -> None:
        rendered = RenderedPrompt(template_name="test-tmpl", prompt="Rendered content")
        self.prompt_engine.render.return_value = rendered

        expected_response = AIResponse(
            id="resp-1", request_id="req-1", text_content="done", status=ResponseStatus.SUCCESS
        )
        self.ai_service.send_request.return_value = expected_response

        def run_pipeline():
            return self.pipeline.execute(
                provider=AIProvider.OPENAI,
                model_type=AIModelType.FAST,
                template_name="test-tmpl",
                context=self.context,
                variables={},
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_pipeline) for _ in range(15)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r, expected_response)

    def test_deterministic_execution(self) -> None:
        rendered = RenderedPrompt(template_name="test-tmpl", prompt="Hello Bob")
        self.prompt_engine.render.return_value = rendered

        # Same inputs must trigger identical request IDs
        self.pipeline.execute(
            provider=AIProvider.OPENAI,
            model_type=AIModelType.FAST,
            template_name="test-tmpl",
            context=self.context,
            variables={"name": "Bob"},
        )
        req1 = self.ai_service.send_request.call_args[0][1]

        self.pipeline.execute(
            provider=AIProvider.OPENAI,
            model_type=AIModelType.FAST,
            template_name="test-tmpl",
            context=self.context,
            variables={"name": "Bob"},
        )
        req2 = self.ai_service.send_request.call_args[0][1]

        self.assertEqual(req1.id, req2.id)


if __name__ == "__main__":
    unittest.main()
