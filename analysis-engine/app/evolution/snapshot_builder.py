"""Concrete implementation of ArchitectureSnapshotCalculator."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.evolution.exceptions import EvolutionValidationError
from app.evolution.interfaces import (
    ArchitectureAnalysisProvider,
    ArchitectureSnapshotCalculator,
)
from app.evolution.models import ArchitectureSnapshot


class ArchitectureSnapshotService(ArchitectureSnapshotCalculator):
    """Concrete service compiling codebase structural metrics into immutable ArchitectureSnapshot instances."""

    def __init__(self, provider: ArchitectureAnalysisProvider) -> None:
        """Initializes the calculator service with constructor dependency injection.

        Args:
            provider: Injected provider to retrieve baseline static analysis outputs.
        """
        if provider is None:
            raise ValueError("ArchitectureAnalysisProvider dependency must not be None.")
        if not isinstance(provider, ArchitectureAnalysisProvider):
            raise TypeError("Dependency must inherit from ArchitectureAnalysisProvider interface.")
        self.provider = provider

    def calculate_snapshot(self, commit_id: str) -> ArchitectureSnapshot:
        """Compiles structural metrics into an immutable ArchitectureSnapshot.

        Args:
            commit_id: Git commit hash identifier representing target code point.

        Returns:
            The compiled ArchitectureSnapshot domain DTO.

        Raises:
            EvolutionValidationError: If validation fails or data retrieves inconsistent values.
        """
        if not commit_id or not commit_id.strip():
            raise EvolutionValidationError("commit_id must be a non-empty string.")

        # 1. Fetch analysis data from injected provider
        try:
            graph = self.provider.get_dependency_graph(commit_id)
            arch_result = self.provider.get_architecture_result(commit_id)
            quality_report = self.provider.get_quality_report(commit_id)
            tech_debt_report = self.provider.get_technical_debt_report(commit_id)
        except Exception as e:
            raise EvolutionValidationError(f"Inconsistent query lookup for commit '{commit_id}': {e}") from e

        # 2. Extract module inventory & graph metadata
        sorted_modules: List[str] = []
        node_count = 0
        edge_count = 0
        if graph is not None:
            # Validate input data formats defensively
            if not hasattr(graph, "nodes") or not hasattr(graph, "edges"):
                raise EvolutionValidationError("Retrieved dependency graph is invalid or corrupt.")

            # Filter MODULE nodes and normalize path slashes
            for node in graph.nodes:
                # We also support node type checks to filter modules
                # e.g., node.type.value == "module"
                node_type_val = getattr(node.type, "value", str(node.type))
                if node_type_val == "module":
                    norm_path = node.id.replace("\\", "/")
                    sorted_modules.append(norm_path)

            sorted_modules.sort()
            node_count = len(graph.nodes)
            edge_count = len(graph.edges)

        # 3. Extract layers & architectural metrics
        sorted_layers: List[str] = []
        arch_metrics: List[Dict[str, Any]] = []
        if arch_result is not None:
            if not hasattr(arch_result, "layers") or not hasattr(arch_result, "metrics"):
                raise EvolutionValidationError("Retrieved architecture analysis result is invalid or corrupt.")

            # Sort layer names alphabetically
            sorted_layers = sorted([layer.name for layer in arch_result.layers])

            # Extract metrics
            for m in arch_result.metrics:
                arch_metrics.append({
                    "name": m.name,
                    "value": float(m.value),
                    "unit": str(m.unit),
                })
            arch_metrics.sort(key=lambda x: x["name"])

        # 4. Extract quality metrics
        quality_metrics_dict: Dict[str, Any] = {
            "overall_score": 0.0,
            "overall_level": "unknown",
            "metrics_by_category": {},
            "metrics": [],
        }
        if quality_report is not None:
            if not hasattr(quality_report, "summary") or not hasattr(quality_report, "metrics"):
                raise EvolutionValidationError("Retrieved quality report is invalid or corrupt.")

            sumy = quality_report.summary
            quality_metrics_dict["overall_score"] = float(sumy.overall_score)
            quality_metrics_dict["overall_level"] = getattr(sumy.overall_level, "value", str(sumy.overall_level))

            # Convert categories mapping keys to string
            cat_metrics = {}
            if sumy.metrics_by_category:
                for k, v in sumy.metrics_by_category.items():
                    cat_metrics[getattr(k, "value", str(k))] = float(v)
            quality_metrics_dict["metrics_by_category"] = cat_metrics

            # Collect individual metrics list
            individual_metrics = []
            for m in quality_report.metrics:
                individual_metrics.append({
                    "name": m.name,
                    "value": float(m.value),
                    "level": getattr(m.level, "value", str(m.level)),
                })
            individual_metrics.sort(key=lambda x: x["name"])
            quality_metrics_dict["metrics"] = individual_metrics

        # 5. Extract technical debt metrics
        tech_debt_metrics_dict: Dict[str, Any] = {
            "total_items": 0,
            "total_effort_minutes": 0,
            "items_by_category": {},
            "effort_by_severity": {},
            "items": [],
        }
        if tech_debt_report is not None:
            if not hasattr(tech_debt_report, "summary") or not hasattr(tech_debt_report, "items"):
                raise EvolutionValidationError("Retrieved technical debt report is invalid or corrupt.")

            sumy = tech_debt_report.summary
            tech_debt_metrics_dict["total_items"] = int(sumy.total_items)
            tech_debt_metrics_dict["total_effort_minutes"] = int(sumy.total_effort_minutes)

            # Convert item categories to string
            cat_items = {}
            if sumy.items_by_category:
                for k, v in sumy.items_by_category.items():
                    cat_items[getattr(k, "value", str(k))] = int(v)
            tech_debt_metrics_dict["items_by_category"] = cat_items

            # Convert severities to string
            sev_efforts = {}
            if sumy.effort_by_severity:
                for k, v in sumy.effort_by_severity.items():
                    sev_efforts[getattr(k, "value", str(k))] = int(v)
            tech_debt_metrics_dict["effort_by_severity"] = sev_efforts

            # Individual findings
            findings = []
            for item in tech_debt_report.items:
                findings.append({
                    "id": item.id,
                    "title": item.title,
                    "category": getattr(item.category, "value", str(item.category)),
                    "severity": getattr(item.severity, "value", str(item.severity)),
                    "effort_minutes": int(item.effort_minutes),
                })
            findings.sort(key=lambda x: x["id"])
            tech_debt_metrics_dict["items"] = findings

        # 6. Compose components metadata dictionary
        components = {
            "modules": sorted_modules,
            "dependency_graph_metadata": {
                "node_count": node_count,
                "edge_count": edge_count,
            },
            "architectural_metrics": arch_metrics,
            "quality_metrics": quality_metrics_dict,
            "technical_debt_metrics": tech_debt_metrics_dict,
        }

        # 7. Construct and return snapshot DTO
        return ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id=commit_id,
            timestamp=datetime.now(timezone.utc),
            layers=tuple(sorted_layers),
            components=components,
        )
