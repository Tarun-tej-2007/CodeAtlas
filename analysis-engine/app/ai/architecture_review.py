"""AI Architecture Review Engine synthesizing analysis artifacts into reports."""

import uuid
from typing import Any, List, Optional, Tuple

from app.ai.enums import RecommendationCategory, RecommendationPriority
from app.ai.exceptions import AIValidationError
from app.ai.interfaces import ArchitectureReviewer
from app.ai.models import (
    AIAnalysis,
    AIContext,
    AIRecommendation,
    ArchitectureReview,
    ArchitectureRisk,
    ArchitectureStrength,
    ArchitectureWeakness,
    RefactoringRoadmap,
)


class ArchitectureReviewService(ArchitectureReviewer):
    """Concrete ArchitectureReviewer service implementing synthesis of context & findings."""

    def __init__(self) -> None:
        """Initializes the architecture review service."""
        pass

    def generate_review(
        self,
        context: AIContext,
        analysis: AIAnalysis,
        recommendations: Tuple[AIRecommendation, ...],
    ) -> ArchitectureReview:
        """Synthesizes context facts, run diagnostics, and recommendations into an ArchitectureReview.

        Args:
            context: Collected codebase facts context.
            analysis: Associated AIAnalysis run details.
            recommendations: Set of resolved recommendations.

        Returns:
            The compiled immutable ArchitectureReview report.

        Raises:
            AIValidationError: If input validation fails.
        """
        # Fail-fast validation
        if context is None:
            raise AIValidationError("context must not be None.")
        if analysis is None:
            raise AIValidationError("analysis must not be None.")
        if recommendations is None:
            raise AIValidationError("recommendations must not be None.")

        from app.ai.cache import execution_cache, make_hashable
        cache = execution_cache.get()
        cache_key = None
        if cache is not None:
            cache_key = make_hashable(("generate_review", context, analysis, recommendations))
            if cache_key in cache:
                return cache[cache_key]

        # Match project and commit IDs
        if context.project_id != analysis.project_id:
            raise AIValidationError("context and analysis project_id mismatch.")
        if context.commit_id != analysis.commit_id:
            raise AIValidationError("context and analysis commit_id mismatch.")

        # 1. Executive Summary compilation
        rec_counts = {p: 0 for p in RecommendationPriority}
        for rec in recommendations:
            rec_counts[rec.priority] += 1

        counts_summary = ", ".join(f"{count} {p.value}" for p, count in rec_counts.items() if count > 0)
        summary_details = f" Found {counts_summary} recommendations." if counts_summary else " No issues were identified."
        executive_summary = (
            f"Architecture review report compiled for project {context.project_id} at commit {context.commit_id} "
            f"using review mode '{analysis.analysis_type.value}'.{summary_details}"
        )

        # 2. Health Score evaluation
        # Critical = -15, High = -10, Medium = -5, Low = -2
        # Governance violation = -5 each, Architecture issue = -3 each
        health_score = 100.0
        for rec in recommendations:
            if rec.priority == RecommendationPriority.CRITICAL:
                health_score -= 15.0
            elif rec.priority == RecommendationPriority.HIGH:
                health_score -= 10.0
            elif rec.priority == RecommendationPriority.MEDIUM:
                health_score -= 5.0
            elif rec.priority == RecommendationPriority.LOW:
                health_score -= 2.0

        if context.governance_violations:
            health_score -= 5.0 * len(context.governance_violations)
        if context.architecture_issues:
            health_score -= 3.0 * len(context.architecture_issues)

        health_score = max(0.0, min(100.0, health_score))

        # 3. Strengths compilation
        strengths_list: List[ArchitectureStrength] = []
        if not context.governance_violations:
            strengths_list.append(
                ArchitectureStrength(
                    title="Strict Governance Rule Compliance",
                    description="No compliance policy or architectural rule violations were flagged during verification.",
                    category="governance",
                    affected_components=(),
                )
            )
        if context.files_count > 0:
            strengths_list.append(
                ArchitectureStrength(
                    title="Modular Separation",
                    description=f"The project successfully defines {context.files_count} modular structures.",
                    category="modularization",
                    affected_components=(),
                )
            )
        if context.decisions_summary:
            strengths_list.append(
                ArchitectureStrength(
                    title="Documented Architecture Intent",
                    description=f"The team maintains {len(context.decisions_summary)} architecture decision records.",
                    category="documentation",
                    affected_components=(),
                )
            )

        # If no strengths found, provide default fallback
        if not strengths_list:
            strengths_list.append(
                ArchitectureStrength(
                    title="Standard Repository Layout",
                    description="Codebase conforms to standard project structuring conventions.",
                    category="layout",
                    affected_components=(),
                )
            )

        # Sort strengths deterministically
        strengths = tuple(sorted(strengths_list, key=lambda s: (s.category, s.title.lower())))

        # 4. Weaknesses compilation
        weaknesses_list: List[ArchitectureWeakness] = []
        # Add weaknesses from recommendations (ARCHITECTURE, REFACTORING, TECHNICAL_DEBT)
        for rec in recommendations:
            if rec.category in (RecommendationCategory.ARCHITECTURE, RecommendationCategory.REFACTORING, RecommendationCategory.TECHNICAL_DEBT):
                weaknesses_list.append(
                    ArchitectureWeakness(
                        title=rec.title,
                        description=rec.description,
                        severity=rec.priority.value,
                        affected_components=rec.affected_files,
                    )
                )

        # Add weaknesses from architecture issues
        if context.architecture_issues:
            for issue_str in context.architecture_issues:
                weaknesses_list.append(
                    ArchitectureWeakness(
                        title="Structural violation issue",
                        description=issue_str,
                        severity="warning",
                        affected_components=(),
                    )
                )

        # Remove duplicate weaknesses (same title, description, severity)
        seen_weaknesses = set()
        unique_weaknesses = []
        for w in weaknesses_list:
            key = (w.title.lower(), w.description.lower(), w.severity)
            if key not in seen_weaknesses:
                seen_weaknesses.add(key)
                unique_weaknesses.append(w)

        weaknesses = tuple(sorted(unique_weaknesses, key=lambda w: (w.severity, w.title.lower())))

        # 5. Risks compilation
        risks_list: List[ArchitectureRisk] = []
        # Add risks from recommendations (SECURITY, PERFORMANCE, DEPENDENCY)
        for rec in recommendations:
            if rec.category in (RecommendationCategory.SECURITY, RecommendationCategory.PERFORMANCE, RecommendationCategory.DEPENDENCY):
                likelihood = "high" if rec.priority in (RecommendationPriority.CRITICAL, RecommendationPriority.HIGH) else "medium"
                impact = "high" if rec.category == RecommendationCategory.SECURITY else "medium"
                mitigation = rec.suggested_fix or "Establish structural constraints check."
                risks_list.append(
                    ArchitectureRisk(
                        title=rec.title,
                        description=rec.description,
                        likelihood=likelihood,
                        impact=impact,
                        mitigation=mitigation,
                    )
                )

        seen_risks = set()
        unique_risks = []
        for r in risks_list:
            key = (r.title.lower(), r.description.lower())
            if key not in seen_risks:
                seen_risks.add(key)
                unique_risks.append(r)

        risks = tuple(sorted(unique_risks, key=lambda r: (r.likelihood, r.title.lower())))

        # 6. Refactoring Roadmap compilation
        phases = []
        if rec_counts[RecommendationPriority.CRITICAL] > 0 or rec_counts[RecommendationPriority.HIGH] > 0:
            phases.append("Phase 1: Address critical and high-priority structural risks.")
        if rec_counts[RecommendationPriority.MEDIUM] > 0:
            phases.append("Phase 2: Perform medium-priority refactoring and cleanup.")
        if rec_counts[RecommendationPriority.LOW] > 0:
            phases.append("Phase 3: Tackle low-priority tech debt optimization tasks.")

        if not phases:
            phases.append("Phase 1: Continuous monitoring of structural rules compliance.")

        workload = "high" if (rec_counts[RecommendationPriority.CRITICAL] + rec_counts[RecommendationPriority.HIGH]) > 2 else "medium"
        if len(recommendations) == 0:
            workload = "low"

        roadmap = RefactoringRoadmap(
            phases=tuple(phases),
            estimated_workload=workload,
            prerequisites=("Perform dependency verification build",),
        )

        # 7. Actions and recommendations
        immediate_actions_list = []
        long_term_list = []

        for rec in recommendations:
            actions = rec.suggested_actions or (rec.title,)
            for action in actions:
                if rec.priority in (RecommendationPriority.CRITICAL, RecommendationPriority.HIGH):
                    immediate_actions_list.append(action)
                else:
                    long_term_list.append(action)

        # Default fallbacks
        if not immediate_actions_list:
            immediate_actions_list.append("Maintain compliance with current architecture policies.")
        if not long_term_list:
            long_term_list.append("Evaluate potential performance and scale optimization paths.")

        immediate_actions = tuple(sorted(list(set(immediate_actions_list))))
        long_term_recommendations = tuple(sorted(list(set(long_term_list))))

        res = ArchitectureReview(
            project_id=context.project_id,
            commit_id=context.commit_id,
            executive_summary=executive_summary,
            health_score=health_score,
            strengths=strengths,
            weaknesses=weaknesses,
            risks=risks,
            roadmap=roadmap,
            immediate_actions=immediate_actions,
            long_term_recommendations=long_term_recommendations,
        )

        if cache is not None and cache_key is not None:
            cache[cache_key] = res

        return res
