"""Service layer for constructing and validating architecture governance policies."""

import re
import uuid
from datetime import datetime, timezone
from typing import Any, List, Mapping, Optional, Tuple

from app.governance.enums import PolicyCategory, RuleType, ViolationSeverity
from app.governance.exceptions import GovernanceValidationError
from app.governance.models import GovernancePolicy, PolicyMetadata, PolicyRule


class PolicyDefinitionService:
    """Stateless service responsible for creating, validating, and normalizing architecture governance policies."""

    def create_policy(
        self,
        name: str,
        version: str,
        category: PolicyCategory,
        rules: Tuple[PolicyRule, ...],
        extra_info: Optional[Mapping[str, Any]] = None,
    ) -> GovernancePolicy:
        """Constructs, validates, and normalizes an immutable GovernancePolicy instance.

        Args:
            name: Policy name identifier.
            version: Version metadata string.
            category: Classification category of this policy.
            rules: Immutable tuple of PolicyRule rules.
            extra_info: Optional metadata mapping attributes.

        Returns:
            The constructed immutable GovernancePolicy.

        Raises:
            GovernanceValidationError: If validation fails, duplicate rules exist, or contradictions are detected.
        """
        if not name or not name.strip():
            raise GovernanceValidationError("Policy name must not be empty.")
        if not version or not version.strip():
            raise GovernanceValidationError("Policy version must not be empty.")
        if not isinstance(category, PolicyCategory):
            raise GovernanceValidationError("Category must be a valid PolicyCategory enum.")
        if rules is None:
            raise GovernanceValidationError("Rules collection must not be None.")

        # Normalize strings
        norm_name = name.strip()
        norm_version = version.strip()

        # 1. Validate rules uniqueness and normalize rule identifiers
        seen_names = set()
        normalized_rules = []
        for r in rules:
            if not isinstance(r, PolicyRule):
                raise GovernanceValidationError("All rule items must be valid PolicyRule instances.")

            rule_name = r.name.strip()
            if not rule_name:
                raise GovernanceValidationError("Rule name must not be empty.")

            norm_rule_name = rule_name.lower()
            if norm_rule_name in seen_names:
                raise GovernanceValidationError(f"Duplicate rule name detected: '{rule_name}'")
            seen_names.add(norm_rule_name)

            # Normalize rule configurations (e.g. normalize string lists)
            normalized_config = {}
            for k, v in r.configuration.items():
                if isinstance(v, str):
                    normalized_config[k.strip()] = v.strip()
                elif isinstance(v, (list, tuple)):
                    normalized_config[k.strip()] = tuple(
                        item.strip() if isinstance(item, str) else item for item in v
                    )
                else:
                    normalized_config[k.strip()] = v

            normalized_rules.append(
                PolicyRule(
                    rule_id=r.rule_id,
                    name=rule_name,
                    rule_type=r.rule_type,
                    severity=r.severity,
                    configuration=normalized_config,
                )
            )

        # 2. Check for contradictory rules in the policy
        self._validate_contradictory_rules(normalized_rules)

        # 3. Deterministic rule ordering: sort by rule name and rule_type value
        normalized_rules.sort(key=lambda r: (r.name.lower(), r.rule_type.value))

        # 4. Construct metadata
        policy_id = uuid.uuid4()
        metadata = PolicyMetadata(
            policy_id=policy_id,
            name=norm_name,
            version=norm_version,
            category=category,
            created_at=datetime.now(timezone.utc),
            extra_info=dict(extra_info) if extra_info else {},
        )

        # 5. Build and return GovernancePolicy DTO
        return GovernancePolicy(
            policy_id=policy_id,
            metadata=metadata,
            rules=tuple(normalized_rules),
        )

    def _validate_contradictory_rules(self, rules: List[PolicyRule]) -> None:
        """Validates that there are no contradictory constraints between rules in the policy."""
        # Separate configuration profiles by rule type to compare constraints
        forbidden_deps = set()
        required_deps = set()

        metrics_bounds = {}  # metric_name -> {min: val, max: val}

        for r in rules:
            cfg = r.configuration

            # Check Dependency restrictions contradiction (e.g. forbidden vs required modules)
            if r.rule_type in (RuleType.FORBIDDEN_DEPENDENCY, RuleType.REQUIRED_DEPENDENCY):
                # Extrapolate list of modules from configuration keys
                forbiddens = cfg.get("forbidden_modules") or cfg.get("forbidden_dependencies") or ()
                requireds = cfg.get("required_modules") or cfg.get("required_dependencies") or ()

                # If they are single string values, wrap them in list
                if isinstance(forbiddens, str):
                    forbiddens = (forbiddens,)
                if isinstance(requireds, str):
                    requireds = (requireds,)

                for d in forbiddens:
                    forbidden_deps.add(d.strip())
                for d in requireds:
                    required_deps.add(d.strip())

            # Check Threshold contradictions (e.g. min_threshold > max_threshold)
            if r.rule_type == RuleType.THRESHOLD:
                metric = cfg.get("metric_name") or cfg.get("metric")
                if metric:
                    metric = str(metric).strip().lower()
                    min_val = cfg.get("min_threshold") or cfg.get("min_value")
                    max_val = cfg.get("max_threshold") or cfg.get("max_value")

                    if metric not in metrics_bounds:
                        metrics_bounds[metric] = {"min": None, "max": None}

                    if min_val is not None:
                        try:
                            val = float(min_val)
                            metrics_bounds[metric]["min"] = val
                        except ValueError:
                            pass
                    if max_val is not None:
                        try:
                            val = float(max_val)
                            metrics_bounds[metric]["max"] = val
                        except ValueError:
                            pass

            # Check Naming convention contradictions (e.g. required vs forbidden suffix)
            if r.rule_type == RuleType.LAYER_ORDERING:
                # E.g. circular layer order constraints could be checked, but simpler:
                pass

        # 1. Dependency checks: a dependency cannot be both required and forbidden
        overlap = forbidden_deps & required_deps
        if overlap:
            raise GovernanceValidationError(
                f"Contradictory dependency rules detected. The following module(s) are both required and forbidden: {overlap}"
            )

        # 2. Metric thresholds: min_threshold cannot exceed max_threshold
        for metric, bounds in metrics_bounds.items():
            if bounds["min"] is not None and bounds["max"] is not None:
                if bounds["min"] > bounds["max"]:
                    raise GovernanceValidationError(
                        f"Contradictory thresholds for metric '{metric}': minimum limit {bounds['min']} exceeds maximum limit {bounds['max']}."
                    )
