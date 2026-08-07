"""Unit tests verifying the AI Architecture Intelligence domain foundation."""

import unittest
import uuid
from datetime import datetime, timezone
from types import MappingProxyType

from pydantic import ValidationError

from app.ai import (
    # Enums
    AIAnalysisStatus,
    AIAnalysisType,
    AIProvider,
    RecommendationCategory,
    RecommendationPriority,
    # Exceptions
    AIContextError,
    AIError,
    AIPersistenceError,
    AIProviderError,
    AIValidationError,
    PromptGenerationError,
    # Models
    AIAnalysis,
    AIContext,
    AIMetadata,
    AIRecommendation,
    AIRequest,
    AIResult,
    AIUsageStatistics,
    PromptContext,
    # Interfaces
    AIAnalysisPersistence,
    AIContextBuilder,
    LLMProvider,
    PromptBuilder,
    RecommendationGenerator,
)


class TestAIDomainExceptions(unittest.TestCase):
    """Verifies that all domain exceptions properly inherit from AIError."""

    def test_exception_inheritance(self) -> None:
        self.assertTrue(issubclass(AIValidationError, AIError))
        self.assertTrue(issubclass(AIProviderError, AIError))
        self.assertTrue(issubclass(AIContextError, AIError))
        self.assertTrue(issubclass(AIPersistenceError, AIError))
        self.assertTrue(issubclass(PromptGenerationError, AIError))


class TestAIDomainEnums(unittest.TestCase):
    """Verifies valid enumeration values."""

    def test_enum_values(self) -> None:
        self.assertEqual(AIProvider.OPENAI, "openai")
        self.assertEqual(AIAnalysisStatus.PENDING, "pending")
        self.assertEqual(RecommendationPriority.CRITICAL, "critical")
        self.assertEqual(RecommendationCategory.ARCHITECTURE, "architecture")
        self.assertEqual(AIAnalysisType.FULL_ARCHITECTURE_REVIEW, "full_architecture_review")


class TestAIDomainModels(unittest.TestCase):
    """Verifies model immutability, validation constraints, and serialization."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-perf-123"
        self.time_utc = datetime(2026, 8, 7, 10, 0, 0, tzinfo=timezone.utc)
        self.metadata = AIMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            provider=AIProvider.MOCK,
            model_name="mock-gpt-4",
            temperature=0.5,
            extra_info={"depth": 2},
        )

    def test_metadata_immutability_and_validation(self) -> None:
        # Check author empty validation
        with self.assertRaises(ValidationError):
            AIMetadata(
                author=" ",
                created_at=self.time_utc,
                provider=AIProvider.MOCK,
                model_name="mock-gpt-4",
            )

        # Check timestamp timezone validation
        with self.assertRaises(ValidationError):
            AIMetadata(
                author="Lead Architect",
                created_at=datetime.now(),  # naive local time
                provider=AIProvider.MOCK,
                model_name="mock-gpt-4",
            )

        # Immutability
        with self.assertRaises(ValidationError):
            # pydantic v2 raises ValidationError or AttributeError on mutability mutation attempts
            # depending on frozen state enforcement
            self.metadata.temperature = 1.0

        # MappingProxyType protection
        self.assertIsInstance(self.metadata.extra_info, MappingProxyType)
        with self.assertRaises(TypeError):
            self.metadata.extra_info["depth"] = 3

    def test_ai_request_validation(self) -> None:
        req = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.REFACTORING_REVIEW,
            metadata=self.metadata,
            custom_instructions="Look for complexity issues.",
        )
        self.assertEqual(req.commit_id, self.commit_id)

        # Validation on empty commit
        with self.assertRaises(ValidationError):
            AIRequest(
                project_id=self.project_id,
                commit_id=" ",
                analysis_type=AIAnalysisType.REFACTORING_REVIEW,
                metadata=self.metadata,
            )

    def test_ai_context_serialization(self) -> None:
        ctx = AIContext(
            project_id=self.project_id,
            commit_id=self.commit_id,
            files_count=10,
            extra_context={"graph_depth": 5},
        )
        data = ctx.model_dump()
        self.assertEqual(data["commit_id"], self.commit_id)
        self.assertEqual(data["files_count"], 10)
        self.assertEqual(data["extra_context"]["graph_depth"], 5)

    def test_prompt_context_validation(self) -> None:
        # Check empty prompts
        with self.assertRaises(ValidationError):
            PromptContext(system_prompt="", user_prompt="Analyze.")

        # Check successful creation
        pc = PromptContext(system_prompt="SYS", user_prompt="USER", variables={"a": 1})
        self.assertEqual(pc.system_prompt, "SYS")
        self.assertIsInstance(pc.variables, MappingProxyType)


class TestAIDomainInterfaces(unittest.TestCase):
    """Verifies abstract interfaces instantiation contract checks."""

    def test_interfaces_are_abstract(self) -> None:
        with self.assertRaises(TypeError):
            AIContextBuilder()

        with self.assertRaises(TypeError):
            PromptBuilder()

        with self.assertRaises(TypeError):
            LLMProvider()

        with self.assertRaises(TypeError):
            RecommendationGenerator()

        with self.assertRaises(TypeError):
            AIAnalysisPersistence()


if __name__ == "__main__":
    unittest.main()
