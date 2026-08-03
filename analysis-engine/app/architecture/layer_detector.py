"""Layer Detection Engine module.

Analyzes a dependency graph and classifies nodes into architectural layers
based on configurable, language-agnostic matching rules.
"""

import re
from typing import Dict, List, Set, Tuple
from pydantic import BaseModel, Field

from app.graph import DependencyGraph
from app.graph.dependency_models import GraphNode
from app.graph.enums import DependencyNodeType
from app.architecture.enums import LayerType
from app.architecture.models import ArchitectureLayer


class LayerRule(BaseModel):
    """Configuration rule for assigning dependency graph nodes to architectural layers."""

    layer_id: str = Field(..., description="Unique stable identifier for the layer.")
    layer_name: str = Field(..., description="Human-readable name of the layer.")
    layer_type: LayerType = Field(..., description="The category classification of the layer.")

    # Match criteria (at least one must match if specified)
    id_patterns: List[str] = Field(
        default_factory=list, description="Regex patterns to match against node IDs."
    )
    name_patterns: List[str] = Field(
        default_factory=list, description="Regex patterns to match against node names."
    )
    metadata_patterns: Dict[str, str] = Field(
        default_factory=dict, description="Metadata key to regex pattern dictionary."
    )
    types: List[DependencyNodeType] = Field(
        default_factory=list, description="Limit match to specific node types."
    )

    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Metadata keys/values to attach to the resolved layer."
    )

    def matches_node(self, node: GraphNode) -> bool:
        """Determines if a graph node satisfies this rule's matching criteria."""
        # 1. Node type filter
        if self.types and node.type not in self.types:
            return False

        # If no regex patterns are defined, check if type constraint was met
        has_patterns = bool(self.id_patterns or self.name_patterns or self.metadata_patterns)
        if not has_patterns:
            return bool(self.types)

        # 2. ID patterns match
        if self.id_patterns:
            for pattern in self.id_patterns:
                try:
                    if re.search(pattern, node.id):
                        return True
                except re.error:
                    pass

        # 3. Name patterns match
        if self.name_patterns:
            for pattern in self.name_patterns:
                try:
                    if re.search(pattern, node.name):
                        return True
                except re.error:
                    pass

        # 4. Metadata pattern matches
        if self.metadata_patterns:
            for key, pattern in self.metadata_patterns.items():
                if key in node.metadata:
                    val = str(node.metadata[key])
                    try:
                        if re.search(pattern, val):
                            return True
                    except re.error:
                        pass

        return False


class LayerDetector:
    """Stateless layer detection engine that classifies nodes into architectural layers."""

    def __init__(self, rules: List[LayerRule] = None) -> None:
        """Initializes the detector with a list of classification rules."""
        self._rules = list(rules) if rules is not None else []

    def detect_layers(self, graph: DependencyGraph) -> List[ArchitectureLayer]:
        """Groups graph nodes into distinct layers based on the match rules.

        Nodes not matching any rule default to the UNKNOWN layer.
        """
        # Map: layer_id -> Set of node IDs
        layers_map: Dict[str, Set[str]] = {}
        # Map: layer_id -> (LayerType, layer_name, metadata)
        layer_meta: Dict[str, Tuple[LayerType, str, Dict[str, str]]] = {}

        # Register configured layers
        for rule in self._rules:
            if rule.layer_id not in layers_map:
                layers_map[rule.layer_id] = set()
                layer_meta[rule.layer_id] = (rule.layer_type, rule.layer_name, dict(rule.metadata))

        # Register default UNKNOWN layer fallback
        unknown_id = "unknown"
        if unknown_id not in layers_map:
            layers_map[unknown_id] = set()
            layer_meta[unknown_id] = (LayerType.UNKNOWN, "Unknown Layer", {})

        # Classify each node from the graph
        for node in graph.nodes:
            matched = False
            for rule in self._rules:
                if rule.matches_node(node):
                    layers_map[rule.layer_id].add(node.id)
                    matched = True
                    break

            if not matched:
                layers_map[unknown_id].add(node.id)

        # Construct final sorted ArchitectureLayer models
        result_layers: List[ArchitectureLayer] = []
        for lid, nodes in layers_map.items():
            if not nodes:
                continue

            ltype, lname, lmeta = layer_meta[lid]
            result_layers.append(
                ArchitectureLayer(
                    id=lid,
                    name=lname,
                    layer_type=ltype,
                    node_ids=sorted(list(nodes)),
                    metadata=lmeta,
                )
            )

        # Sort the final layers list lexicographically by ID for determinism
        result_layers.sort(key=lambda x: x.id)
        return result_layers
