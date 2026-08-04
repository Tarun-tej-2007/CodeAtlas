"""Architecture Metrics Engine module.

Computes architectural coupling, instability, and summary metrics
over layer and dependency structures in a language-agnostic manner.
"""

from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field

from app.architecture.models import ArchitectureLayer
from app.architecture.layer_dependency import LayerDependencyResult


class LayerMetrics(BaseModel):
    """Architectural metrics computed for a single layer."""

    layer_id: str = Field(..., description="The unique layer identifier.")
    afferent_coupling: int = Field(
        ..., description="Number of incoming inter-layer dependencies (Ca)."
    )
    efferent_coupling: int = Field(
        ..., description="Number of outgoing inter-layer dependencies (Ce)."
    )
    instability: float = Field(
        ..., description="Instability metric value (I = Ce / (Ca + Ce)). Bounded [0.0, 1.0]."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Metadata settings for the layer metrics."
    )

    model_config = ConfigDict(frozen=True)


class ArchitectureMetricsResult(BaseModel):
    """Aggregate architectural metrics calculated across the entire architecture."""

    layer_metrics: List[LayerMetrics] = Field(
        default_factory=list, description="Per-layer metrics list, sorted deterministically by layer ID."
    )
    average_instability: float = Field(
        ..., description="Average instability value across all layers."
    )
    total_afferent_coupling: int = Field(
        ..., description="Sum of afferent couplings across all layers."
    )
    total_efferent_coupling: int = Field(
        ..., description="Sum of efferent couplings across all layers."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Metadata settings for the metrics result."
    )

    model_config = ConfigDict(frozen=True)


class ArchitectureMetricsEngine:
    """Stateless metrics engine that calculates coupling and instability metrics."""

    def __init__(self) -> None:
        """Initializes the metrics engine."""
        pass

    def compute_metrics(
        self,
        layers: List[ArchitectureLayer],
        dependency_result: LayerDependencyResult,
    ) -> ArchitectureMetricsResult:
        """Computes per-layer metrics (Ca, Ce, Instability) and architectural aggregates.

        All calculations handle boundary divisions cleanly and are deterministic.
        """
        layer_metrics_list: List[LayerMetrics] = []

        for layer in layers:
            # Sum of dependency counts targeting this layer
            ca = sum(
                dep.dependency_count
                for dep in dependency_result.dependencies
                if dep.target_layer_id == layer.id
            )
            # Sum of dependency counts originating from this layer
            ce = sum(
                dep.dependency_count
                for dep in dependency_result.dependencies
                if dep.source_layer_id == layer.id
            )

            # Instability I = Ce / (Ca + Ce)
            total_coupling = ca + ce
            instability = float(ce) / total_coupling if total_coupling > 0 else 0.0

            layer_metrics_list.append(
                LayerMetrics(
                    layer_id=layer.id,
                    afferent_coupling=ca,
                    efferent_coupling=ce,
                    instability=instability,
                    metadata={},
                )
            )

        # Sort per-layer metrics deterministically by layer_id
        layer_metrics_list.sort(key=lambda x: x.layer_id)

        # Calculate architectural summary aggregates
        total_ca = sum(lm.afferent_coupling for lm in layer_metrics_list)
        total_ce = sum(lm.efferent_coupling for lm in layer_metrics_list)
        avg_instability = (
            sum(lm.instability for lm in layer_metrics_list) / len(layer_metrics_list)
            if layer_metrics_list
            else 0.0
        )

        return ArchitectureMetricsResult(
            layer_metrics=layer_metrics_list,
            average_instability=avg_instability,
            total_afferent_coupling=total_ca,
            total_efferent_coupling=total_ce,
            metadata={},
        )
