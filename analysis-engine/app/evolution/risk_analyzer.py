"""Concrete implementation of RiskAnalyzer."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.evolution.enums import RiskSeverity
from app.evolution.exceptions import EvolutionValidationError
from app.evolution.interfaces import RiskAnalyzer
from app.evolution.models import (
    ArchitecturalRisk,
    ArchitecturalRiskReport,
    EvolutionTrendResult,
)


class CodeAtlasArchitecturalRiskAnalyzer(RiskAnalyzer):
    """Concrete risk analyzer detecting design erosion and degradation trends across historical data."""

    def analyze_risks(self, trend_result: EvolutionTrendResult) -> ArchitecturalRiskReport:
        """Analyzes trend details to identify emerging structural risks.

        Args:
            trend_result: Input compiled EvolutionTrendResult.

        Returns:
            The generated ArchitecturalRiskReport.

        Raises:
            EvolutionValidationError: If trend_result is null or input lists are inconsistent.
        """
        if trend_result is None:
            raise EvolutionValidationError("trend_result parameter must not be None.")

        from app.evolution.cache import execution_cache
        cache = execution_cache.get()
        if cache is not None:
            trend_key = (
                f"risks:{hash(trend_result.coupling_trend)}:{hash(trend_result.complexity_trend)}:"
                f"{hash(trend_result.tech_debt_trend)}:{hash(trend_result.quality_trend)}:"
                f"{hash(trend_result.layer_stability)}:{hash(trend_result.module_growth)}"
            )
            if trend_key in cache:
                return cache[trend_key]

        # Validate trend list consistencies (e.g. check lengths)
        lengths = {
            len(trend_result.coupling_trend),
            len(trend_result.complexity_trend),
            len(trend_result.tech_debt_trend),
            len(trend_result.quality_trend),
            len(trend_result.layer_stability),
            len(trend_result.module_growth),
        }
        if len(lengths) > 1:
            raise EvolutionValidationError("Trend histories have inconsistent timeline series lengths.")

        risks: List[ArchitecturalRisk] = []

        def get_severity(score: float) -> RiskSeverity:
            if score >= 80.0:
                return RiskSeverity.CRITICAL
            if score >= 50.0:
                return RiskSeverity.HIGH
            if score >= 25.0:
                return RiskSeverity.MEDIUM
            return RiskSeverity.LOW

        summary = trend_result.summary

        # Helper to extract trend slope directions
        c_trend = summary.get("coupling_trend", "stable")
        comp_trend = summary.get("complexity_trend", "stable")
        td_trend = summary.get("tech_debt_trend", "stable")
        q_trend = summary.get("quality_trend", "stable")
        layer_stability = summary.get("layer_stability", "stable")
        growth_trend = summary.get("module_growth", "stable")

        # 1. Architectural Erosion
        if q_trend == "decreasing":
            score = 45.0
            if len(trend_result.quality_trend) > 1:
                q0 = trend_result.quality_trend[0]
                q_last = trend_result.quality_trend[-1]
                if q0 > q_last:
                    score = round(min(100.0, (q0 - q_last) * 5.0), 3)

            risks.append(
                ArchitecturalRisk(
                    name="Architectural Erosion",
                    description="Codebase quality is steadily declining across snapshot analysis commits.",
                    score=score,
                    severity=get_severity(score),
                    mitigation_recommendation="Schedule codebase refactoring sessions and establish strict quality gates.",
                )
            )

        # 2. Dependency Explosion
        if growth_trend == "increasing":
            score = 50.0
            if len(trend_result.module_growth) > 1:
                g0 = trend_result.module_growth[0]
                g_last = trend_result.module_growth[-1]
                if g_last > g0:
                    score = round(min(100.0, (g_last - g0) * 4.0), 3)

            risks.append(
                ArchitecturalRisk(
                    name="Dependency Explosion",
                    description="Repository size and component growth rates are rising exponentially.",
                    score=score,
                    severity=get_severity(score),
                    mitigation_recommendation="Enforce module subdivision standards and optimize folder boundaries.",
                )
            )

        # 3. Cyclic Dependency Growth
        # Triggered by increasing coupling
        if c_trend == "increasing":
            score = 55.0
            if len(trend_result.coupling_trend) > 1:
                c0 = trend_result.coupling_trend[0]
                c_last = trend_result.coupling_trend[-1]
                if c_last > c0:
                    score = round(min(100.0, (c_last - c0) * 80.0), 3)

            risks.append(
                ArchitecturalRisk(
                    name="Cyclic Dependency Growth",
                    description="High coupling rate suggests hidden cyclic dependency loops are forming.",
                    score=score,
                    severity=get_severity(score),
                    mitigation_recommendation="Verify circular imports and use shared interfaces or dependency inversion.",
                )
            )

        # 4. Layer Degradation
        if layer_stability == "decreasing":
            score = 40.0
            if len(trend_result.layer_stability) > 1:
                l0 = trend_result.layer_stability[0]
                l_last = trend_result.layer_stability[-1]
                if l0 > l_last:
                    score = round(min(100.0, (l0 - l_last) * 25.0), 3)

            risks.append(
                ArchitecturalRisk(
                    name="Layer Degradation",
                    description="Architectural layer boundaries are losing definition and stability.",
                    score=score,
                    severity=get_severity(score),
                    mitigation_recommendation="Re-evaluate architectural layer assignments and clean layer rule violations.",
                )
            )

        # 5. Increasing Coupling
        if c_trend == "increasing":
            score = 30.0
            if len(trend_result.coupling_trend) > 1:
                c0 = trend_result.coupling_trend[0]
                c_last = trend_result.coupling_trend[-1]
                if c_last > c0:
                    score = round(min(100.0, (c_last - c0) * 50.0), 3)

            risks.append(
                ArchitecturalRisk(
                    name="Increasing Coupling",
                    description="Average coupling metrics are increasing over historical time windows.",
                    score=score,
                    severity=get_severity(score),
                    mitigation_recommendation="Identify high-coupling components and extract modular, isolated wrappers.",
                )
            )

        # 6. Increasing Complexity
        if comp_trend == "increasing":
            score = 35.0
            if len(trend_result.complexity_trend) > 1:
                cmp0 = trend_result.complexity_trend[0]
                cmp_last = trend_result.complexity_trend[-1]
                if cmp_last > cmp0:
                    score = round(min(100.0, (cmp_last - cmp0) * 10.0), 3)

            risks.append(
                ArchitecturalRisk(
                    name="Increasing Complexity",
                    description="Cyclomatic complexity or cognitive complexity scores are rising.",
                    score=score,
                    severity=get_severity(score),
                    mitigation_recommendation="Decompose complex functions/methods into smaller cohesive components.",
                )
            )

        # 7. Technical Debt Acceleration
        if td_trend == "increasing":
            score = 40.0
            if len(trend_result.tech_debt_trend) > 1:
                td0 = trend_result.tech_debt_trend[0]
                td_last = trend_result.tech_debt_trend[-1]
                if td_last > td0:
                    score = round(min(100.0, (td_last - td0) * 10.0), 3)

            risks.append(
                ArchitecturalRisk(
                    name="Technical Debt Acceleration",
                    description="Technical debt item counts or remediation effort is rising rapidly.",
                    score=score,
                    severity=get_severity(score),
                    mitigation_recommendation="Allocate technical debt payoff tasks during sprint planning pipelines.",
                )
            )

        # 8. Module Hotspot Concentration
        if comp_trend == "increasing" and growth_trend == "increasing":
            score = 75.0
            risks.append(
                ArchitecturalRisk(
                    name="Module Hotspot Concentration",
                    description="Concurrent rises in module growth and complexity indicate hotspot nodes are forming.",
                    score=score,
                    severity=get_severity(score),
                    mitigation_recommendation="Perform refactoring on frequently modified hotspot files to decouple logic.",
                )
            )

        # Ensure deterministic ordering of reported risks alphabetically by name
        risks.sort(key=lambda r: r.name)

        overall_score = round(max([r.score for r in risks]), 3) if risks else 0.0

        report = ArchitecturalRiskReport(
            report_id=uuid.uuid4(),
            generated_at=datetime.now(timezone.utc),
            overall_risk_score=overall_score,
            risks=tuple(risks),
        )
        if cache is not None:
            trend_key = (
                f"risks:{hash(trend_result.coupling_trend)}:{hash(trend_result.complexity_trend)}:"
                f"{hash(trend_result.tech_debt_trend)}:{hash(trend_result.quality_trend)}:"
                f"{hash(trend_result.layer_stability)}:{hash(trend_result.module_growth)}"
            )
            cache[trend_key] = report
        return report
