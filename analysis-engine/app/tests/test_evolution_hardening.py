"""Unit and integration tests for the production hardening aspects of Architecture Evolution."""

import logging
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.evolution import (
    ArchitecturalChange,
    ArchitecturalChangeType,
    ArchitecturalRiskReport,
    ArchitectureSnapshot,
    ArchitectureSnapshotCalculator,
    ArchitectureEvolutionResult,
    ArchitectureEvolutionService,
    EvolutionDifferenceEngine,
    EvolutionMetadata,
    EvolutionPersistence,
    EvolutionRequest,
    EvolutionResult,
    EvolutionStatus,
    EvolutionSummary,
    EvolutionTrendResult,
    EvolutionValidationError,
    EvolutionPersistenceError,
    EvolutionFileSystemError,
    RiskAnalyzer,
    TrendAnalyzer,
    execution_cache,
)


class LoggerCaptureHandler(logging.Handler):
    """Logging handler recording all logged message strings."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(self.format(record))


class TestEvolutionHardening(unittest.TestCase):
    """Verifies structured logging, timing metrics tracking, exception translation, and context releases."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.project_name = "HardenedOrch"
        self.correlation_id = "evolution-corr-abc-123"
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)

        # Mock dependencies
        self.snapshot_calc = MagicMock(spec=ArchitectureSnapshotCalculator)
        self.diff_engine = MagicMock(spec=EvolutionDifferenceEngine)
        self.trend_analyzer = MagicMock(spec=TrendAnalyzer)
        self.risk_analyzer = MagicMock(spec=RiskAnalyzer)
        self.persistence = MagicMock(spec=EvolutionPersistence)

        self.service = ArchitectureEvolutionService(
            snapshot_calculator=self.snapshot_calc,
            difference_engine=self.diff_engine,
            trend_analyzer=self.trend_analyzer,
            risk_analyzer=self.risk_analyzer,
            persistence=self.persistence,
        )

        self.request = EvolutionRequest(
            project_id=self.project_id,
            project_name=self.project_name,
            source_commit="c1",
            target_commit="c2",
            correlation_id=self.correlation_id,
        )

        # Setup standard mock outputs
        self.current_snap = ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id="c2",
            timestamp=self.time_utc,
            layers=(),
            components={},
        )
        self.prev_snap = ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id="c1",
            timestamp=self.time_utc,
            layers=(),
            components={},
        )
        self.changes = (
            ArchitecturalChange(
                component_name="module:a.py",
                change_type=ArchitecturalChangeType.ADDED,
            ),
        )

        self.snapshot_calc.calculate_snapshot.return_value = self.current_snap
        self.persistence.get_snapshot.return_value = self.prev_snap
        self.persistence.list_results.return_value = ()
        self.diff_engine.diff_snapshots.return_value = self.changes

        # Register capture log handler
        self.log_handler = LoggerCaptureHandler()
        logging.getLogger("analysis-engine.evolution").addHandler(self.log_handler)
        logging.getLogger("analysis-engine.evolution").setLevel(logging.INFO)

    def tearDown(self) -> None:
        logging.getLogger("analysis-engine.evolution").removeHandler(self.log_handler)
        execution_cache.set(None)

    def test_correlation_id_propagation_and_logging(self) -> None:
        """Verifies correlation ID is tracked inside extra_info and recorded throughout service logging statements."""
        res = self.service.evolve_architecture(self.request)

        self.assertEqual(res.extra_info.get("correlation_id"), self.correlation_id)

        # Check logs contain correlation ID prefix
        logs = self.log_handler.messages
        self.assertTrue(any(self.correlation_id in msg for msg in logs))
        self.assertTrue(any("Stage 1" in msg for msg in logs))
        self.assertTrue(any("Completed architecture evolution" in msg for msg in logs))

    def test_metrics_collection(self) -> None:
        """Verifies duration metric timing values are populated in output response dictionary."""
        # Setup history mock to trigger full workflow execution
        hist_meta = EvolutionMetadata(
            project_name=self.project_name,
            source_commit="c0",
            target_commit="c1",
            created_at=self.time_utc,
            status=EvolutionStatus.COMPLETED,
        )
        hist_res = EvolutionResult(
            evolution_id=uuid.uuid4(),
            metadata=hist_meta,
            changes=(),
            summary=EvolutionSummary(added_count=0, removed_count=0, modified_count=0, unchanged_count=0),
        )
        self.persistence.list_results.return_value = (hist_res,)

        mock_trends = EvolutionTrendResult(
            coupling_trend=(),
            complexity_trend=(),
            tech_debt_trend=(),
            quality_trend=(),
            layer_stability=(),
            module_growth=(),
            summary={},
        )
        mock_report = ArchitecturalRiskReport(
            report_id=uuid.uuid4(),
            generated_at=self.time_utc,
            overall_risk_score=0.0,
            risks=(),
        )
        self.trend_analyzer.analyze_trends.return_value = mock_trends
        self.risk_analyzer.analyze_risks.return_value = mock_report

        res = self.service.evolve_architecture(self.request)

        metrics = res.extra_info.get("metrics")
        self.assertIsNotNone(metrics)
        self.assertIn("snapshot_generation_ms", metrics)
        self.assertIn("architecture_comparison_ms", metrics)
        self.assertIn("trend_analysis_ms", metrics)
        self.assertIn("risk_analysis_ms", metrics)
        self.assertIn("persistence_ms", metrics)
        self.assertIn("total_orchestration_ms", metrics)

    def test_persistence_failure_translation(self) -> None:
        """Verifies database transient errors translate into EvolutionPersistenceError wrapper."""
        self.persistence.get_snapshot.side_effect = RuntimeError("Sqlite IO Timeout error")

        with self.assertRaises(EvolutionPersistenceError):
            self.service.evolve_architecture(self.request)

    def test_filesystem_failure_translation(self) -> None:
        """Verifies snapshot building transient scan faults translate to EvolutionFileSystemError."""
        self.snapshot_calc.calculate_snapshot.side_effect = PermissionError("EACCES Denied")

        with self.assertRaises(EvolutionFileSystemError):
            self.service.evolve_architecture(self.request)

    def test_resource_cleanup_on_success(self) -> None:
        """Verifies execution cache is released when processing succeeds."""
        self.service.evolve_architecture(self.request)
        self.assertIsNone(execution_cache.get())

    def test_resource_cleanup_on_failure(self) -> None:
        """Verifies execution cache is released even when workflow throws exception."""
        self.snapshot_calc.calculate_snapshot.side_effect = RuntimeError("Panic")

        with self.assertRaises(Exception):
            self.service.evolve_architecture(self.request)

        self.assertIsNone(execution_cache.get())


if __name__ == "__main__":
    unittest.main()
