"""Architecture Smell Detection Engine module.

Analyzes dependency graphs, layers, validation results, and metrics to locate
architectural design smells like God Components, Feature Envy, and Low Cohesion.
"""

import hashlib
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.graph import DependencyGraph
from app.graph.cycle_detector import CycleDetector
from app.architecture.enums import AnalysisCategory, SeverityLevel, ArchitectureSmellType
from app.architecture.models import (
    ArchitectureAnalysisResult,
    ArchitectureIssue,
    ArchitectureLayer,
    ArchitectureMetric,
)
from app.architecture.layer_dependency import LayerDependencyResult
from app.architecture.layer_rules import LayerRuleValidationResult
from app.architecture.metrics import ArchitectureMetricsResult


class SmellDetectorConfig(BaseModel):
    """Configurable thresholds for detecting architectural smells."""

    coupling_threshold: int = Field(
        default=20,
        description="Max afferent or efferent coupling count before warning high coupling.",
    )
    cohesion_threshold: float = Field(
        default=0.2,
        description="Min cohesion ratio of (internal / total edges) before flagging low cohesion.",
    )
    instability_delta_threshold: float = Field(
        default=0.3,
        description="Min delta (I_src - I_tgt) for warning on unstable dependencies.",
    )
    god_layer_node_count_threshold: int = Field(
        default=50, description="Max node list length in a layer before flagging a God Layer."
    )
    god_node_degree_threshold: int = Field(
        default=30,
        description="Max combined incoming/outgoing degree for a node before flagging a God Node.",
    )
    feature_envy_ratio: float = Field(
        default=0.7,
        description="Min concentration ratio of a layer's efferent links to a single target layer.",
    )
    feature_envy_min_edges: int = Field(
        default=5,
        description="Min efferent coupling needed before evaluating layer feature envy.",
    )

    model_config = ConfigDict(frozen=True)


class ArchitectureSmellDetector:
    """Stateless detector analyzing domain results for architectural violations and design smells."""

    def __init__(self, config: Optional[SmellDetectorConfig] = None) -> None:
        """Initializes the smell detector with configuration parameters."""
        self.config = config or SmellDetectorConfig()
        self._cycle_detector = CycleDetector()

    def _get_stable_id(self, prefix: str, content: str) -> str:
        """Helper to create a deterministic ID for issues using SHA-256."""
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
        return f"{prefix}-{h}"

    def detect_smells(
        self,
        graph: DependencyGraph,
        layers: List[ArchitectureLayer],
        dependencies: LayerDependencyResult,
        validation_result: LayerRuleValidationResult,
        metrics: ArchitectureMetricsResult,
    ) -> ArchitectureAnalysisResult:
        """Runs the smell detection algorithms and populates an ArchitectureAnalysisResult."""
        issues: List[ArchitectureIssue] = []
        diagnostics: List[str] = []

        diagnostics.append("Started architectural smell detection scan.")

        # Map node_id -> layer_id
        node_to_layer: Dict[str, str] = {}
        for layer in layers:
            for node_id in layer.node_ids:
                node_to_layer[node_id] = layer.id

        # 1. CYCLIC_DEPENDENCY
        cycle_res = self._cycle_detector.detect_cycles(graph)
        for cycle in cycle_res.cycles:
            cycle_str = " -> ".join(cycle)
            issue_id = self._get_stable_id("smell-cycle", cycle_str)
            issues.append(
                ArchitectureIssue(
                    id=issue_id,
                    title="Cyclic Dependency Detected",
                    description=f"A dependency cycle exists in the codebase: {cycle_str}.",
                    severity=SeverityLevel.CRITICAL,
                    category=AnalysisCategory.SMELL,
                    recommendation="Refactor the cycle by introducing interface abstractions or decoupling models.",
                    location=cycle[0] if cycle else None,
                    metadata={
                        "cycle_path": cycle_str,
                        "smell_type": ArchitectureSmellType.CYCLIC_DEPENDENCY.value,
                    },
                )
            )

        # 2. LAYER_VIOLATION
        for violation in validation_result.violations:
            issue_id = self._get_stable_id(
                "smell-layer-violation",
                f"{violation.rule_id}-{violation.source_layer_id}-{violation.target_layer_id}",
            )
            issues.append(
                ArchitectureIssue(
                    id=issue_id,
                    title="Layer Dependency Violation",
                    description=violation.message,
                    severity=SeverityLevel.ERROR,
                    category=AnalysisCategory.LAYERING,
                    recommendation="Redirect the violating dependencies through approved interfaces or layers.",
                    location=violation.source_layer_id,
                    metadata={
                        "rule_id": violation.rule_id,
                        "source_layer_id": violation.source_layer_id,
                        "target_layer_id": violation.target_layer_id,
                        "dependency_count": str(violation.dependency_count),
                        "smell_type": ArchitectureSmellType.LAYER_VIOLATION.value,
                    },
                )
            )

        # 3. HIGH_COUPLING
        for lm in metrics.layer_metrics:
            if lm.afferent_coupling > self.config.coupling_threshold:
                issue_id = self._get_stable_id("smell-high-coupling-ca", lm.layer_id)
                issues.append(
                    ArchitectureIssue(
                        id=issue_id,
                        title="High Afferent Coupling (Ca)",
                        description=(
                            f"Layer '{lm.layer_id}' has afferent coupling Ca={lm.afferent_coupling}, "
                            f"exceeding the threshold of {self.config.coupling_threshold}."
                        ),
                        severity=SeverityLevel.WARNING,
                        category=AnalysisCategory.COUPLING,
                        recommendation="Introduce facade modules or subdivide the layer to reduce incoming dependency load.",
                        location=lm.layer_id,
                        metadata={
                            "layer_id": lm.layer_id,
                            "afferent_coupling": str(lm.afferent_coupling),
                            "smell_type": ArchitectureSmellType.HIGH_COUPLING.value,
                        },
                    )
                )
            if lm.efferent_coupling > self.config.coupling_threshold:
                issue_id = self._get_stable_id("smell-high-coupling-ce", lm.layer_id)
                issues.append(
                    ArchitectureIssue(
                        id=issue_id,
                        title="High Efferent Coupling (Ce)",
                        description=(
                            f"Layer '{lm.layer_id}' has efferent coupling Ce={lm.efferent_coupling}, "
                            f"exceeding the threshold of {self.config.coupling_threshold}."
                        ),
                        severity=SeverityLevel.WARNING,
                        category=AnalysisCategory.COUPLING,
                        recommendation="Decouple modules inside this layer or extract shared utilities to a utility layer.",
                        location=lm.layer_id,
                        metadata={
                            "layer_id": lm.layer_id,
                            "efferent_coupling": str(lm.efferent_coupling),
                            "smell_type": ArchitectureSmellType.HIGH_COUPLING.value,
                        },
                    )
                )

        # 4. LOW_COHESION
        # Calculate internal edges count for each layer
        layer_internal_edges: Dict[str, int] = {layer.id: 0 for layer in layers}
        for edge in graph.edges:
            src_l = node_to_layer.get(edge.source_id)
            tgt_l = node_to_layer.get(edge.target_id)
            if src_l and src_l == tgt_l:
                layer_internal_edges[src_l] += 1

        for lm in metrics.layer_metrics:
            internal = layer_internal_edges.get(lm.layer_id, 0)
            external = lm.afferent_coupling + lm.efferent_coupling
            total = internal + external
            cohesion = float(internal) / total if total > 0 else 1.0

            if total > 0 and cohesion < self.config.cohesion_threshold:
                issue_id = self._get_stable_id("smell-low-cohesion", lm.layer_id)
                issues.append(
                    ArchitectureIssue(
                        id=issue_id,
                        title="Low Layer Cohesion",
                        description=(
                            f"Layer '{lm.layer_id}' exhibits low cohesion ratio of {cohesion:.2f} "
                            f"(internal={internal}, external={external})."
                        ),
                        severity=SeverityLevel.WARNING,
                        category=AnalysisCategory.COHESION,
                        recommendation="Refactor the layer by grouping highly related files together or splitting it.",
                        location=lm.layer_id,
                        metadata={
                            "layer_id": lm.layer_id,
                            "cohesion_ratio": f"{cohesion:.4f}",
                            "smell_type": ArchitectureSmellType.LOW_COHESION.value,
                        },
                    )
                )

        # 5. UNSTABLE_DEPENDENCY
        instability_map = {lm.layer_id: lm.instability for lm in metrics.layer_metrics}
        for dep in dependencies.dependencies:
            i_src = instability_map.get(dep.source_layer_id)
            i_tgt = instability_map.get(dep.target_layer_id)
            if i_src is not None and i_tgt is not None:
                if i_src > i_tgt + self.config.instability_delta_threshold:
                    issue_id = self._get_stable_id(
                        "smell-unstable-dep", f"{dep.source_layer_id}-{dep.target_layer_id}"
                    )
                    issues.append(
                        ArchitectureIssue(
                            id=issue_id,
                            title="Unstable Dependency Boundary",
                            description=(
                                f"Unstable layer '{dep.source_layer_id}' (I={i_src:.2f}) "
                                f"depends on a more stable layer '{dep.target_layer_id}' (I={i_tgt:.2f})."
                            ),
                            severity=SeverityLevel.WARNING,
                            category=AnalysisCategory.DEPENDENCY,
                            recommendation="Invert dependencies using interface definitions or abstract coupling.",
                            location=dep.source_layer_id,
                            metadata={
                                "source_layer_id": dep.source_layer_id,
                                "target_layer_id": dep.target_layer_id,
                                "source_instability": f"{i_src:.4f}",
                                "target_instability": f"{i_tgt:.4f}",
                                "smell_type": ArchitectureSmellType.UNSTABLE_DEPENDENCY.value,
                            },
                        )
                    )

        # 6. GOD_COMPONENT
        # God layer check
        for layer in layers:
            if len(layer.node_ids) > self.config.god_layer_node_count_threshold:
                issue_id = self._get_stable_id("smell-god-layer", layer.id)
                issues.append(
                    ArchitectureIssue(
                        id=issue_id,
                        title="God Layer Component",
                        description=(
                            f"Layer '{layer.id}' contains too many nodes ({len(layer.node_ids)}), "
                            f"exceeding the threshold of {self.config.god_layer_node_count_threshold}."
                        ),
                        severity=SeverityLevel.WARNING,
                        category=AnalysisCategory.STRUCTURE,
                        recommendation="Decompose this layer into smaller logical namespaces or sub-packages.",
                        location=layer.id,
                        metadata={
                            "layer_id": layer.id,
                            "node_count": str(len(layer.node_ids)),
                            "smell_type": ArchitectureSmellType.GOD_COMPONENT.value,
                        },
                    )
                )

        # God node check (incoming + outgoing connections)
        for node in graph.nodes:
            deg_out = len(graph.get_outgoing_target_ids(node.id))
            deg_in = len(graph.get_incoming_source_ids(node.id))
            total_deg = deg_out + deg_in
            if total_deg > self.config.god_node_degree_threshold:
                issue_id = self._get_stable_id("smell-god-node", node.id)
                issues.append(
                    ArchitectureIssue(
                        id=issue_id,
                        title="God Node Component",
                        description=(
                            f"Node '{node.id}' has a high connection degree of {total_deg} "
                            f"(in={deg_in}, out={deg_out}), exceeding the threshold of {self.config.god_node_degree_threshold}."
                        ),
                        severity=SeverityLevel.WARNING,
                        category=AnalysisCategory.STRUCTURE,
                        recommendation="Refactor the node/class by applying Single Responsibility Principle.",
                        location=node.id,
                        metadata={
                            "node_id": node.id,
                            "degree": str(total_deg),
                            "smell_type": ArchitectureSmellType.GOD_COMPONENT.value,
                        },
                    )
                )

        # 7. FEATURE_ENVY
        for lm in metrics.layer_metrics:
            ce_total = lm.efferent_coupling
            if ce_total >= self.config.feature_envy_min_edges:
                out_deps = [
                    d for d in dependencies.dependencies if d.source_layer_id == lm.layer_id
                ]
                for dep in out_deps:
                    ratio = float(dep.dependency_count) / ce_total
                    if ratio > self.config.feature_envy_ratio:
                        issue_id = self._get_stable_id(
                            "smell-feature-envy", f"{lm.layer_id}-{dep.target_layer_id}"
                        )
                        issues.append(
                            ArchitectureIssue(
                                id=issue_id,
                                title="Layer Feature Envy",
                                description=(
                                    f"Layer '{lm.layer_id}' has excessive outgoing dependency concentration "
                                    f"({ratio*100:.1f}%) on target layer '{dep.target_layer_id}'."
                                ),
                                severity=SeverityLevel.WARNING,
                                category=AnalysisCategory.COHESION,
                                recommendation="Move tightly coupled components into the target layer or merge boundaries.",
                                location=lm.layer_id,
                                metadata={
                                    "source_layer_id": lm.layer_id,
                                    "target_layer_id": dep.target_layer_id,
                                    "concentration_ratio": f"{ratio:.4f}",
                                    "smell_type": ArchitectureSmellType.FEATURE_ENVY.value,
                                },
                            )
                        )

        # Sort issues deterministically by unique stable ID
        issues.sort(key=lambda x: x.id)

        # Build list of ArchitectureMetric references from metrics
        metrics_dto_list: List[ArchitectureMetric] = []
        metrics_dto_list.append(
            ArchitectureMetric(
                name="average_instability",
                value=metrics.average_instability,
                unit="ratio",
                description="Average instability across all layers.",
            )
        )
        for lm in metrics.layer_metrics:
            metrics_dto_list.append(
                ArchitectureMetric(
                    name=f"layer_{lm.layer_id}_afferent_coupling",
                    value=float(lm.afferent_coupling),
                    unit="count",
                    description=f"Afferent coupling (Ca) of layer {lm.layer_id}.",
                )
            )
            metrics_dto_list.append(
                ArchitectureMetric(
                    name=f"layer_{lm.layer_id}_efferent_coupling",
                    value=float(lm.efferent_coupling),
                    unit="count",
                    description=f"Efferent coupling (Ce) of layer {lm.layer_id}.",
                )
            )
            metrics_dto_list.append(
                ArchitectureMetric(
                    name=f"layer_{lm.layer_id}_instability",
                    value=lm.instability,
                    unit="ratio",
                    description=f"Instability (I) of layer {lm.layer_id}.",
                )
            )

        diagnostics.append(f"Completed smell detection. Detected {len(issues)} issues.")

        return ArchitectureAnalysisResult(
            issues=issues,
            layers=layers,
            metrics=metrics_dto_list,
            diagnostics=diagnostics,
            metadata={},
        )
