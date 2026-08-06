"""Unit and performance integration tests for the Architecture Evolution caching layers."""

import time
import unittest
import uuid
from datetime import datetime, timezone

from app.evolution import (
    ArchitecturalChange,
    ArchitecturalChangeType,
    ArchitecturalRisk,
    ArchitecturalRiskReport,
    ArchitectureSnapshot,
    ArchitectureSnapshotService,
    ArchitectureEvolutionDifferenceEngine,
    ArchitecturalTrendAnalyzer,
    CodeAtlasArchitecturalRiskAnalyzer,
    EvolutionMetadata,
    EvolutionRequest,
    EvolutionResult,
    EvolutionStatus,
    EvolutionSummary,
    EvolutionTrendResult,
    execution_cache,
    ArchitectureAnalysisProvider,
)


class DummyAnalysisProvider(ArchitectureAnalysisProvider):
    def __init__(self) -> None:
        self.call_count = 0

    def get_dependency_graph(self, commit_id: str):
        self.call_count += 1
        return None

    def get_architecture_result(self, commit_id: str):
        return None

    def get_quality_report(self, commit_id: str):
        return None

    def get_technical_debt_report(self, commit_id: str):
        return None


class TestEvolutionPerformance(unittest.TestCase):
    """Verifies cache hits, lifecycle limits, cleanups between queries, and regression checks."""

    def setUp(self) -> None:
        # Reset the ContextVar before each test
        self.token = execution_cache.set(None)

    def tearDown(self) -> None:
        execution_cache.reset(self.token)

    def test_snapshot_cache_reuse(self) -> None:
        """Verifies duplicate snapshot requests retrieve pre-computed snapshots from cache without invoking provider."""
        provider = DummyAnalysisProvider()
        calculator = ArchitectureSnapshotService(provider)

        # Set up active cache
        token = execution_cache.set({})
        try:
            # First calculate
            snap1 = calculator.calculate_snapshot("commit1")
            self.assertEqual(provider.call_count, 1)

            # Second calculate of identical commit
            snap2 = calculator.calculate_snapshot("commit1")
            self.assertEqual(provider.call_count, 1)  # Provider count is still 1
            self.assertIs(snap1, snap2)
        finally:
            execution_cache.reset(token)

    def test_comparison_cache_reuse(self) -> None:
        """Verifies identical snapshot comparisons return cached changes list directly."""
        engine = ArchitectureEvolutionDifferenceEngine()
        time_utc = datetime.now(timezone.utc)
        s1 = ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id="c1",
            timestamp=time_utc,
            layers=(),
            components={},
        )
        s2 = ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id="c2",
            timestamp=time_utc,
            layers=(),
            components={},
        )

        token = execution_cache.set({})
        try:
            res1 = engine.diff_snapshots(s1, s2)
            res2 = engine.diff_snapshots(s1, s2)
            self.assertIs(res1, res2)
        finally:
            execution_cache.reset(token)

    def test_trend_cache_reuse(self) -> None:
        """Verifies duplicate trend requests return cached trend outputs."""
        analyzer = ArchitecturalTrendAnalyzer()
        meta = EvolutionMetadata(
            project_name="TrendProj",
            source_commit="c1",
            target_commit="c2",
            created_at=datetime.now(timezone.utc),
            status=EvolutionStatus.COMPLETED,
        )
        res = EvolutionResult(
            evolution_id=uuid.uuid4(),
            metadata=meta,
            changes=(),
            summary=EvolutionSummary(added_count=0, removed_count=0, modified_count=0, unchanged_count=0),
        )
        history = (res,)

        token = execution_cache.set({})
        try:
            t1 = analyzer.analyze_trends(history)
            t2 = analyzer.analyze_trends(history)
            self.assertIs(t1, t2)
        finally:
            execution_cache.reset(token)

    def test_risk_cache_reuse(self) -> None:
        """Verifies duplicate risk analyses retrieve cached risk reports."""
        analyzer = CodeAtlasArchitecturalRiskAnalyzer()
        trend = EvolutionTrendResult(
            coupling_trend=(0.1,),
            complexity_trend=(1.0,),
            tech_debt_trend=(5,),
            quality_trend=(90.0,),
            layer_stability=(1.0,),
            module_growth=(5,),
            summary={},
        )

        token = execution_cache.set({})
        try:
            r1 = analyzer.analyze_risks(trend)
            r2 = analyzer.analyze_risks(trend)
            self.assertIs(r1, r2)
        finally:
            execution_cache.reset(token)

    def test_cache_invalidation_between_runs(self) -> None:
        """Verifies cache does not leak across different evolution execution boundaries."""
        provider = DummyAnalysisProvider()
        calculator = ArchitectureSnapshotService(provider)

        # 1. Run in context A
        tokenA = execution_cache.set({})
        try:
            calculator.calculate_snapshot("commit1")
            self.assertEqual(provider.call_count, 1)
        finally:
            execution_cache.reset(tokenA)

        # 2. Run in context B (should call provider since cache was invalidated)
        tokenB = execution_cache.set({})
        try:
            calculator.calculate_snapshot("commit1")
            self.assertEqual(provider.call_count, 2)
        finally:
            execution_cache.reset(tokenB)


if __name__ == "__main__":
    unittest.main()
