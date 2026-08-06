"""Unit tests for the production hardening aspects of Incremental Analysis."""

import logging
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
    FileFingerprint,
    IncrementalAnalysisMetadata,
    IncrementalAnalysisResult,
    IncrementalAnalysisValidationError,
    IncrementalAnalysisPersistenceError,
    IncrementalAnalysisFileSystemError,
    IncrementalAnalysisService,
    IncrementalAnalysisPersistence,
    IncrementalStatus,
    RepositorySnapshot,
    RepositorySnapshotService,
    SHA256SnapshotDifferenceEngine,
)
from app.incremental.cache import execution_cache


class TestIncrementalHardening(unittest.TestCase):
    """Verifies correlation ID propagation, exceptions translation, profiling metrics, and teardown safety."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.project_name = "HardenedProj"
        self.repo_root = "c:/Users/tarun/OneDrive/Desktop/projects/CodeAtlas/analysis-engine/app/tests/temp_dir"
        self.correlation_id = "test-correlation-12345"

        # Mock collaborators
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

        self.current_snap = RepositorySnapshot(commit_id="commit_target", fingerprints={})
        self.snapshot_service.create_snapshot.return_value = self.current_snap
        self.persistence.get_snapshot.return_value = None

        # Capture logs
        self.log_handler = LoggerCaptureHandler()
        logging.getLogger("analysis-engine.incremental").addHandler(self.log_handler)
        logging.getLogger("analysis-engine.incremental").setLevel(logging.INFO)

    def tearDown(self) -> None:
        logging.getLogger("analysis-engine.incremental").removeHandler(self.log_handler)
        execution_cache.set(None)

    def test_correlation_id_propagation_and_logging(self) -> None:
        """Verifies correlation ID propagates through metadata and logs contain structured details."""
        cf = ChangedFile(path="src/a.py", change_type=ChangeType.ADDED)
        self.diff_engine.diff_snapshots.return_value = (cf,)

        res = self.service.analyze_incrementally(
            project_id=self.project_id,
            project_name=self.project_name,
            repository_root=self.repo_root,
            source_commit="c1",
            target_commit="c2",
            dependency_graph=self.dependency_graph,
            correlation_id=self.correlation_id,
        )

        # 1. Metadata check
        self.assertEqual(res.metadata.extra_info.get("correlation_id"), self.correlation_id)

        # 2. Logs verification
        logs = self.log_handler.messages
        self.assertTrue(any(self.correlation_id in msg for msg in logs))
        self.assertTrue(any("Stage 1" in msg for msg in logs))
        self.assertTrue(any("Completed incremental analysis" in msg for msg in logs))

    def test_metrics_collection(self) -> None:
        """Verifies duration metric timing calculations are recorded correctly in response."""
        cf = ChangedFile(path="src/a.py", change_type=ChangeType.UNCHANGED)
        self.diff_engine.diff_snapshots.return_value = (cf,)

        res = self.service.analyze_incrementally(
            project_id=self.project_id,
            project_name=self.project_name,
            repository_root=self.repo_root,
            source_commit="c1",
            target_commit="c2",
            dependency_graph=self.dependency_graph,
            correlation_id=self.correlation_id,
        )

        metrics = res.metadata.extra_info.get("metrics")
        self.assertIsNotNone(metrics)
        self.assertIn("snapshot_generation_ms", metrics)
        self.assertIn("change_detection_ms", metrics)
        self.assertIn("dependency_impact_analysis_ms", metrics)
        self.assertIn("persistence_ms", metrics)
        self.assertIn("total_orchestration_ms", metrics)

    def test_persistence_failure_translation(self) -> None:
        """Verifies persistence errors map to IncrementalAnalysisPersistenceError."""
        # Cause database read failure during get_snapshot
        self.persistence.get_snapshot.side_effect = RuntimeError("DB Query Failure")

        with self.assertRaises(IncrementalAnalysisPersistenceError):
            self.service.analyze_incrementally(
                project_id=self.project_id,
                project_name=self.project_name,
                repository_root=self.repo_root,
                source_commit="c1",
                target_commit="c2",
                dependency_graph=self.dependency_graph,
            )

    def test_filesystem_failure_translation(self) -> None:
        """Verifies transient file errors map to IncrementalAnalysisFileSystemError."""
        self.snapshot_service.create_snapshot.side_effect = PermissionError("Access Denied")

        with self.assertRaises(IncrementalAnalysisFileSystemError):
            self.service.analyze_incrementally(
                project_id=self.project_id,
                project_name=self.project_name,
                repository_root=self.repo_root,
                source_commit="c1",
                target_commit="c2",
                dependency_graph=self.dependency_graph,
            )

    def test_resource_cleanup_on_failure(self) -> None:
        """Verifies context cache tokens are safely cleared even during pipeline failures."""
        self.snapshot_service.create_snapshot.side_effect = RuntimeError("Crash")

        with self.assertRaises(Exception):
            self.service.analyze_incrementally(
                project_id=self.project_id,
                project_name=self.project_name,
                repository_root=self.repo_root,
                source_commit="c1",
                target_commit="c2",
                dependency_graph=self.dependency_graph,
            )

        # Cache must be released and evaluate to None
        self.assertIsNone(execution_cache.get())


class LoggerCaptureHandler(logging.Handler):
    """Logging handler recording all logged warning/info strings."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(self.format(record))
