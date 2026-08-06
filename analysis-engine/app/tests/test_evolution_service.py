"""Unit tests for the Architecture Evolution Orchestrator (ArchitectureEvolutionService)."""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.evolution import (
    ArchitecturalChange,
    ArchitecturalChangeType,
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
    RiskAnalyzer,
    TrendAnalyzer,
    ArchitecturalRiskReport,
)


class TestEvolutionService(unittest.TestCase):
    """Verifies workflow orchestration, short-circuit boundaries, and error translation safeguards."""

    def setUp(self) -> None:
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
            project_id=uuid.uuid4(),
            project_name="OrchProj",
            source_commit="c1",
            target_commit="c2",
        )

        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)
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

        self.snapshot_calc.calculate_snapshot.return_value = self.current_snap
        self.persistence.get_snapshot.return_value = self.prev_snap
        self.persistence.list_results.return_value = ()

        self.changes = (
            ArchitecturalChange(
                component_name="module:a.py",
                change_type=ArchitecturalChangeType.ADDED,
            ),
        )
        self.diff_engine.diff_snapshots.return_value = self.changes

    def test_constructor_dependency_injection_safeguards(self) -> None:
        """Verifies validations on null dependencies during instantiations."""
        with self.assertRaises(ValueError):
            ArchitectureEvolutionService(
                snapshot_calculator=None,  # type: ignore
                difference_engine=self.diff_engine,
                trend_analyzer=self.trend_analyzer,
                risk_analyzer=self.risk_analyzer,
                persistence=self.persistence,
            )

    def test_first_time_evolution_short_circuits_analysis(self) -> None:
        """Verifies that if no previous snapshot exists, the orchestrator short-circuits trend/risk metrics."""
        self.persistence.get_snapshot.return_value = None  # First time

        res = self.service.evolve_architecture(self.request)

        self.assertIsNone(res.previous_snapshot)
        self.assertIsNone(res.trends)
        self.assertIsNone(res.risk_report)
        self.assertEqual(res.summary.added_count, 1)

    def test_single_historical_record_short_circuits_analysis(self) -> None:
        """Verifies trend analysis is skipped if only one chronological record (current run) is present."""
        self.persistence.get_snapshot.return_value = self.prev_snap
        self.persistence.list_results.return_value = ()  # No history yet

        res = self.service.evolve_architecture(self.request)

        # 1 result total -> insufficient history (requires >= 2 results)
        self.assertIsNone(res.trends)
        self.assertIsNone(res.risk_report)

    def test_multi_snapshot_workflow_orchestration(self) -> None:
        """Verifies full execution mapping when sufficient history exists."""
        self.persistence.get_snapshot.return_value = self.prev_snap

        # Populate a single mock history item (2 items total with current run)
        hist_meta = EvolutionMetadata(
            project_name="OrchProj",
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
        mock_risk_report = ArchitecturalRiskReport(
            report_id=uuid.uuid4(),
            generated_at=datetime.now(timezone.utc),
            overall_risk_score=0.0,
            risks=(),
        )
        self.trend_analyzer.analyze_trends.return_value = mock_trends
        self.risk_analyzer.analyze_risks.return_value = mock_risk_report

        res = self.service.evolve_architecture(self.request)

        self.assertIsNotNone(res.trends)
        self.assertIsNotNone(res.risk_report)
        self.trend_analyzer.analyze_trends.assert_called_once()
        self.risk_analyzer.analyze_risks.assert_called_once_with(mock_trends)

    def test_collaborator_exception_translations(self) -> None:
        """Verifies exceptions in sub-engines map to EvolutionValidationError."""
        # 1. Snapshot calculator error
        self.snapshot_calc.calculate_snapshot.side_effect = RuntimeError("Disk IO Error")
        with self.assertRaises(EvolutionValidationError) as ctx:
            self.service.evolve_architecture(self.request)
        self.assertIn("Snapshot building failed", str(ctx.exception))

        # Reset calculator mock
        self.snapshot_calc.calculate_snapshot.side_effect = None

        # 2. Diff engine error
        self.diff_engine.diff_snapshots.side_effect = TypeError("Data corruption")
        with self.assertRaises(EvolutionValidationError) as ctx2:
            self.service.evolve_architecture(self.request)
        self.assertIn("Snapshot comparison failed", str(ctx2.exception))


if __name__ == "__main__":
    unittest.main()
