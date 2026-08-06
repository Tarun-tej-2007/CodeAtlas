"""Unit tests for the Architectural Trend Analyzer (ArchitecturalTrendAnalyzer)."""

import unittest
import uuid
from datetime import datetime, timezone, timedelta

from app.evolution import (
    ArchitecturalChange,
    ArchitecturalChangeType,
    ArchitecturalTrendAnalyzer,
    EvolutionMetadata,
    EvolutionResult,
    EvolutionStatus,
    EvolutionSummary,
    EvolutionValidationError,
)


class TestEvolutionTrendAnalyzer(unittest.TestCase):
    """Verifies that ArchitecturalTrendAnalyzer computes metrics trends and validation correctly."""

    def setUp(self) -> None:
        self.analyzer = ArchitecturalTrendAnalyzer()
        self.base_time = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)

    def create_dummy_result(
        self,
        created_offset_mins: int,
        target_commit: str,
        changes: list[ArchitecturalChange],
    ) -> EvolutionResult:
        """Helper to build an EvolutionResult DTO for timeline tests."""
        metadata = EvolutionMetadata(
            project_name="TrendProj",
            source_commit="commit_prev",
            target_commit=target_commit,
            created_at=self.base_time + timedelta(minutes=created_offset_mins),
            status=EvolutionStatus.COMPLETED,
        )
        summary = EvolutionSummary(added_count=1, removed_count=0, modified_count=0, unchanged_count=0)
        return EvolutionResult(
            evolution_id=uuid.uuid4(),
            metadata=metadata,
            changes=tuple(changes),
            summary=summary,
        )

    def test_empty_history(self) -> None:
        """Verifies empty history list returns stable and empty trends result DTO."""
        res = self.analyzer.analyze_trends(())
        self.assertEqual(res.coupling_trend, ())
        self.assertEqual(res.summary["coupling_trend"], "stable")

    def test_single_evolution_result(self) -> None:
        """Verifies analyzer handles single chronological evolution correctly."""
        changes = [
            ArchitecturalChange(
                component_name="architectural_metric:coupling",
                change_type=ArchitecturalChangeType.MODIFIED,
                metadata={"value": 0.4},
            )
        ]
        result = self.create_dummy_result(0, "c1", changes)

        res = self.analyzer.analyze_trends((result,))
        self.assertEqual(res.coupling_trend, (0.4,))
        self.assertEqual(res.summary["coupling_trend"], "stable")

    def test_chronological_ordering_validation_failure(self) -> None:
        """Verifies chronological ordering validation rejects retrogressive updates."""
        r1 = self.create_dummy_result(10, "c1", [])
        r2 = self.create_dummy_result(5, "c2", [])  # Created earlier than r1

        with self.assertRaises(EvolutionValidationError):
            self.analyzer.analyze_trends((r1, r2))

    def test_duplicate_history_elimination(self) -> None:
        """Verifies consecutive results targeting the same commit hash are ignored."""
        changes1 = [
            ArchitecturalChange(
                component_name="architectural_metric:coupling",
                change_type=ArchitecturalChangeType.MODIFIED,
                metadata={"value": 0.4},
            )
        ]
        changes2 = [
            ArchitecturalChange(
                component_name="architectural_metric:coupling",
                change_type=ArchitecturalChangeType.MODIFIED,
                metadata={"value": 0.6},
            )
        ]

        r1 = self.create_dummy_result(0, "c1", changes1)
        r2 = self.create_dummy_result(5, "c1", changes2)  # Duplicate commit "c1"

        res = self.analyzer.analyze_trends((r1, r2))
        # Second duplicate result should be omitted, yielding only a single metric
        self.assertEqual(res.coupling_trend, (0.4,))

    def test_metric_trend_directions(self) -> None:
        """Verifies that increasing, decreasing, and stable trends calculate correctly."""
        step1 = [
            ArchitecturalChange(
                component_name="architectural_metric:coupling",
                change_type=ArchitecturalChangeType.MODIFIED,
                metadata={"value": 0.4},
            ),
            # Tech Debt Total Items
            ArchitecturalChange(
                component_name="technical_debt:summary",
                change_type=ArchitecturalChangeType.MODIFIED,
                metadata={"total_items": 10},
            ),
            # Quality overall score
            ArchitecturalChange(
                component_name="quality_metrics:summary",
                change_type=ArchitecturalChangeType.MODIFIED,
                metadata={"overall_score": 90.0},
            ),
        ]
        step2 = [
            ArchitecturalChange(
                component_name="architectural_metric:coupling",
                change_type=ArchitecturalChangeType.MODIFIED,
                metadata={"value": 0.6},
            ),
            ArchitecturalChange(
                component_name="technical_debt:summary",
                change_type=ArchitecturalChangeType.MODIFIED,
                metadata={"total_items": 5},
            ),
            ArchitecturalChange(
                component_name="quality_metrics:summary",
                change_type=ArchitecturalChangeType.MODIFIED,
                metadata={"overall_score": 90.0},  # Stable
            ),
        ]

        r1 = self.create_dummy_result(0, "c1", step1)
        r2 = self.create_dummy_result(5, "c2", step2)

        res = self.analyzer.analyze_trends((r1, r2))

        # Coupling: 0.4 -> 0.6 => increasing
        self.assertEqual(res.coupling_trend, (0.4, 0.6))
        self.assertEqual(res.summary["coupling_trend"], "increasing")

        # Tech debt: 10 -> 5 => decreasing
        self.assertEqual(res.tech_debt_trend, (10, 5))
        self.assertEqual(res.summary["tech_debt_trend"], "decreasing")

        # Quality: 90.0 -> 90.0 => stable
        self.assertEqual(res.quality_trend, (90.0, 90.0))
        self.assertEqual(res.summary["quality_trend"], "stable")

    def test_module_growth_and_layer_stability(self) -> None:
        """Verifies that active module list accumulation tracks net delta growth correctly."""
        step1 = [
            ArchitecturalChange(component_name="module:a.py", change_type=ArchitecturalChangeType.ADDED),
            ArchitecturalChange(component_name="module:b.py", change_type=ArchitecturalChangeType.ADDED),
            ArchitecturalChange(component_name="layer:Domain", change_type=ArchitecturalChangeType.ADDED),
        ]
        step2 = [
            # Retain a.py, delete b.py, add c.py
            ArchitecturalChange(component_name="module:a.py", change_type=ArchitecturalChangeType.UNCHANGED),
            ArchitecturalChange(component_name="module:b.py", change_type=ArchitecturalChangeType.REMOVED),
            ArchitecturalChange(component_name="module:c.py", change_type=ArchitecturalChangeType.ADDED),
            # Layers remain unchanged
            ArchitecturalChange(component_name="layer:Domain", change_type=ArchitecturalChangeType.UNCHANGED),
        ]

        r1 = self.create_dummy_result(0, "c1", step1)
        r2 = self.create_dummy_result(5, "c2", step2)

        res = self.analyzer.analyze_trends((r1, r2))

        # Module counts: Step 1 (a, b) -> 2. Step 2 (a, c) -> 2 => stable
        self.assertEqual(res.module_growth, (2, 2))
        self.assertEqual(res.summary["module_growth"], "stable")

        # Layer count: Step 1 (Domain) -> 1. Step 2 (Domain) -> 1 => stable
        self.assertEqual(res.layer_stability, (1.0, 1.0))
        self.assertEqual(res.summary["layer_stability"], "stable")

    def test_large_history_window_limit(self) -> None:
        """Verifies configurable trailing history window sizes are respected."""
        history = []
        for i in range(10):
            changes = [
                ArchitecturalChange(
                    component_name="architectural_metric:coupling",
                    change_type=ArchitecturalChangeType.MODIFIED,
                    metadata={"value": float(i)},
                )
            ]
            history.append(self.create_dummy_result(i * 5, f"c{i}", changes))

        res = self.analyzer.analyze_trends(tuple(history), window_size=5)

        # Should only track the last 5 results (5, 6, 7, 8, 9)
        self.assertEqual(res.coupling_trend, (5.0, 6.0, 7.0, 8.0, 9.0))


if __name__ == "__main__":
    unittest.main()
