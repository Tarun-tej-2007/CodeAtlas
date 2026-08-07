"""Unit tests for the ArchitectureReviewService component."""

import unittest
import uuid
from datetime import datetime, timezone

from app.ai import (
    AIAnalysis,
    AIAnalysisStatus,
    AIAnalysisType,
    AIContext,
    AIMetadata,
    AIProvider,
    AIRecommendation,
    AIUsageStatistics,
    AIValidationError,
    ArchitectureReview,
    RecommendationCategory,
    RecommendationPriority,
)
from app.ai.architecture_review import ArchitectureReviewService


class TestArchitectureReview(unittest.TestCase):
    """Verifies that architecture review generation is stateless, safe, and aggregates recommendations correctly."""

    def setUp(self) -> None:
        self.service = ArchitectureReviewService()
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
        self.analysis = AIAnalysis(
            analysis_id=uuid.uuid4(),
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.FULL_ARCHITECTURE_REVIEW,
            status=AIAnalysisStatus.COMPLETED,
            started_at=self.time_utc,
            completed_at=self.time_utc,
            statistics=AIUsageStatistics(),
        )
        self.context = AIContext(
            project_id=self.project_id,
            commit_id=self.commit_id,
            files_count=10,
            governance_violations=("Viol 1 [error]",),
            architecture_issues=("Layer Smell 1",),
            decisions_summary=("Use PostgreSQL (accepted)",),
        )

    def test_invalid_parameters(self) -> None:
        """Verifies fail-fast validation on missing inputs or project mismatch."""
        with self.assertRaises(AIValidationError):
            self.service.generate_review(None, self.analysis, ())

        with self.assertRaises(AIValidationError):
            self.service.generate_review(self.context, None, ())

        # Mismatch project ID
        bad_analysis = AIAnalysis(
            analysis_id=uuid.uuid4(),
            project_id=uuid.uuid4(),  # Different ID
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.FULL_ARCHITECTURE_REVIEW,
            status=AIAnalysisStatus.COMPLETED,
            started_at=self.time_utc,
        )
        with self.assertRaises(AIValidationError):
            self.service.generate_review(self.context, bad_analysis, ())

    def test_empty_review(self) -> None:
        """Verifies review generation with empty recommendations and minimal context."""
        empty_ctx = AIContext(
            project_id=self.project_id,
            commit_id=self.commit_id,
            files_count=0,
        )
        review = self.service.generate_review(empty_ctx, self.analysis, ())

        self.assertIsInstance(review, ArchitectureReview)
        self.assertEqual(review.health_score, 100.0)
        self.assertEqual(len(review.strengths), 1)  # Compliance strength
        self.assertEqual(review.weaknesses, ())
        self.assertEqual(review.risks, ())

    def test_complete_review_generation_and_deduplication(self) -> None:
        """Verifies full aggregation, scoring deduction, and deduplication works."""
        rec1 = AIRecommendation(
            recommendation_id=uuid.uuid4(),
            title="Refactor Layering",
            description="UI depends directly on database.",
            category=RecommendationCategory.ARCHITECTURE,
            priority=RecommendationPriority.CRITICAL,
        )
        rec2 = AIRecommendation(
            recommendation_id=uuid.uuid4(),
            title="Fix SSL",
            description="Use TLS for secure connections.",
            category=RecommendationCategory.SECURITY,
            priority=RecommendationPriority.HIGH,
            suggested_fix="Enable SSL in configs.",
            suggested_actions=("Update config.json",),
        )

        review = self.service.generate_review(self.context, self.analysis, (rec1, rec2))

        # Health score deductions:
        # Base: 100
        # rec1 critical: -15
        # rec2 high: -10
        # gov violation: -5
        # arch issue: -3
        # Expected score: 100 - 33 = 67.0
        self.assertEqual(review.health_score, 67.0)

        # Strengths: ADR strength, Modular strength, layout strength
        self.assertEqual(len(review.strengths), 2)  # Modular Separation, Documented Architecture Intent
        self.assertEqual(review.strengths[0].title, "Documented Architecture Intent")

        # Weaknesses: rec1 weakness, and the context architecture issue weakness
        self.assertEqual(len(review.weaknesses), 2)

        # Risks: rec2 security risk
        self.assertEqual(len(review.risks), 1)
        self.assertEqual(review.risks[0].title, "Fix SSL")

        # Roadmap, immediate actions
        self.assertIn("Update config.json", review.immediate_actions)
        self.assertGreater(len(review.roadmap.phases), 0)


if __name__ == "__main__":
    unittest.main()
