"""Unit tests for the Architecture Snapshot Builder (ArchitectureSnapshotService)."""

import unittest
import uuid
from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock

from pydantic import BaseModel, Field

from app.evolution import (
    ArchitectureAnalysisProvider,
    ArchitectureSnapshotService,
    EvolutionValidationError,
)


# Minimal dummy domain classes matching actual platform models for test mocking
class DummyNode(BaseModel):
    id: str
    type: Any = None


class DummyEdge(BaseModel):
    source_id: str
    target_id: str
    type: Any = None


class DummyGraph(BaseModel):
    nodes: list[Any] = Field(default_factory=list)
    edges: list[Any] = Field(default_factory=list)


class DummyLayer(BaseModel):
    name: str


class DummyMetric(BaseModel):
    name: str
    value: float
    unit: str
    level: Any = None


class DummyArchResult(BaseModel):
    layers: list[Any] = Field(default_factory=list)
    metrics: list[Any] = Field(default_factory=list)


class DummyQualitySummary(BaseModel):
    overall_score: float
    overall_level: Any
    metrics_by_category: dict[Any, float] = Field(default_factory=dict)


class DummyQualityReport(BaseModel):
    summary: Any
    metrics: list[Any] = Field(default_factory=list)


class DummyTechDebtItem(BaseModel):
    id: str
    title: str
    category: Any
    severity: Any
    effort_minutes: int


class DummyTechDebtSummary(BaseModel):
    total_items: int
    total_effort_minutes: int
    items_by_category: dict[Any, int] = Field(default_factory=dict)
    effort_by_severity: dict[Any, int] = Field(default_factory=dict)


class DummyTechDebtReport(BaseModel):
    summary: Any
    items: list[Any] = Field(default_factory=list)


class TestEvolutionSnapshotBuilder(unittest.TestCase):
    """Verifies that ArchitectureSnapshotService compiles structural models deterministically."""

    def setUp(self) -> None:
        self.mock_provider = MagicMock(spec=ArchitectureAnalysisProvider)
        self.service = ArchitectureSnapshotService(provider=self.mock_provider)
        self.commit_id = "test_commit_hash_123"

        # Setup standard mock objects
        # Dummy node types
        self.module_type = MagicMock()
        self.module_type.value = "module"

        self.class_type = MagicMock()
        self.class_type.value = "class"

        # Mock dependency graph
        self.nodes = [
            DummyNode(id="src\\components\\button.py", type=self.module_type),
            DummyNode(id="src\\utils.py", type=self.module_type),
            DummyNode(id="ButtonClass", type=self.class_type),
        ]
        self.edges = [
            DummyEdge(source_id="src\\components\\button.py", target_id="ButtonClass")
        ]
        self.graph = DummyGraph(nodes=self.nodes, edges=self.edges)

        # Mock architecture result
        self.layers = [DummyLayer(name="UI"), DummyLayer(name="Core")]
        self.arch_metrics = [
            DummyMetric(name="Coupling", value=0.45, unit="ratio"),
            DummyMetric(name="Cohesion", value=0.8, unit="ratio"),
        ]
        self.arch_result = DummyArchResult(layers=self.layers, metrics=self.arch_metrics)

        # Mock quality report
        self.quality_level = MagicMock()
        self.quality_level.value = "high"
        self.cat_mock = MagicMock()
        self.cat_mock.value = "complexity"

        self.quality_summary = DummyQualitySummary(
            overall_score=88.5,
            overall_level=self.quality_level,
            metrics_by_category={self.cat_mock: 12.0},
        )
        self.quality_metrics = [
            DummyMetric(name="Complexity", value=12.0, unit="lines"),
            DummyMetric(name="Duplication", value=2.5, unit="percent"),
        ]
        # Map quality level to dummy metrics
        for m in self.quality_metrics:
            m.level = self.quality_level
        self.quality_report = DummyQualityReport(
            summary=self.quality_summary, metrics=self.quality_metrics
        )

        # Mock technical debt report
        self.td_cat = MagicMock()
        self.td_cat.value = "code_smell"
        self.td_sev = MagicMock()
        self.td_sev.value = "major"

        self.td_summary = DummyTechDebtSummary(
            total_items=1,
            total_effort_minutes=30,
            items_by_category={self.td_cat: 1},
            effort_by_severity={self.td_sev: 30},
        )
        self.td_items = [
            DummyTechDebtItem(
                id="TD01",
                title="Large Class",
                category=self.td_cat,
                severity=self.td_sev,
                effort_minutes=30,
            )
        ]
        self.td_report = DummyTechDebtReport(summary=self.td_summary, items=self.td_items)

        # Assign standard returns
        self.mock_provider.get_dependency_graph.return_value = self.graph
        self.mock_provider.get_architecture_result.return_value = self.arch_result
        self.mock_provider.get_quality_report.return_value = self.quality_report
        self.mock_provider.get_technical_debt_report.return_value = self.td_report

    def test_dependency_injection_behavior(self) -> None:
        """Verifies validator constructor validation behaviors."""
        with self.assertRaises(ValueError):
            ArchitectureSnapshotService(provider=None)  # type: ignore

        with self.assertRaises(TypeError):
            ArchitectureSnapshotService(provider="invalid_type")  # type: ignore

    def test_empty_repository(self) -> None:
        """Verifies calculation on empty codebase analysis returns clean initialized defaults."""
        empty_graph = DummyGraph(nodes=[], edges=[])
        self.mock_provider.get_dependency_graph.return_value = empty_graph
        self.mock_provider.get_architecture_result.return_value = None
        self.mock_provider.get_quality_report.return_value = None
        self.mock_provider.get_technical_debt_report.return_value = None

        snap = self.service.calculate_snapshot(self.commit_id)

        self.assertEqual(snap.commit_id, self.commit_id)
        self.assertEqual(snap.layers, ())
        self.assertEqual(snap.components["modules"], [])
        self.assertEqual(snap.components["dependency_graph_metadata"]["node_count"], 0)
        self.assertEqual(snap.components["dependency_graph_metadata"]["edge_count"], 0)
        self.assertEqual(snap.components["architectural_metrics"], [])

    def test_single_module_repository(self) -> None:
        """Verifies correct calculation on a single module dataset."""
        single_node = [DummyNode(id="main.py", type=self.module_type)]
        self.mock_provider.get_dependency_graph.return_value = DummyGraph(nodes=single_node)
        self.mock_provider.get_architecture_result.return_value = None
        self.mock_provider.get_quality_report.return_value = None
        self.mock_provider.get_technical_debt_report.return_value = None

        snap = self.service.calculate_snapshot(self.commit_id)
        self.assertEqual(snap.components["modules"], ["main.py"])

    def test_multi_module_normalization_and_sorting(self) -> None:
        """Verifies normalization of backslashes and alphabetical component ordering."""
        snap = self.service.calculate_snapshot(self.commit_id)

        # Expected normalized paths (backslashes converted to forward slashes) and sorted
        expected_modules = ["src/components/button.py", "src/utils.py"]
        self.assertEqual(snap.components["modules"], expected_modules)

        # Expected sorted layers
        self.assertEqual(snap.layers, ("Core", "UI"))

    def test_large_repository_scalability(self) -> None:
        """Verifies snapshot building executes quickly for large node collections."""
        large_nodes = [
            DummyNode(id=f"src/file_{i}.py", type=self.module_type)
            for i in range(1000)
        ]
        self.mock_provider.get_dependency_graph.return_value = DummyGraph(nodes=large_nodes)

        import time
        start = time.perf_counter()
        snap = self.service.calculate_snapshot(self.commit_id)
        elapsed = time.perf_counter() - start

        self.assertEqual(len(snap.components["modules"]), 1000)
        self.assertLess(elapsed, 0.2)  # Typically resolves in < 50ms

    def test_deterministic_generation_across_repeated_runs(self) -> None:
        """Verifies snapshot results are identical for identical inputs regardless of execution runs."""
        snap1 = self.service.calculate_snapshot(self.commit_id)
        snap2 = self.service.calculate_snapshot(self.commit_id)

        # Content of components should match exactly
        self.assertEqual(snap1.components["modules"], snap2.components["modules"])
        self.assertEqual(snap1.components["architectural_metrics"], snap2.components["architectural_metrics"])
        self.assertEqual(snap1.layers, snap2.layers)

    def test_validation_failures_on_invalid_commit(self) -> None:
        """Verifies validator raises exception on empty or blank commit hashes."""
        with self.assertRaises(EvolutionValidationError):
            self.service.calculate_snapshot("")

        with self.assertRaises(EvolutionValidationError):
            self.service.calculate_snapshot("   ")

    def test_edge_cases_incomplete_analysis_corruption(self) -> None:
        """Verifies validator catches corrupt report objects and throws validation error."""
        # Corrupt dependency graph without nodes attribute
        corrupt_graph = MagicMock()
        del corrupt_graph.nodes
        self.mock_provider.get_dependency_graph.return_value = corrupt_graph

        with self.assertRaises(EvolutionValidationError):
            self.service.calculate_snapshot(self.commit_id)


if __name__ == "__main__":
    unittest.main()
