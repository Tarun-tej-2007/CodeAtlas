"""Compliance scoring engine service implementation."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from app.governance.enums import ViolationSeverity
from app.governance.exceptions import GovernanceValidationError
from app.governance.interfaces import ComplianceScorer
from app.governance.models import ComplianceReport, ComplianceScore, GovernanceViolationReport


class ComplianceScoringService(ComplianceScorer):
    """Concrete ComplianceScorer service computing overall and category-level compliance scores."""

    def calculate_compliance(
        self,
        violation_report: GovernanceViolationReport,
        history: Optional[Tuple[Any, ...]] = None,
    ) -> ComplianceReport:
        """Computes compliance metrics scoring from the GovernanceViolationReport.

        Args:
            violation_report: Enriched GovernanceViolationReport input.
            history: Optional trailing historical trend context list to adjust score.

        Returns:
            The compiled ComplianceReport DTO.

        Raises:
            GovernanceValidationError: If validation checks fail.
        """
        if violation_report is None:
            raise GovernanceValidationError("violation_report must not be None.")
        if not isinstance(violation_report, GovernanceViolationReport):
            raise GovernanceValidationError("violation_report must be a valid GovernanceViolationReport instance.")

        # Check execution cache
        from app.governance.cache import execution_cache, make_hashable
        cache = execution_cache.get()
        cache_key = None
        if cache is not None:
            cache_key = make_hashable(("calculate_compliance", violation_report, history))
            if cache_key in cache:
                return cache[cache_key]

        # 1. Base Score setup
        overall_score = 100.0
        category_scores: Dict[str, float] = {
            "dependency": 100.0,
            "layer": 100.0,
            "metric": 100.0,
            "naming": 100.0,
            "ownership": 100.0,
            "quality": 100.0,
        }

        # Deductions mapping per refined severity level
        deductions = {
            ViolationSeverity.ERROR: 15.0,
            ViolationSeverity.WARNING: 5.0,
            ViolationSeverity.INFO: 1.0,
        }

        # 2. Category classification and score deductions
        for v in violation_report.violations:
            # Map root cause to category
            rc = v.root_cause
            if rc == "unwanted_dependency":
                cat = "dependency"
            elif rc == "layer_boundary_bypass":
                cat = "layer"
            elif rc in ("complexity_threshold_exceeded", "high_coupling_detected"):
                cat = "metric"
            elif rc == "naming_convention_deviation":
                cat = "naming"
            elif rc == "missing_ownership":
                cat = "ownership"
            elif rc == "technical_debt_limit_exceeded":
                cat = "quality"
            else:
                cat = "quality"

            deduction = deductions.get(v.refined_severity, 5.0)
            overall_score -= deduction
            category_scores[cat] -= deduction

        # Clip scores to [0.0, 100.0]
        overall_score = max(0.0, min(100.0, overall_score))
        for cat in category_scores:
            category_scores[cat] = max(0.0, min(100.0, category_scores[cat]))

        # Sort category scores dictionary keys alphabetically for absolute determinism
        sorted_category_scores = {k: category_scores[k] for k in sorted(category_scores.keys())}

        # 3. Repository score calculation
        repository_score = max(0.0, 100.0 - (5.0 * len(violation_report.violations)))

        # 4. Trend-aware compliance adjustments
        trend_adjustment = 0.0
        if history:
            prev_scores = []
            for item in history:
                if hasattr(item, "compliance_score") and hasattr(item.compliance_score, "overall_score"):
                    prev_scores.append(item.compliance_score.overall_score)
                elif isinstance(item, dict) and "compliance_score" in item:
                    prev_scores.append(item["compliance_score"].get("overall_score", 100.0))

            if prev_scores:
                # Compare against the average of recent historical runs
                avg_history = sum(prev_scores) / len(prev_scores)
                diff = overall_score - avg_history
                # Cap adjustment to maximum +/- 5.0 points
                trend_adjustment = round(max(-5.0, min(5.0, diff * 0.1)), 2)
            else:
                # Count historical violation numbers
                hist_violation_counts = []
                for h_rep in history:
                    if hasattr(h_rep, "violations"):
                        hist_violation_counts.append(len(h_rep.violations))

                if hist_violation_counts:
                    avg_violations = sum(hist_violation_counts) / len(hist_violation_counts)
                    current_violations = len(violation_report.violations)
                    if current_violations < avg_violations:
                        trend_adjustment = 5.0  # Positive improvement adjustment bonus
                    elif current_violations > avg_violations:
                        trend_adjustment = -5.0  # Negative regression adjustment penalty

        final_overall_score = max(0.0, min(100.0, overall_score + trend_adjustment))

        # Deterministic sorting of category scores dict
        sorted_category_scores = {k: category_scores[k] for k in sorted(category_scores.keys())}

        # Coverage drops as rule violations increase
        policy_coverage = max(0.0, 100.0 - (5.0 * len(violation_report.violations_by_rule)))

        # 6. Construct ComplianceScore DTO
        comp_score = ComplianceScore(
            score_id=uuid.uuid4(),
            overall_score=final_overall_score,
            category_scores=sorted_category_scores,
            repository_score=repository_score,
            trend_adjustment=trend_adjustment,
            policy_coverage=policy_coverage,
        )

        # 7. Construct and return ComplianceReport DTO
        report = ComplianceReport(
            report_id=uuid.uuid4(),
            project_id=violation_report.project_id,
            commit_id=violation_report.commit_id,
            generated_at=datetime.now(timezone.utc),
            compliance_score=comp_score,
            violation_report_id=violation_report.report_id,
            extra_info={},
        )

        if cache is not None and cache_key is not None:
            cache[cache_key] = report

        return report
