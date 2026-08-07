"""Unit tests for the PromptBuilderService component."""

import unittest
import uuid
from datetime import datetime, timezone
from types import MappingProxyType

from app.ai import (
    AIAnalysisType,
    AIContext,
    AIMetadata,
    AIProvider,
    AIRequest,
    AIValidationError,
    PromptContext,
)
from app.ai.prompt_builder import PromptBuilderService


class TestPromptBuilder(unittest.TestCase):
    """Verifies that prompt generation is stateless, safe, deterministic, and correctly formats context."""

    def setUp(self) -> None:
        self.service = PromptBuilderService()
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-abc-123"
        self.time_utc = datetime(2026, 8, 7, 10, 0, 0, tzinfo=timezone.utc)
        self.metadata = AIMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            provider=AIProvider.MOCK,
            model_name="mock-model",
            temperature=0.0,
            extra_info={},
        )

        self.empty_context = AIContext(
            project_id=self.project_id,
            commit_id=self.commit_id,
            files_count=0,
        )

        self.rich_context = AIContext(
            project_id=self.project_id,
            commit_id=self.commit_id,
            files_count=5,
            dependency_graph_summary="Node: a.py\nNode: b.py",
            architecture_issues=("LAYERING [error]: Issue 1",),
            governance_violations=("Rule 1 [warning]: Msg 1",),
            decisions_summary=("Use FastAPI (design)",),
            extra_context={"evolution": "Quality Trend: [90, 95]"},
        )

    def test_invalid_parameters(self) -> None:
        """Verifies fail-fast validation on missing inputs."""
        req = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.FULL_ARCHITECTURE_REVIEW,
            metadata=self.metadata,
        )

        with self.assertRaises(AIValidationError):
            self.service.build_prompt(None, self.empty_context)

        with self.assertRaises(AIValidationError):
            self.service.build_prompt(req, None)

    def test_empty_context(self) -> None:
        """Verifies generation succeeds even with minimal context."""
        req = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.FULL_ARCHITECTURE_REVIEW,
            metadata=self.metadata,
        )

        prompt_ctx = self.service.build_prompt(req, self.empty_context)

        self.assertIsInstance(prompt_ctx, PromptContext)
        self.assertIn("full architecture review", prompt_ctx.system_prompt)
        self.assertNotIn("Architecture Issues:", prompt_ctx.system_prompt)

    def test_architecture_review_prompt(self) -> None:
        """Verifies prompt content for FULL_ARCHITECTURE_REVIEW includes issues, structure, and details."""
        req = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.FULL_ARCHITECTURE_REVIEW,
            metadata=self.metadata,
        )

        prompt_ctx = self.service.build_prompt(req, self.rich_context)

        self.assertIn("full architecture review", prompt_ctx.system_prompt)
        self.assertIn("Node: a.py", prompt_ctx.system_prompt)
        self.assertIn("LAYERING [error]: Issue 1", prompt_ctx.system_prompt)
        self.assertIn("Rule 1 [warning]: Msg 1", prompt_ctx.system_prompt)
        self.assertIn("Use FastAPI (design)", prompt_ctx.system_prompt)
        self.assertIn("Quality Trend: [90, 95]", prompt_ctx.system_prompt)

    def test_security_review_prompt(self) -> None:
        """Verifies system instructions change correctly for SECURITY_REVIEW type."""
        req = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.SECURITY_REVIEW,
            metadata=self.metadata,
        )

        prompt_ctx = self.service.build_prompt(req, self.rich_context)
        self.assertIn("security architect", prompt_ctx.system_prompt)

    def test_governance_review_prompt(self) -> None:
        """Verifies system instructions change correctly for GOVERNANCE_REVIEW type."""
        req = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.GOVERNANCE_REVIEW,
            metadata=self.metadata,
        )

        prompt_ctx = self.service.build_prompt(req, self.rich_context)
        self.assertIn("compliance officer", prompt_ctx.system_prompt)

    def test_adr_review_prompt(self) -> None:
        """Verifies system instructions change correctly for ADR_REVIEW type."""
        req = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.ADR_REVIEW,
            metadata=self.metadata,
        )

        prompt_ctx = self.service.build_prompt(req, self.rich_context)
        self.assertIn("ADR quality reviewer", prompt_ctx.system_prompt)

    def test_custom_instructions_and_token_estimation(self) -> None:
        """Verifies user custom instructions override default user prompt and tokens are estimated."""
        req = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.CUSTOM,
            metadata=self.metadata,
            custom_instructions="Focus on performance optimization recommendations.",
        )

        prompt_ctx = self.service.build_prompt(req, self.rich_context)

        self.assertEqual(prompt_ctx.user_prompt, "Focus on performance optimization recommendations.")
        self.assertIsInstance(prompt_ctx.variables, MappingProxyType)
        
        token_est = prompt_ctx.variables.get("token_estimate")
        self.assertIsNotNone(token_est)
        self.assertGreater(token_est, 0)


if __name__ == "__main__":
    unittest.main()
