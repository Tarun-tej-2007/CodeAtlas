"""Decision health analyzer service implementation evaluating adr quality and completeness."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.decision.enums import DecisionRelationshipType, DecisionStatus
from app.decision.exceptions import DecisionValidationError
from app.decision.interfaces import DecisionHealthAnalyzer
from app.decision.models import ArchitectureDecision, DecisionDriftReport, DecisionHealth, DecisionHealthReport, DecisionTraceGraph


class DecisionHealthAnalyzerService(DecisionHealthAnalyzer):
    """Concrete DecisionHealthAnalyzer service implementing quality metrics, scores and classification rules."""

    def analyze_health(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        decisions: Tuple[ArchitectureDecision, ...],
        drift_report: DecisionDriftReport,
        trace_graph: DecisionTraceGraph,
        evolution_result: Optional[Any] = None,
        governance_result: Optional[Any] = None,
    ) -> DecisionHealthReport:
        """Evaluates health, compliance quality, and document completeness of decisions.

        Args:
            project_id: Associated project identifier.
            commit_id: Associated Git commit hash.
            decisions: Collection of decisions.
            drift_report: Compiled drift analysis report.
            trace_graph: Traceability graph.
            evolution_result: Optional evolution trend result.
            governance_result: Optional governance result.

        Returns:
            The compiled DecisionHealthReport DTO.

        Raises:
            DecisionValidationError: If parameters fail validation.
        """
        if project_id is None:
            raise DecisionValidationError("project_id must not be None.")
        if not commit_id or not commit_id.strip():
            raise DecisionValidationError("commit_id must be a non-empty string.")
        if decisions is None:
            raise DecisionValidationError("decisions collection must not be None.")
        if drift_report is None or not isinstance(drift_report, DecisionDriftReport):
            raise DecisionValidationError("drift_report must be a valid DecisionDriftReport instance.")
        if trace_graph is None or not isinstance(trace_graph, DecisionTraceGraph):
            raise DecisionValidationError("trace_graph must be a valid DecisionTraceGraph instance.")

        from app.decision.cache import execution_cache, make_hashable
        cache = execution_cache.get()
        cache_key = None
        if cache is not None:
            cache_key = make_hashable((
                "analyze_health", project_id, commit_id.strip(), decisions, drift_report,
                trace_graph, evolution_result, governance_result
            ))
            if cache_key in cache:
                return cache[cache_key]

        # Baseline setup
        overall_score = 100.0
        traceability_score = 100.0
        freshness_score = 100.0
        alignment_score = 100.0
        completeness_score = 100.0

        recommendations: List[str] = []
        metrics: Dict[str, Any] = {
            "total_decisions": len(decisions),
            "stale_decisions": 0,
            "orphaned_decisions": 0,
            "drifted_decisions": 0,
            "governance_conflicts": 0,
            "inconsistent_lifecycle": 0,
            "undocumented_fields": 0,
        }

        # Date to evaluate freshness against (default to now)
        now = datetime.now(timezone.utc)

        # Map decisions by ID for drift check
        drifted_ids = {d.decision_id for d in drift_report.drifts}
        metrics["drifted_decisions"] = len(drifted_ids)

        # 1. Evaluate each decision
        for dec in decisions:
            if not isinstance(dec, ArchitectureDecision):
                raise DecisionValidationError("All items in decisions must be valid ArchitectureDecision instances.")

            targets = dec.metadata.extra_info.get("targets") or ()
            if isinstance(targets, str):
                targets = (targets,)

            # A. Traceability Completeness
            if dec.status in (DecisionStatus.ACCEPTED, DecisionStatus.PROPOSED) and not targets:
                traceability_score -= 15.0
                overall_score -= 10.0
                metrics["orphaned_decisions"] += 1
                recommendations.append("Define traceability targets for orphaned decisions.")

            # B. Decision Freshness
            age_days = (now - dec.metadata.updated_at).days
            if age_days > 180 and dec.status not in (DecisionStatus.SUPERSEDED, DecisionStatus.DEPRECATED):
                freshness_score -= 10.0
                overall_score -= 5.0
                metrics["stale_decisions"] += 1
                recommendations.append("Review and refresh stale decisions older than 6 months.")

            # C. Decision Lifecycle Consistency
            if dec.status == DecisionStatus.SUPERSEDED:
                has_supersedes_rel = any(
                    r.relationship_type in (DecisionRelationshipType.SUPERSEDED_BY, DecisionRelationshipType.SUPERSEDES)
                    for r in dec.relationships
                )
                if not has_supersedes_rel:
                    completeness_score -= 10.0
                    overall_score -= 10.0
                    metrics["inconsistent_lifecycle"] += 1
                    recommendations.append("Add SUPERSEDED_BY relationship link for superseded decisions.")

            # D. Documentation Completeness
            doc_gap = False
            for field in (dec.title, dec.context, dec.decision_text, dec.consequences):
                if not field or len(field.strip()) < 10:
                    doc_gap = True
            if doc_gap:
                completeness_score -= 15.0
                overall_score -= 5.0
                metrics["undocumented_fields"] += 1
                recommendations.append("Provide complete context and consequence documentation in ADRs.")

        # 2. Evaluate Drifts and Alignments
        for drift in drift_report.drifts:
            if drift.classification == "governance_conflict":
                alignment_score -= 15.0
                overall_score -= 10.0
                metrics["governance_conflicts"] += 1
                recommendations.append("Align decisions with active governance policy rules.")
            elif drift.classification == "evolution_divergence":
                alignment_score -= 10.0
                overall_score -= 5.0
                recommendations.append("Resolve active architecture implementation drifts.")
            else:
                alignment_score -= 5.0
                overall_score -= 5.0
                recommendations.append("Resolve active architecture implementation drifts.")

        # Governance baseline failure deduction
        if governance_result is not None:
            status = getattr(governance_result, "status", None)
            if status and str(status).lower() in ("failed", "critical"):
                alignment_score -= 10.0
                overall_score -= 10.0

        # Evolution baseline failure deduction
        if evolution_result is not None:
            status = getattr(evolution_result, "status", None)
            if status and str(status).lower() in ("failed", "critical", "risk"):
                alignment_score -= 10.0
                overall_score -= 5.0

        # Cap scores to [0.0, 100.0]
        overall_score = max(0.0, min(100.0, overall_score))
        traceability_score = max(0.0, min(100.0, traceability_score))
        freshness_score = max(0.0, min(100.0, freshness_score))
        alignment_score = max(0.0, min(100.0, alignment_score))
        completeness_score = max(0.0, min(100.0, completeness_score))

        # Classify Health
        if overall_score >= 90.0:
            classification = "Excellent"
        elif overall_score >= 75.0:
            classification = "Good"
        elif overall_score >= 60.0:
            classification = "Fair"
        elif overall_score >= 40.0:
            classification = "Poor"
        else:
            classification = "Critical"

        # Sort category scores deterministically
        category_scores = {
            "alignment": alignment_score,
            "completeness": completeness_score,
            "freshness": freshness_score,
            "traceability": traceability_score,
        }

        # Deduplicate and sort recommendations deterministically
        unique_recs = sorted(list(set(recommendations)))

        health = DecisionHealth(
            health_id=uuid.uuid4(),
            overall_score=overall_score,
            category_scores=category_scores,
            classification=classification,
            recommendations=tuple(unique_recs),
            metrics=metrics,
        )

        res = DecisionHealthReport(
            report_id=uuid.uuid4(),
            project_id=project_id,
            commit_id=commit_id.strip(),
            health=health,
            extra_info={},
        )

        if cache is not None and cache_key is not None:
            cache[cache_key] = res

        return res
