"""Unit tests for the DecisionTraceabilityService and trace graph compilation."""

import unittest
import uuid
from datetime import datetime, timezone

from app.decision import (
    ArchitectureDecision,
    DecisionCategory,
    DecisionPriority,
    DecisionStatus,
    DecisionTraceabilityService,
    DecisionMetadata,
    DecisionTraceLink,
    DecisionTraceGraph,
    DecisionTraceabilityError,
)


class TestDecisionTraceability(unittest.TestCase):
    """Verifies decision target extraction, indexing, duplication elimination, and ordering."""

    def setUp(self) -> None:
        self.service = DecisionTraceabilityService()
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-trace-456"
        self.time_utc = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)
        self.metadata = DecisionMetadata(
            author="Lead Architect",
            created_at=self.time_utc,
            updated_at=self.time_utc,
            extra_info={},
        )

    def test_empty_repository_and_empty_decisions(self) -> None:
        """Verifies correct trace graph compilation for empty inputs."""
        graph = self.service.trace_decisions(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(),
        )
        self.assertEqual(graph.project_id, self.project_id)
        self.assertEqual(graph.commit_id, self.commit_id)
        self.assertEqual(len(graph.links), 0)
        self.assertEqual(len(graph.links_by_target), 0)
        self.assertEqual(len(graph.links_by_decision), 0)

    def test_single_trace_relationship(self) -> None:
        """Verifies mapping of a single file target to a decision."""
        dec_id = uuid.uuid4()
        dec = ArchitectureDecision(
            decision_id=dec_id,
            title="T",
            category=DecisionCategory.DESIGN,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.LOW,
            context="C",
            decision_text="D",
            consequences="Con",
            metadata=DecisionMetadata(
                author="A",
                created_at=self.time_utc,
                updated_at=self.time_utc,
                extra_info={"targets": ("file:src/app.py",)},
            ),
        )

        graph = self.service.trace_decisions(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(dec,),
        )

        self.assertEqual(len(graph.links), 1)
        link = graph.links[0]
        self.assertEqual(link.target_id, "src/app.py")
        self.assertEqual(link.target_type, "file")
        self.assertEqual(link.decision_id, dec_id)

        # Index maps correctly
        self.assertIn("file:src/app.py", graph.links_by_target)
        self.assertEqual(graph.links_by_target["file:src/app.py"], (dec_id,))

    def test_multiple_trace_relationships_types(self) -> None:
        """Verifies tracking across file, package, policy, component and evolution target link types."""
        dec1_id = uuid.uuid4()
        dec1 = ArchitectureDecision(
            decision_id=dec1_id,
            title="T1",
            category=DecisionCategory.DESIGN,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.LOW,
            context="C",
            decision_text="D",
            consequences="Con",
            metadata=DecisionMetadata(
                author="A",
                created_at=self.time_utc,
                updated_at=self.time_utc,
                extra_info={"targets": ("package:src/components", "policy:layer_rule")},
            ),
        )

        dec2_id = uuid.uuid4()
        dec2 = ArchitectureDecision(
            decision_id=dec2_id,
            title="T2",
            category=DecisionCategory.DESIGN,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.LOW,
            context="C",
            decision_text="D",
            consequences="Con",
            metadata=DecisionMetadata(
                author="A",
                created_at=self.time_utc,
                updated_at=self.time_utc,
                extra_info={"targets": ("evolution:evolution_01",)},
            ),
        )

        graph = self.service.trace_decisions(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(dec1, dec2),
        )

        # 3 links total
        self.assertEqual(len(graph.links), 3)
        types = [link.target_type for link in graph.links]
        # Sorted alphabetically: evolution, package, policy
        self.assertEqual(types, ["evolution", "package", "policy"])

    def test_duplicate_link_elimination(self) -> None:
        """Verifies duplicate target link declarations are deduped under a single decision."""
        dec_id = uuid.uuid4()
        dec = ArchitectureDecision(
            decision_id=dec_id,
            title="T",
            category=DecisionCategory.DESIGN,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.LOW,
            context="C",
            decision_text="D",
            consequences="Con",
            metadata=DecisionMetadata(
                author="A",
                created_at=self.time_utc,
                updated_at=self.time_utc,
                extra_info={"targets": ("file:src/app.py", "file:src/app.py")},
            ),
        )

        graph = self.service.trace_decisions(
            project_id=self.project_id,
            commit_id=self.commit_id,
            decisions=(dec,),
        )

        self.assertEqual(len(graph.links), 1)

    def test_invalid_parameters_failures(self) -> None:
        """Verifies check throws DecisionTraceabilityError on None parameter settings."""
        with self.assertRaises(DecisionTraceabilityError):
            self.service.trace_decisions(project_id=None, commit_id="commit1", decisions=())


if __name__ == "__main__":
    unittest.main()
