"""Layer Dependency Analysis Engine module.

Aggregates node-level directed dependencies in a DependencyGraph into
deterministic inter-layer relationships.
"""

from typing import Dict, List, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.graph import DependencyGraph
from app.graph.enums import DependencyEdgeType
from app.architecture.models import ArchitectureLayer


class LayerDependency(BaseModel):
    """Represents an aggregated dependency relationship between two distinct layers."""

    source_layer_id: str = Field(..., description="The source layer identifier.")
    target_layer_id: str = Field(..., description="The target layer identifier.")
    dependency_count: int = Field(..., description="Total count of inter-layer node-level edges.")
    edge_types: List[DependencyEdgeType] = Field(
        default_factory=list, description="Unique dependency edge types contributing to this relationship."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Custom metadata for the layer dependency connection."
    )

    model_config = ConfigDict(frozen=True)


class LayerDependencyResult(BaseModel):
    """Immutable container for all aggregated layer dependencies."""

    dependencies: List[LayerDependency] = Field(
        default_factory=list, description="Sorted list of aggregated layer dependencies."
    )

    model_config = ConfigDict(frozen=True)


class LayerDependencyAnalyzer:
    """Stateless analyzer that aggregates node dependencies into layer relationships."""

    def __init__(self) -> None:
        """Initializes the layer dependency analyzer."""
        pass

    def analyze(self, graph: DependencyGraph, layers: List[ArchitectureLayer]) -> LayerDependencyResult:
        """Aggregates graph edges into layer-to-layer dependency groups.

        Intra-layer connections are ignored. Output is sorted deterministically.
        """
        # Map: node_id -> layer_id
        node_to_layer: Dict[str, str] = {}
        for layer in layers:
            for node_id in layer.node_ids:
                node_to_layer[node_id] = layer.id

        # Aggregation Map: (src_layer, tgt_layer) -> (count, set of edge_types)
        aggregation: Dict[Tuple[str, str], Tuple[int, Set[DependencyEdgeType]]] = {}

        for edge in graph.edges:
            src_layer = node_to_layer.get(edge.source_id)
            tgt_layer = node_to_layer.get(edge.target_id)

            # Skip if either node doesn't map to a layer
            if not src_layer or not tgt_layer:
                continue

            # Ignore intra-layer dependencies
            if src_layer == tgt_layer:
                continue

            key = (src_layer, tgt_layer)
            if key not in aggregation:
                aggregation[key] = (0, set())

            count, edge_types = aggregation[key]
            aggregation[key] = (count + 1, edge_types | {edge.type})

        # Build LayerDependency list
        dependencies: List[LayerDependency] = []
        for (src_layer, tgt_layer), (count, edge_types) in aggregation.items():
            # Sort edge types lexicographically by value
            sorted_types = sorted(list(edge_types), key=lambda x: x.value)
            dependencies.append(
                LayerDependency(
                    source_layer_id=src_layer,
                    target_layer_id=tgt_layer,
                    dependency_count=count,
                    edge_types=sorted_types,
                    metadata={},
                )
            )

        # Sort dependencies deterministically by (source_layer_id, target_layer_id)
        dependencies.sort(key=lambda d: (d.source_layer_id, d.target_layer_id))

        return LayerDependencyResult(dependencies=dependencies)
