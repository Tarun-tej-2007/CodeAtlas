"""Decision drift analyzer service implementation detecting structural intent divergences."""

import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.decision.enums import DecisionStatus
from app.decision.exceptions import DecisionValidationError
from app.decision.interfaces import DecisionDriftAnalyzer
from app.decision.models import ArchitectureDecision, DecisionDrift, DecisionDriftReport, DecisionTraceGraph


class DecisionDriftAnalyzerService(DecisionDriftAnalyzer):
    """Concrete DecisionDriftAnalyzer service implementing intent divergence checks."""

    def analyze_drift(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        decisions: Tuple[ArchitectureDecision, ...],
        trace_graph: DecisionTraceGraph,
        dependency_graph: Optional[Any] = None,
        arch_result: Optional[Any] = None,
        governance_result: Optional[Any] = None,
        evolution_result: Optional[Any] = None,
    ) -> DecisionDriftReport:
        """Analyzes divergence between architectural intent and implementation state.

        Args:
            project_id: Associated project identifier.
            commit_id: Associated Git commit hash.
            decisions: Registered decisions to evaluate.
            trace_graph: Traceability graph mapping decisions to code targets.
            dependency_graph: Optional dependency graph output.
            arch_result: Optional architecture analysis result.
            governance_result: Optional governance check result.
            evolution_result: Optional evolution trend result.

        Returns:
            The compiled DecisionDriftReport DTO.

        Raises:
            DecisionValidationError: If inputs are invalid or contradictory.
        """
        if project_id is None:
            raise DecisionValidationError("project_id must not be None.")
        if not commit_id or not commit_id.strip():
            raise DecisionValidationError("commit_id must be a non-empty string.")
        if decisions is None:
            raise DecisionValidationError("decisions collection must not be None.")
        if trace_graph is None or not isinstance(trace_graph, DecisionTraceGraph):
            raise DecisionValidationError("trace_graph must be a valid DecisionTraceGraph instance.")

        drift_findings: List[DecisionDrift] = []

        # Map decisions by ID for lookup
        dec_map = {d.decision_id: d for d in decisions}

        for dec in decisions:
            if not isinstance(dec, ArchitectureDecision):
                raise DecisionValidationError("All items in decisions must be valid ArchitectureDecision instances.")

            dec_id = dec.decision_id
            targets = dec.metadata.extra_info.get("targets") or ()
            if isinstance(targets, str):
                targets = (targets,)

            # 1. Detect Orphaned Decisions
            if dec.status in (DecisionStatus.ACCEPTED, DecisionStatus.PROPOSED) and not targets:
                drift_findings.append(
                    DecisionDrift(
                        drift_id=uuid.uuid4(),
                        decision_id=dec_id,
                        classification="orphaned_decision",
                        severity="medium",
                        message=f"Decision '{dec.title}' is in {dec.status.value} status but defines no traceability targets.",
                        details={},
                    )
                )

        # 2. Check each link in trace graph for broken traceability / missing implementation / conflicts
        # Keep track of unique target-decision pairs to eliminate duplicate findings
        seen_findings = set()

        for link in trace_graph.links:
            dec_id = link.decision_id
            dec = dec_map.get(dec_id)
            if not dec:
                # If trace link refers to a decision not in current analysis payload, skip or log
                continue

            target_id = link.target_id
            target_type = link.target_type

            # File Target validation -> Missing Implementation / Broken Traceability
            if target_type == "file":
                # Check dependency graph nodes list
                has_node = False
                if dependency_graph is not None:
                    # Support networkx graph or custom dependency graph wrapper
                    if hasattr(dependency_graph, "has_node"):
                        has_node = dependency_graph.has_node(target_id)
                    elif hasattr(dependency_graph, "nodes"):
                        # If nodes is a collection
                        if hasattr(dependency_graph.nodes, "keys"):
                            has_node = target_id in dependency_graph.nodes.keys()
                        else:
                            has_node = target_id in dependency_graph.nodes
                else:
                    # If dependency graph is not supplied but target is specified, consider it broken traceability
                    has_node = False

                if not has_node:
                    finding_key = (dec_id, "missing_implementation", target_id)
                    if finding_key not in seen_findings:
                        seen_findings.add(finding_key)
                        drift_findings.append(
                            DecisionDrift(
                                drift_id=uuid.uuid4(),
                                decision_id=dec_id,
                                classification="missing_implementation",
                                severity="high",
                                message=f"Implementation file '{target_id}' declared in decision '{dec.title}' is missing.",
                                details={"target_id": target_id, "target_type": "file"},
                            )
                        )

            # Policy Target validation -> Governance Conflict
            elif target_type == "policy":
                has_conflict = False
                conflict_msg = ""
                if governance_result is not None:
                    # If governance result has failed or contains violations matching target_id
                    violations = getattr(governance_result, "violations", ()) or ()
                    for viol in violations:
                        rule_name = getattr(viol, "rule_name", "")
                        rule_id = getattr(viol, "rule_id", None)
                        if rule_name == target_id or str(rule_id) == target_id:
                            has_conflict = True
                            conflict_msg = getattr(viol, "message", "")
                            break

                if has_conflict:
                    finding_key = (dec_id, "governance_conflict", target_id)
                    if finding_key not in seen_findings:
                        seen_findings.add(finding_key)
                        drift_findings.append(
                            DecisionDrift(
                                drift_id=uuid.uuid4(),
                                decision_id=dec_id,
                                classification="governance_conflict",
                                severity="high",
                                message=f"Governance conflict: target policy '{target_id}' has violation: '{conflict_msg}'.",
                                details={"target_id": target_id, "target_type": "policy"},
                            )
                        )

            # Evolution Target validation -> Evolution Divergence
            elif target_type == "evolution":
                has_divergence = False
                if evolution_result is not None:
                    # E.g. check if evolution result has risks or regression
                    # Let's check for risk items or status
                    status = getattr(evolution_result, "status", None)
                    if status and str(status).lower() in ("failed", "critical", "risk", "warning"):
                        has_divergence = True

                if has_divergence:
                    finding_key = (dec_id, "evolution_divergence", target_id)
                    if finding_key not in seen_findings:
                        seen_findings.add(finding_key)
                        drift_findings.append(
                            DecisionDrift(
                                drift_id=uuid.uuid4(),
                                decision_id=dec_id,
                                classification="evolution_divergence",
                                severity="medium",
                                message=f"Evolution trend shows regression for target '{target_id}' in decision '{dec.title}'.",
                                details={"target_id": target_id, "target_type": "evolution"},
                            )
                        )

        # 3. Preserve deterministic ordering: sort drifts alphabetically by classification, severity, then message
        drift_findings.sort(key=lambda d: (d.classification, d.severity, d.message))

        # Group findings by classification deterministically
        grouped: Dict[str, List[DecisionDrift]] = {}
        for d in drift_findings:
            if d.classification not in grouped:
                grouped[d.classification] = []
            grouped[d.classification].append(d)

        sorted_grouped = {}
        for key in sorted(grouped.keys()):
            sorted_grouped[key] = tuple(grouped[key])

        return DecisionDriftReport(
            report_id=uuid.uuid4(),
            project_id=project_id,
            commit_id=commit_id.strip(),
            drifts=tuple(drift_findings),
            drifts_by_classification=sorted_grouped,
            extra_info={},
        )
