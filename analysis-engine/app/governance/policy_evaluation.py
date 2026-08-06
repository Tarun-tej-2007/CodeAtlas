"""Service layer for evaluating architecture governance policies."""

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.evolution.interfaces import ArchitectureAnalysisProvider
from app.governance.enums import GovernanceStatus, RuleType, ViolationSeverity
from app.governance.exceptions import GovernanceValidationError, PolicyEvaluationError
from app.governance.interfaces import PolicyRuleEvaluator
from app.governance.models import (
    GovernancePolicy,
    GovernanceRequest,
    GovernanceResult,
    GovernanceSummary,
    PolicyRule,
    PolicyViolation,
)


class PolicyEvaluationService(PolicyRuleEvaluator):
    """Concrete PolicyRuleEvaluator that evaluates policies against platform static analysis outputs."""

    def __init__(self, provider: ArchitectureAnalysisProvider) -> None:
        """Initializes service using constructor dependency injection.

        Args:
            provider: Injected ArchitectureAnalysisProvider dependency.
        """
        if provider is None:
            raise ValueError("provider dependency must not be None.")
        if not isinstance(provider, ArchitectureAnalysisProvider):
            raise TypeError("provider must inherit from ArchitectureAnalysisProvider.")
        self.provider = provider

    def evaluate_rule(self, commit_id: str, rule: PolicyRule) -> Tuple[PolicyViolation, ...]:
        """Evaluates a single policy rule against codebase structure at the given commit.

        Args:
            commit_id: Git commit hash identifier representing target code point.
            rule: Injected PolicyRule domain model.

        Returns:
            An immutable tuple of PolicyViolation items.

        Raises:
            GovernanceValidationError: If parameters are invalid.
            PolicyEvaluationError: If rule evaluation fails during execution.
        """
        if not commit_id or not commit_id.strip():
            raise GovernanceValidationError("commit_id must be a non-empty string.")
        if not isinstance(rule, PolicyRule):
            raise GovernanceValidationError("rule must be a valid PolicyRule instance.")

        violations: List[PolicyViolation] = []
        cfg = rule.configuration

        try:
            # Load analysis data dynamically
            graph = self.provider.get_dependency_graph(commit_id)
            arch_result = self.provider.get_architecture_result(commit_id)
            quality_report = self.provider.get_quality_report(commit_id)
            tech_debt_report = self.provider.get_technical_debt_report(commit_id)
        except Exception as e:
            raise PolicyEvaluationError(f"Failed to load analysis outputs: {e}") from e

        # Case: Empty repository (if graph is None or empty)
        nodes = graph.nodes if graph is not None else []
        edges = graph.edges if graph is not None else []

        # 1. Dependency Restrictions
        if rule.rule_type in (RuleType.FORBIDDEN_DEPENDENCY, RuleType.REQUIRED_DEPENDENCY):
            forbiddens = cfg.get("forbidden_modules") or cfg.get("forbidden_dependencies") or ()
            requireds = cfg.get("required_modules") or cfg.get("required_dependencies") or ()

            if isinstance(forbiddens, str):
                forbiddens = (forbiddens,)
            if isinstance(requireds, str):
                requireds = (requireds,)

            source_scope = cfg.get("source_module") or cfg.get("source_pattern") or ""

            # Evaluate FORBIDDEN_DEPENDENCY
            if rule.rule_type == RuleType.FORBIDDEN_DEPENDENCY:
                for edge in edges:
                    src = edge.source_id.replace("\\", "/")
                    tgt = edge.target_id.replace("\\", "/")

                    if source_scope and not src.startswith(str(source_scope)):
                        continue

                    for f_mod in forbiddens:
                        f_mod_norm = str(f_mod).strip()
                        if tgt == f_mod_norm or tgt.startswith(f_mod_norm + "/"):
                            violations.append(
                                PolicyViolation(
                                    violation_id=uuid.uuid4(),
                                    rule_id=rule.rule_id,
                                    rule_name=rule.name,
                                    severity=rule.severity,
                                    message=f"Dependency violation: Module '{src}' depends on forbidden module '{tgt}'.",
                                    details={"source": src, "target": tgt},
                                )
                            )

            # Evaluate REQUIRED_DEPENDENCY
            if rule.rule_type == RuleType.REQUIRED_DEPENDENCY and source_scope:
                source_scope_str = str(source_scope).strip()
                # Find all nodes matching source_scope
                matching_sources = [
                    n.id for n in nodes if n.id == source_scope_str or n.id.startswith(source_scope_str + "/")
                ]
                for src in matching_sources:
                    # Find all outgoing target IDs from this source
                    targets = {edge.target_id for edge in edges if edge.source_id == src}
                    for r_mod in requireds:
                        r_mod_norm = str(r_mod).strip()
                        # Check if target is not depended on
                        if not any(t == r_mod_norm or t.startswith(r_mod_norm + "/") for t in targets):
                            violations.append(
                                PolicyViolation(
                                    violation_id=uuid.uuid4(),
                                    rule_id=rule.rule_id,
                                    rule_name=rule.name,
                                    severity=rule.severity,
                                    message=f"Dependency violation: Module '{src}' does not depend on required module '{r_mod_norm}'.",
                                    details={"source": src, "missing_dependency": r_mod_norm},
                                )
                            )

        # 2. Layering Constraints
        elif rule.rule_type == RuleType.LAYER_ORDERING:
            allowed_layer_deps = cfg.get("allowed_layer_dependencies") or {}
            # Map node IDs to layer names
            node_layers: Dict[str, str] = {}
            if arch_result is not None and hasattr(arch_result, "layers"):
                for layer in arch_result.layers:
                    for nid in layer.node_ids:
                        node_layers[nid] = layer.name

            for edge in edges:
                src_layer = node_layers.get(edge.source_id)
                tgt_layer = node_layers.get(edge.target_id)

                if src_layer and tgt_layer and src_layer != tgt_layer:
                    allowed = allowed_layer_deps.get(src_layer) or ()
                    if isinstance(allowed, str):
                        allowed = (allowed,)
                    if tgt_layer not in allowed:
                        violations.append(
                            PolicyViolation(
                                violation_id=uuid.uuid4(),
                                rule_id=rule.rule_id,
                                rule_name=rule.name,
                                severity=rule.severity,
                                message=f"Layer dependency violation: Layer '{src_layer}' ({edge.source_id}) depends on Layer '{tgt_layer}' ({edge.target_id}) which is not allowed.",
                                details={
                                    "source_node": edge.source_id,
                                    "target_node": edge.target_id,
                                    "source_layer": src_layer,
                                    "target_layer": tgt_layer,
                                },
                            )
                        )

        # 3. Naming Conventions, Package/Module Ownership & General Thresholds
        elif rule.rule_type == RuleType.THRESHOLD:
            metric_name = str(cfg.get("metric_name") or cfg.get("metric") or "").strip().lower()
            max_thresh = cfg.get("max_threshold") or cfg.get("max_value")
            min_thresh = cfg.get("min_threshold") or cfg.get("min_value")

            # Check Naming conventions (using threshold format/regex logic if defined)
            naming_pattern = cfg.get("naming_pattern") or cfg.get("pattern")
            if naming_pattern:
                pat = str(naming_pattern).strip()
                try:
                    rx = re.compile(pat)
                except re.error as e:
                    raise PolicyEvaluationError(f"Invalid regex naming pattern '{pat}': {e}") from e

                for node in nodes:
                    node_type_val = getattr(node.type, "value", str(node.type))
                    if node_type_val == "module":
                        if not rx.match(node.name):
                            violations.append(
                                PolicyViolation(
                                    violation_id=uuid.uuid4(),
                                    rule_id=rule.rule_id,
                                    rule_name=rule.name,
                                    severity=rule.severity,
                                    message=f"Naming violation: Module name '{node.name}' does not match pattern '{pat}'.",
                                    details={"node_id": node.id, "node_name": node.name, "pattern": pat},
                                )
                            )

            # Check Package/Module Ownership
            require_owner = cfg.get("require_owner")
            allowed_owners = cfg.get("allowed_owners") or ()
            if isinstance(allowed_owners, str):
                allowed_owners = (allowed_owners,)

            if require_owner or allowed_owners:
                for node in nodes:
                    node_type_val = getattr(node.type, "value", str(node.type))
                    if node_type_val == "module":
                        owner = node.metadata.get("owner")
                        if not owner:
                            if require_owner:
                                violations.append(
                                    PolicyViolation(
                                        violation_id=uuid.uuid4(),
                                        rule_id=rule.rule_id,
                                        rule_name=rule.name,
                                        severity=rule.severity,
                                        message=f"Ownership violation: Module '{node.id}' has no owner defined.",
                                        details={"node_id": node.id},
                                    )
                                )
                        else:
                            if allowed_owners and owner not in allowed_owners:
                                violations.append(
                                    PolicyViolation(
                                        violation_id=uuid.uuid4(),
                                        rule_id=rule.rule_id,
                                        rule_name=rule.name,
                                        severity=rule.severity,
                                        message=f"Ownership violation: Module '{node.id}' owner '{owner}' is not in allowed owners list.",
                                        details={"node_id": node.id, "owner": owner},
                                    )
                                )

            # Check Complexity, Coupling & Technical Debt metrics thresholds
            if metric_name:
                all_metrics = []

                # Extract quality metrics
                if quality_report is not None and hasattr(quality_report, "metrics"):
                    for m in quality_report.metrics:
                        all_metrics.append((m.name.lower(), float(m.value), f"Quality metric '{m.name}'"))

                # Extract architecture metrics
                if arch_result is not None and hasattr(arch_result, "metrics"):
                    for m in arch_result.metrics:
                        all_metrics.append((m.name.lower(), float(m.value), f"Architecture metric '{m.name}'"))

                # Extract technical debt summary values
                if tech_debt_report is not None and hasattr(tech_debt_report, "summary"):
                    summ = tech_debt_report.summary
                    all_metrics.append(("technical_debt_items", float(summ.total_items), "Total technical debt items"))
                    all_metrics.append(("technical_debt_effort_minutes", float(summ.total_effort_minutes), "Total technical debt effort (minutes)"))
                    all_metrics.append(("effort_minutes", float(summ.total_effort_minutes), "Technical debt effort minutes"))

                # Evaluate thresholds
                for m_id, m_val, m_desc in all_metrics:
                    if m_id == metric_name or metric_name in m_id:
                        if max_thresh is not None and m_val > float(max_thresh):
                            violations.append(
                                PolicyViolation(
                                    violation_id=uuid.uuid4(),
                                    rule_id=rule.rule_id,
                                    rule_name=rule.name,
                                    severity=rule.severity,
                                    message=f"{m_desc} value {m_val} exceeds maximum threshold of {max_thresh}.",
                                    details={"metric": m_id, "value": m_val, "threshold": max_thresh},
                                )
                            )
                        if min_thresh is not None and m_val < float(min_thresh):
                            violations.append(
                                PolicyViolation(
                                    violation_id=uuid.uuid4(),
                                    rule_id=rule.rule_id,
                                    rule_name=rule.name,
                                    severity=rule.severity,
                                    message=f"{m_desc} value {m_val} falls below minimum threshold of {min_thresh}.",
                                    details={"metric": m_id, "value": m_val, "threshold": min_thresh},
                                )
                            )

        # Preserve deterministic ordering of violations sorted alphabetically by rule_name and message
        violations.sort(key=lambda v: (v.rule_name, v.message))
        return tuple(violations)

    def evaluate_request(self, request: GovernanceRequest) -> GovernanceResult:
        """Evaluates all policies defined in the GovernanceRequest and compiles the final GovernanceResult.

        Args:
            request: Injected GovernanceRequest payload.

        Returns:
            The compiled immutable GovernanceResult.

        Raises:
            GovernanceValidationError: If request parameter is invalid.
            PolicyEvaluationError: If rule execution fails.
        """
        if request is None or not isinstance(request, GovernanceRequest):
            raise GovernanceValidationError("request must be a valid GovernanceRequest instance.")

        all_violations: List[PolicyViolation] = []
        total_rules = 0

        # Evaluate rules policy-by-policy
        for policy in request.policies:
            if not isinstance(policy, GovernancePolicy):
                raise GovernanceValidationError("Policies list must contain valid GovernancePolicy objects.")

            for rule in policy.rules:
                total_rules += 1
                violations = self.evaluate_rule(request.commit_id, rule)
                all_violations.extend(violations)

        # Count summary metrics
        passed_count = 0
        failed_count = 0
        warning_count = 0

        # We keep track of which rules had violations
        violated_rules = set()
        for v in all_violations:
            violated_rules.add(v.rule_id)
            if v.severity == ViolationSeverity.ERROR:
                failed_count += 1
            else:
                warning_count += 1

        passed_count = max(0, total_rules - len(violated_rules))

        summary = GovernanceSummary(
            passed_count=passed_count,
            failed_count=failed_count,
            warning_count=warning_count,
            total_rules=total_rules,
        )

        # Determine overall execution status
        if failed_count > 0:
            status = GovernanceStatus.FAILED
        elif warning_count > 0:
            status = GovernanceStatus.WARNING
        else:
            status = GovernanceStatus.PASSED

        # Preserve deterministic ordering of violations sorted alphabetically by rule_name and message
        all_violations.sort(key=lambda v: (v.rule_name, v.message))

        return GovernanceResult(
            result_id=uuid.uuid4(),
            project_id=request.project_id,
            commit_id=request.commit_id,
            status=status,
            violations=tuple(all_violations),
            summary=summary,
            created_at=datetime.now(timezone.utc),
            extra_info={"correlation_id": request.correlation_id} if request.correlation_id else {},
        )
