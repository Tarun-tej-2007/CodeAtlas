"""Unit tests for the Architecture Evolution Difference Engine (ArchitectureEvolutionDifferenceEngine)."""

import unittest
import uuid
from datetime import datetime, timezone

from app.evolution import (
    ArchitecturalChangeType,
    ArchitectureEvolutionDifferenceEngine,
    ArchitectureSnapshot,
    EvolutionValidationError,
)


class TestEvolutionDiffEngine(unittest.TestCase):
    """Verifies delta detection correctness and alphabetical determinism across snapshot versions."""

    def setUp(self) -> None:
        self.engine = ArchitectureEvolutionDifferenceEngine()
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)

    def create_dummy_snapshot(
        self,
        commit_id: str,
        modules: list[str],
        layers: tuple[str, ...] = (),
        graph_meta: dict = None,
        arch_metrics: list = None,
        quality_metrics: dict = None,
        tech_debt: dict = None,
    ) -> ArchitectureSnapshot:
        """Helper to create ArchitectureSnapshot objects populated with test parameters."""
        components = {
            "modules": modules,
            "dependency_graph_metadata": graph_meta or {"node_count": 0, "edge_count": 0},
            "architectural_metrics": arch_metrics or [],
            "quality_metrics": quality_metrics or {
                "overall_score": 100.0,
                "overall_level": "optimal",
                "metrics": [],
            },
            "technical_debt_metrics": tech_debt or {
                "total_items": 0,
                "total_effort_minutes": 0,
                "items": [],
            },
        }
        return ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id=commit_id,
            timestamp=self.time_utc,
            layers=layers,
            components=components,
        )

    def test_empty_vs_empty_snapshots(self) -> None:
        """Verifies comparison of two empty snapshots generates expected unmodified metadata."""
        snap1 = self.create_dummy_snapshot("c1", [])
        snap2 = self.create_dummy_snapshot("c2", [])

        changes = self.engine.diff_snapshots(snap1, snap2)

        # We expect only unchanged dependency_graph and quality_metrics:summary
        names = [c.component_name for c in changes]
        self.assertIn("dependency_graph", names)
        self.assertIn("quality_metrics:summary", names)
        self.assertIn("technical_debt:summary", names)

    def test_empty_vs_populated_snapshots(self) -> None:
        """Verifies comparison resolves all added components."""
        snap1 = self.create_dummy_snapshot("c1", [])
        snap2 = self.create_dummy_snapshot(
            "c2",
            modules=["main.py"],
            layers=("Domain",),
            arch_metrics=[{"name": "Coupling", "value": 0.5}],
        )

        changes = self.engine.diff_snapshots(snap1, snap2)

        added = [c for c in changes if c.change_type == ArchitecturalChangeType.ADDED]
        added_names = [c.component_name for c in added]

        self.assertIn("module:main.py", added_names)
        self.assertIn("layer:Domain", added_names)
        self.assertIn("architectural_metric:Coupling", added_names)

    def test_identical_snapshots(self) -> None:
        """Verifies identical snapshots yield only unchanged types."""
        snap1 = self.create_dummy_snapshot("c1", ["main.py"])
        snap2 = self.create_dummy_snapshot("c2", ["main.py"])

        changes = self.engine.diff_snapshots(snap1, snap2)

        for c in changes:
            # None of the changes should be ADDED or REMOVED
            self.assertNotEqual(c.change_type, ArchitecturalChangeType.ADDED)
            self.assertNotEqual(c.change_type, ArchitecturalChangeType.REMOVED)

    def test_added_and_removed_modules(self) -> None:
        """Verifies added and removed modules generate correct change classifications."""
        snap1 = self.create_dummy_snapshot("c1", ["a.py", "b.py"])
        snap2 = self.create_dummy_snapshot("c2", ["b.py", "c.py"])

        changes = self.engine.diff_snapshots(snap1, snap2)

        added = [c for c in changes if c.change_type == ArchitecturalChangeType.ADDED]
        removed = [c for c in changes if c.change_type == ArchitecturalChangeType.REMOVED]

        self.assertEqual(len(added), 1)
        self.assertEqual(added[0].component_name, "module:c.py")

        self.assertEqual(len(removed), 1)
        self.assertEqual(removed[0].component_name, "module:a.py")

    def test_dependency_graph_and_layer_changes(self) -> None:
        """Verifies node/edge metric differentials raise modified dependency graph logs."""
        snap1 = self.create_dummy_snapshot(
            "c1", [], layers=("Core",), graph_meta={"node_count": 5, "edge_count": 10}
        )
        snap2 = self.create_dummy_snapshot(
            "c2", [], layers=("Core", "UI"), graph_meta={"node_count": 6, "edge_count": 12}
        )

        changes = self.engine.diff_snapshots(snap1, snap2)

        # Graph node difference -> MODIFIED
        g_change = [c for c in changes if c.component_name == "dependency_graph"][0]
        self.assertEqual(g_change.change_type, ArchitecturalChangeType.MODIFIED)

        # Layer UI addition -> ADDED
        ui_change = [c for c in changes if c.component_name == "layer:UI"][0]
        self.assertEqual(ui_change.change_type, ArchitecturalChangeType.ADDED)

    def test_metric_changes(self) -> None:
        """Verifies value differences across all three metric categories."""
        # Setup Quality metrics
        q1 = {
            "overall_score": 90.0,
            "overall_level": "optimal",
            "metrics": [{"name": "C1", "value": 1.0}],
        }
        q2 = {
            "overall_score": 85.0,
            "overall_level": "good",
            "metrics": [{"name": "C1", "value": 2.0}],
        }

        # Setup Tech Debt
        td1 = {
            "total_items": 1,
            "total_effort_minutes": 10,
            "items": [{"id": "T1", "title": "Smell", "effort_minutes": 10}],
        }
        td2 = {
            "total_items": 1,
            "total_effort_minutes": 20,
            "items": [{"id": "T1", "title": "Smell", "effort_minutes": 20}],
        }

        # Setup Arch Metrics
        am1 = [{"name": "A1", "value": 5.0, "unit": "count"}]
        am2 = [{"name": "A1", "value": 6.0, "unit": "count"}]

        snap1 = self.create_dummy_snapshot("c1", [], arch_metrics=am1, quality_metrics=q1, tech_debt=td1)
        snap2 = self.create_dummy_snapshot("c2", [], arch_metrics=am2, quality_metrics=q2, tech_debt=td2)

        changes = self.engine.diff_snapshots(snap1, snap2)

        modified = [c.component_name for c in changes if c.change_type == ArchitecturalChangeType.MODIFIED]

        self.assertIn("architectural_metric:A1", modified)
        self.assertIn("quality_metrics:summary", modified)
        self.assertIn("quality_metric:C1", modified)
        self.assertIn("technical_debt:summary", modified)
        self.assertIn("technical_debt_item:T1", modified)

    def test_deterministic_ordering(self) -> None:
        """Verifies changes list is strictly sorted alphabetically by component name."""
        snap1 = self.create_dummy_snapshot("c1", ["z.py", "a.py"])
        snap2 = self.create_dummy_snapshot("c2", ["z.py", "a.py"])

        changes = self.engine.diff_snapshots(snap1, snap2)

        names = [c.component_name for c in changes]
        # Assert names list matches its sorted version
        self.assertEqual(names, sorted(names))

    def test_validation_failures_on_null_inputs(self) -> None:
        """Verifies validation exceptions are raised when compared objects are null."""
        snap = self.create_dummy_snapshot("c1", [])
        with self.assertRaises(EvolutionValidationError):
            self.engine.diff_snapshots(snap, None)  # type: ignore

        with self.assertRaises(EvolutionValidationError):
            self.engine.diff_snapshots(None, snap)  # type: ignore

    def test_large_repository_diff_performance(self) -> None:
        """Verifies fast diff comparisons with large file sets."""
        snap1 = self.create_dummy_snapshot("c1", [f"file_{i}.py" for i in range(1000)])
        snap2 = self.create_dummy_snapshot("c2", [f"file_{i}.py" for i in range(1000)])

        import time
        start = time.perf_counter()
        changes = self.engine.diff_snapshots(snap1, snap2)
        elapsed = time.perf_counter() - start

        self.assertLess(elapsed, 0.2)  # Under 200ms
        self.assertGreater(len(changes), 1000)


if __name__ == "__main__":
    unittest.main()
