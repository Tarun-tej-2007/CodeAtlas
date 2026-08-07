"""Unit tests for the RecommendationGeneratorService component."""

import unittest
import uuid
from datetime import datetime, timezone

from app.ai import (
    AIAnalysisType,
    AIMetadata,
    AIProvider,
    AIRequest,
    AIValidationError,
    RecommendationCategory,
    RecommendationPriority,
)
from app.ai.recommendation_engine import RecommendationGeneratorService


class TestRecommendationEngine(unittest.TestCase):
    """Verifies that recommendation parsing is stateless, deterministic, and handles malformed inputs."""

    def setUp(self) -> None:
        self.service = RecommendationGeneratorService()
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
        self.request = AIRequest(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.FULL_ARCHITECTURE_REVIEW,
            metadata=self.metadata,
        )

    def test_invalid_parameters(self) -> None:
        """Verifies fail-fast validation on missing inputs."""
        with self.assertRaises(AIValidationError):
            self.service.generate_recommendations(None, "[]")

        with self.assertRaises(AIValidationError):
            self.service.generate_recommendations(self.request, None)

    def test_empty_analysis(self) -> None:
        """Verifies empty raw completion returns empty tuple."""
        recs = self.service.generate_recommendations(self.request, "   ")
        self.assertEqual(recs, ())

    def test_single_recommendation_json(self) -> None:
        """Verifies parsing a single recommendation in JSON format."""
        raw = """
        {
            "title": "Use Constructor Injection",
            "description": "Replace field injection with constructor dependency injection.",
            "category": "architecture",
            "priority": "critical",
            "affected_files": ["src\\\\app.py"],
            "confidence_score": 0.95,
            "reasoning": "Constructor DI guarantees immutability.",
            "affected_components": ["API Layer"],
            "suggested_actions": ["Modify __init__ to accept database dependency."]
        }
        """
        recs = self.service.generate_recommendations(self.request, raw)

        self.assertEqual(len(recs), 1)
        r = recs[0]
        self.assertEqual(r.title, "Use Constructor Injection")
        self.assertEqual(r.category, RecommendationCategory.ARCHITECTURE)
        self.assertEqual(r.priority, RecommendationPriority.CRITICAL)
        self.assertEqual(r.affected_files, ("src/app.py",))
        self.assertEqual(r.confidence_score, 0.95)
        self.assertEqual(r.reasoning, "Constructor DI guarantees immutability.")
        self.assertEqual(r.affected_components, ("API Layer",))
        self.assertEqual(r.suggested_actions, ("Modify __init__ to accept database dependency.",))

    def test_multiple_recommendations_and_duplicate_elimination(self) -> None:
        """Verifies duplicate recommendations are removed and multiple recommendations are parsed."""
        raw = """
        [
            {
                "title": "A",
                "description": "Desc A",
                "category": "architecture",
                "priority": "critical"
            },
            {
                "title": "A",
                "description": "Desc A duplicate",
                "category": "architecture",
                "priority": "critical"
            },
            {
                "title": "B",
                "description": "Desc B",
                "category": "refactoring",
                "priority": "medium"
            }
        ]
        """
        recs = self.service.generate_recommendations(self.request, raw)

        self.assertEqual(len(recs), 2)
        titles = [r.title for r in recs]
        self.assertIn("A", titles)
        self.assertIn("B", titles)

    def test_malformed_recommendation_handling(self) -> None:
        """Verifies malformed entries or JSON syntax errors are ignored gracefully."""
        raw = """
        [
            {
                "title": "Malformed No Category",
                "description": "Missing category and priority."
            },
            {
                "title": "Valid Rec",
                "description": "Standard valid details.",
                "category": "security",
                "priority": "high"
            }
        ]
        """
        recs = self.service.generate_recommendations(self.request, raw)

        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0].title, "Valid Rec")

    def test_deterministic_ordering(self) -> None:
        """Verifies sorted order constraints: priority (highest first), category, then title."""
        raw = """
        [
            {
                "title": "Z Class",
                "description": "Z desc",
                "category": "architecture",
                "priority": "medium"
            },
            {
                "title": "A Class",
                "description": "A desc",
                "category": "architecture",
                "priority": "medium"
            },
            {
                "title": "Critical issue",
                "description": "Crit desc",
                "category": "security",
                "priority": "critical"
            }
        ]
        """
        recs = self.service.generate_recommendations(self.request, raw)

        self.assertEqual(len(recs), 3)
        # Critical priority should come first
        self.assertEqual(recs[0].title, "Critical issue")
        # Then same priority (medium), sorted by title alphabetically ("A Class" before "Z Class")
        self.assertEqual(recs[1].title, "A Class")
        self.assertEqual(recs[2].title, "Z Class")


if __name__ == "__main__":
    unittest.main()
