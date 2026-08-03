"""Layer Rule Validation Engine module.

Validates inter-layer dependencies against a configured set of architectural
layer rules, detecting structural violations.
"""

from typing import Dict, List
from pydantic import BaseModel, ConfigDict, Field

from app.architecture.models import ArchitectureLayer
from app.architecture.layer_dependency import LayerDependencyResult


class LayerRule(BaseModel):
    """Represents a configured architectural rule between two layers."""

    id: str = Field(..., description="Unique stable identifier for the rule.")
    name: str = Field(..., description="Human-readable name of the rule.")
    source_layer: str = Field(..., description="The ID of the source layer.")
    target_layer: str = Field(..., description="The ID of the target layer.")
    allow: bool = Field(..., description="Whether dependencies are permitted from source to target.")
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Custom metadata settings for this rule."
    )

    model_config = ConfigDict(frozen=True)


class LayerRuleViolation(BaseModel):
    """Represents a violation of a layer dependency boundary rule."""

    rule_id: str = Field(..., description="The ID of the violated rule.")
    source_layer_id: str = Field(..., description="The source layer involved in the violation.")
    target_layer_id: str = Field(..., description="The target layer involved in the violation.")
    dependency_count: int = Field(..., description="Number of violating edge links.")
    message: str = Field(..., description="Descriptive violation message.")
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Metadata context for the violation."
    )

    model_config = ConfigDict(frozen=True)


class LayerRuleValidationResult(BaseModel):
    """Result container of a validation run over layer dependencies."""

    violations: List[LayerRuleViolation] = Field(
        default_factory=list, description="Sorted list of all detected rule violations."
    )
    diagnostics: List[str] = Field(
        default_factory=list, description="Diagnostic logs collected during validation."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Metadata settings for the validation run."
    )

    model_config = ConfigDict(frozen=True)


class LayerRuleValidator:
    """Stateless validator that asserts architectural boundary rules over layer dependencies."""

    def __init__(self) -> None:
        """Initializes the layer rule validator."""
        pass

    def validate(
        self,
        dependency_result: LayerDependencyResult,
        layers: List[ArchitectureLayer],
        rules: List[LayerRule],
    ) -> LayerRuleValidationResult:
        """Evaluates layer dependencies against rules, generating violations for disallowed links."""
        violations: List[LayerRuleViolation] = []
        diagnostics: List[str] = []

        diagnostics.append(f"Started layer validation with {len(rules)} rules and {len(layers)} layers.")

        # Map rules for fast lookup
        # key: (source, target) -> list of rules
        rule_map: Dict[tuple[str, str], List[LayerRule]] = {}
        for rule in rules:
            key = (rule.source_layer, rule.target_layer)
            if key not in rule_map:
                rule_map[key] = []
            rule_map[key].append(rule)

        for dep in dependency_result.dependencies:
            key = (dep.source_layer_id, dep.target_layer_id)
            matching_rules = rule_map.get(key, [])

            for rule in matching_rules:
                if not rule.allow:
                    msg = (
                        f"Layer boundary violation: Dependency from '{dep.source_layer_id}' "
                        f"to '{dep.target_layer_id}' is disallowed by rule '{rule.name}' ({rule.id})."
                    )
                    violations.append(
                        LayerRuleViolation(
                            rule_id=rule.id,
                            source_layer_id=dep.source_layer_id,
                            target_layer_id=dep.target_layer_id,
                            dependency_count=dep.dependency_count,
                            message=msg,
                            metadata={"rule_name": rule.name},
                        )
                    )

        # Sort violations deterministically by (rule_id, source_layer_id, target_layer_id)
        violations.sort(key=lambda v: (v.rule_id, v.source_layer_id, v.target_layer_id))

        diagnostics.append(f"Validation completed. Detected {len(violations)} violations.")

        return LayerRuleValidationResult(violations=violations, diagnostics=diagnostics, metadata={})
