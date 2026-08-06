"""Unit tests for the Incremental Analysis orchestrator service."""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.graph.dependency_graph import DependencyGraph
from app.graph.dependency_models import GraphNode
from app.graph.enums import DependencyNodeType
from app.incremental import (
    ChangeType,
    ChangedFile,
    DependencyImpactAnalyzer,
    IncrementalAnalysisValidationError,
    IncrementalAnalysisService,
    IncrementalAnalysisPersistence,
    RepositorySnapshotService,
    SHA256SnapshotDifferenceEngine,
    RepositorySnapshot,
    FileFingerprint,
)


class TestIncrementalAnalysisService(unittest.TestCase):
    """Verifies orchestration sequence, first-time runs, short-circuit loops, validations, and failures."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.project_name = "MockProj"
        self.repo_root = "c:/Users/tarun/OneDrive/Desktop/projects/CodeAtlas/analysis-engine/app/tests/temp_dir"
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)

        # Build Mock collaborators
        self.snapshot_service = MagicMock(spec=RepositorySnapshotService)
        self.diff_engine = MagicMock(spec=SHA256SnapshotDifferenceEngine)
        self.impact_analyzer = MagicMock(spec=DependencyImpactAnalyzer)
        self.persistence = MagicMock(spec=IncrementalAnalysisPersistence)

        self.service = IncrementalAnalysisService(
            snapshot_service=self.snapshot_service,
            diff_engine=self.diff_engine,
            impact_analyzer=self.impact_analyzer,
            persistence=self.persistence,
        )

        self.dependency_graph = DependencyGraph(
            nodes=[GraphNode(id="src/a.py", name="a", type=DependencyNodeType.MODULE)],
            edges=[],
        )

        # Standard return snapshots
        self.current_snap = RepositorySnapshot(commit_id="commit_target", fingerprints={})
        self.snapshot_service.create_snapshot.return_value = self.current_snap
        self.persistence.get_snapshot.return_value = None

    def test_constructor_validation(self) -> None:
        """Verifies constructor validates None inputs."""
        with self.assertRaises(ValueError):
            IncrementalAnalysisService(
                snapshot_service=None,  # type: ignore
                diff_engine=self.diff_engine,
                impact_analyzer=self.impact_analyzer,
                persistence=self.persistence,
            )

    def test_invalid_parameters(self) -> None:
        """Verifies validations reject invalid or None parameters."""
        with self.assertRaises(IncrementalAnalysisValidationError):
            self.service.analyze_incrementally(
                project_id=None,  # type: ignore
                project_name=self.project_name,
                repository_root=self.repo_root,
                source_commit="c1",
                target_commit="c2",
                dependency_graph=self.dependency_graph,
            )

        with self.assertRaises(IncrementalAnalysisValidationError):
            self.service.analyze_incrementally(
                project_id=self.project_id,
                project_name="  ",
                repository_root=self.repo_root,
                source_commit="c1",
                target_commit="c2",
                dependency_graph=self.dependency_graph,
            )

    def test_first_time_repository_analysis(self) -> None:
        """Verifies that a first-time analysis (no previous snapshot found) compares against an empty snapshot."""
        # Setup mock returns
        cf = ChangedFile(path="src/a.py", change_type=ChangeType.ADDED)
        self.diff_engine.diff_snapshots.return_value = (cf,)
        self.impact_analyzer.analyze_impact.return_value = ("src/a.py",)

        res = self.service.analyze_incrementally(
            project_id=self.project_id,
            project_name=self.project_name,
            repository_root=self.repo_root,
            source_commit="c1",
            target_commit="c2",
            dependency_graph=self.dependency_graph,
        )

        self.assertEqual(res.added_count, 1)
        self.assertEqual(res.modified_count, 0)
        self.persistence.get_snapshot.assert_called_once_with("c1")
        # Diff engine should be called with an empty snapshot
        args, _ = self.diff_engine.diff_snapshots.call_args
        self.assertEqual(args[0].commit_id, "c1")
        self.assertEqual(len(args[0].fingerprints), 0)

        # Verifies calls persisted results exactly once
        self.persistence.save_result.assert_called_once_with(res)
        self.persistence.save_snapshot.assert_called_once_with(self.current_snap)

    def test_unchanged_repository_short_circuit(self) -> None:
        """Verifies that an unchanged repository comparison short-circuits, skipping impact evaluation."""
        previous_snap = RepositorySnapshot(commit_id="c1", fingerprints={})
        self.persistence.get_snapshot.return_value = previous_snap

        cf = ChangedFile(path="src/a.py", change_type=ChangeType.UNCHANGED)
        self.diff_engine.diff_snapshots.return_value = (cf,)

        res = self.service.analyze_incrementally(
            project_id=self.project_id,
            project_name=self.project_name,
            repository_root=self.repo_root,
            source_commit="c1",
            target_commit="c2",
            dependency_graph=self.dependency_graph,
        )

        self.assertEqual(res.unchanged_count, 1)
        self.assertEqual(res.added_count, 0)
        # Impact analyzer should NOT be invoked
        self.impact_analyzer.analyze_impact.assert_not_called()

    def test_persistence_failure_propagation(self) -> None:
        """Verifies that persistence storage database failures propagate up unmodified."""
        cf = ChangedFile(path="src/a.py", change_type=ChangeType.ADDED)
        self.diff_engine.diff_snapshots.return_value = (cf,)
        self.persistence.save_result.side_effect = RuntimeError("DB Write Error")

        with self.assertRaises(RuntimeError) as ctx:
            self.service.analyze_incrementally(
                project_id=self.project_id,
                project_name=self.project_name,
                repository_root=self.repo_root,
                source_commit="c1",
                target_commit="c2",
                dependency_graph=self.dependency_graph,
            )
        self.assertEqual(str(ctx.exception), "DB Write Error")


if __name__ == "__main__":
    unittest.main()
