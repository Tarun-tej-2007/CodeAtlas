"""Governance violation analyzer implementation."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from app.governance.enums import ViolationSeverity
from app.governance.exceptions import GovernanceValidationError
from app.governance.interfaces import ViolationAnalyzer
from app.governance.models import EnrichedViolation, GovernanceViolationReport, PolicyViolation


class GovernanceViolationAnalyzer(ViolationAnalyzer):
    """Concrete analyzer class enriching policy violations with priority, root cause, and remediation steps."""

    def analyze_violations(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        violations: Tuple[PolicyViolation, ...],
    ) -> GovernanceViolationReport:
        """Analyzes a collection of PolicyViolation objects, enriching them with governance diagnostics.

        Args:
            project_id: Associated project scope identifier.
            commit_id: Git commit hash identifier representing target codebase state.
            violations: Immutable tuple of raw PolicyViolation objects.

        Returns:
            The compiled immutable GovernanceViolationReport.

        Raises:
            GovernanceValidationError: If validation fails or inconsistency is detected.
        """
        if project_id is None:
            raise GovernanceValidationError("project_id must not be None.")
        if not commit_id or not commit_id.strip():
            raise GovernanceValidationError("commit_id must be a non-empty string.")
        if violations is None:
            raise GovernanceValidationError("violations collection must not be None.")

        enriched_list: List[EnrichedViolation] = []
        rule_groups: Dict[str, List[EnrichedViolation]] = {}
        severity_counts: Dict[str, int] = {
            ViolationSeverity.ERROR.value: 0,
            ViolationSeverity.WARNING.value: 0,
            ViolationSeverity.INFO.value: 0,
        }

        # Step-by-step enrichment
        for v in violations:
            if not isinstance(v, PolicyViolation):
                raise GovernanceValidationError("All items in violations tuple must be valid PolicyViolation objects.")

            rule_name = v.rule_name.strip()
            rule_name_lower = rule_name.lower()

            # 1. Severity Refinement
            refined = v.severity
            if v.severity == ViolationSeverity.WARNING:
                if any(keyword in rule_name_lower for keyword in ("forbidden", "cycle", "security", "bypass")):
                    refined = ViolationSeverity.ERROR
            elif v.severity == ViolationSeverity.INFO:
                if any(keyword in v.message.lower() for keyword in ("not allowed", "violation")):
                    refined = ViolationSeverity.WARNING

            # 2. Priority Ranking
            base_score = 20.0
            if refined == ViolationSeverity.ERROR:
                base_score = 80.0
            elif refined == ViolationSeverity.WARNING:
                base_score = 50.0

            # Modifiers
            if any(keyword in rule_name_lower for keyword in ("coupling", "complexity", "layer")):
                base_score += 10.0
            if any(keyword in rule_name_lower for keyword in ("naming", "owner")):
                base_score -= 5.0

            # Ensure bounds [0.0, 100.0]
            priority_score = max(0.0, min(100.0, base_score))

            if priority_score >= 75.0:
                priority_tier = "HIGH"
            elif priority_score >= 40.0:
                priority_tier = "MEDIUM"
            else:
                priority_tier = "LOW"

            # 3. Root Cause Classification
            if any(kw in rule_name_lower for kw in ("dependency", "forbidden", "import")):
                root_cause = "unwanted_dependency"
            elif any(kw in rule_name_lower for kw in ("layer", "boundary")):
                root_cause = "layer_boundary_bypass"
            elif "complexity" in rule_name_lower:
                root_cause = "complexity_threshold_exceeded"
            elif "coupling" in rule_name_lower:
                root_cause = "high_coupling_detected"
            elif any(kw in rule_name_lower for kw in ("debt", "remediation", "effort")):
                root_cause = "technical_debt_limit_exceeded"
            elif "owner" in rule_name_lower:
                root_cause = "missing_ownership"
            elif any(kw in rule_name_lower for kw in ("naming", "pattern")):
                root_cause = "naming_convention_deviation"
            else:
                root_cause = "general_governance_violation"

            # 4. Impact Scope
            details_keys = v.details.keys()
            if "source" in details_keys and "target" in details_keys:
                impact_scope = "module_to_module_link"
            elif "source_layer" in details_keys:
                impact_scope = "layer_to_layer_link"
            elif "node_id" in details_keys:
                impact_scope = "individual_module"
            else:
                impact_scope = "codebase_wide"

            # 5. Suggested Remediation Metadata
            remediations = {
                "unwanted_dependency": "Remove import or configuration causing the forbidden dependency.",
                "layer_boundary_bypass": "Refactor component to preserve Clean Architecture layer boundaries.",
                "complexity_threshold_exceeded": "Deconstruct functions or methods to reduce cognitive load.",
                "high_coupling_detected": "Introduce abstractions or shared interfaces to decouple components.",
                "technical_debt_limit_exceeded": "Resolve high-priority technical debt findings to reduce total remediation effort.",
                "missing_ownership": "Add 'owner' key to module/package metadata properties.",
                "naming_convention_deviation": "Rename the module or file to match the naming convention pattern.",
            }
            suggested_remediation = remediations.get(root_cause, "Review code changes and address policy violation guidelines.")

            # Create enriched object
            enriched = EnrichedViolation(
                violation_id=v.violation_id,
                rule_id=v.rule_id,
                rule_name=rule_name,
                original_severity=v.severity,
                refined_severity=refined,
                priority_score=priority_score,
                priority_tier=priority_tier,
                root_cause=root_cause,
                impact_scope=impact_scope,
                suggested_remediation=suggested_remediation,
                original_message=v.message,
                details=dict(v.details),
            )

            enriched_list.append(enriched)

            # Grouping by rule
            if rule_name not in rule_groups:
                rule_groups[rule_name] = []
            rule_groups[rule_name].append(enriched)

            # Track counts
            severity_counts[refined.value] = severity_counts.get(refined.value, 0) + 1

        # 6. Preserve deterministic ordering: sort enriched list alphabetically by rule_name and message
        enriched_list.sort(key=lambda x: (x.rule_name.lower(), x.original_message.lower()))

        # Sort the list in each group as well
        sorted_groups: Dict[str, Tuple[EnrichedViolation, ...]] = {}
        for r_name in sorted(rule_groups.keys(), key=lambda s: s.lower()):
            grp = rule_groups[r_name]
            grp.sort(key=lambda x: (x.rule_name.lower(), x.original_message.lower()))
            sorted_groups[r_name] = tuple(grp)

        return GovernanceViolationReport(
            report_id=uuid.uuid4(),
            project_id=project_id,
            commit_id=commit_id.strip(),
            generated_at=datetime.now(timezone.utc),
            violations=tuple(enriched_list),
            violations_by_rule=sorted_groups,
            violations_by_severity=severity_counts,
            extra_info={},
        )
