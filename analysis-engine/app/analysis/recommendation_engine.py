"""AI Recommendation Engine module.

Implements a stateless, extensible engine that maps code findings to actionable,
deterministic recommendations using a registry of modular recommendation strategies.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import hashlib

from app.analysis.enums import RecommendationStatus
from app.analysis.models import (
    AnalysisFinding,
    AnalysisRecommendation,
    AnalysisResult,
)


class RecommendationStrategy(ABC):
    """Abstract interface defining a modular strategy for creating recommendations."""

    @abstractmethod
    def can_handle(self, finding: AnalysisFinding) -> bool:
        """Determines if the strategy is suited to handle this type of finding."""
        pass

    @abstractmethod
    def generate(self, finding: AnalysisFinding) -> AnalysisRecommendation:
        """Returns a recommendation DTO corresponding to the given finding."""
        pass


# --- Concrete Strategies ---


class EmptyRepoStrategy(RecommendationStrategy):
    """Remediation for empty repository findings."""

    def can_handle(self, finding: AnalysisFinding) -> bool:
        return finding.rule_id == "repo-empty"

    def generate(self, finding: AnalysisFinding) -> AnalysisRecommendation:
        remediation = "Populate the repository with source files to begin code quality analysis."
        h = hashlib.sha256(f"{finding.id}:{remediation}".encode("utf-8")).hexdigest()[:12]
        return AnalysisRecommendation(
            id=f"rec-empty-{h}",
            finding_id=finding.id,
            remediation=remediation,
            status=RecommendationStatus.OPEN,
            metadata={"priority": "high"},
        )


class MultiLangStrategy(RecommendationStrategy):
    """Remediation for multi-language system complexities."""

    def can_handle(self, finding: AnalysisFinding) -> bool:
        return finding.rule_id == "repo-multi-language"

    def generate(self, finding: AnalysisFinding) -> AnalysisRecommendation:
        remediation = (
            "Establish a clear directory layout or modular separation to manage "
            "multi-language boundary complexity."
        )
        h = hashlib.sha256(f"{finding.id}:{remediation}".encode("utf-8")).hexdigest()[:12]
        return AnalysisRecommendation(
            id=f"rec-multi-{h}",
            finding_id=finding.id,
            remediation=remediation,
            status=RecommendationStatus.OPEN,
            metadata={"priority": "low"},
        )


class AfferentCouplingStrategy(RecommendationStrategy):
    """Remediation for high afferent coupling core symbols."""

    def can_handle(self, finding: AnalysisFinding) -> bool:
        return finding.rule_id == "symbol-coupling-afferent"

    def generate(self, finding: AnalysisFinding) -> AnalysisRecommendation:
        remediation = (
            "Introduce interfaces, abstract base classes, or events to decouple "
            "this highly utilized symbol from its clients."
        )
        h = hashlib.sha256(f"{finding.id}:{remediation}".encode("utf-8")).hexdigest()[:12]
        return AnalysisRecommendation(
            id=f"rec-afferent-{h}",
            finding_id=finding.id,
            remediation=remediation,
            status=RecommendationStatus.OPEN,
            metadata={"priority": "medium"},
        )


class EfferentCouplingStrategy(RecommendationStrategy):
    """Remediation for excessive efferent coupling symbols."""

    def can_handle(self, finding: AnalysisFinding) -> bool:
        return finding.rule_id == "symbol-coupling-efferent"

    def generate(self, finding: AnalysisFinding) -> AnalysisRecommendation:
        remediation = (
            "Refactor the module or class to delegate responsibilities, reducing the "
            "number of external symbols depended upon."
        )
        h = hashlib.sha256(f"{finding.id}:{remediation}".encode("utf-8")).hexdigest()[:12]
        return AnalysisRecommendation(
            id=f"rec-efferent-{h}",
            finding_id=finding.id,
            remediation=remediation,
            status=RecommendationStatus.OPEN,
            metadata={"priority": "medium"},
        )


class GraphHubStrategy(RecommendationStrategy):
    """Remediation for high connection degree graph hubs."""

    def can_handle(self, finding: AnalysisFinding) -> bool:
        return finding.rule_id == "graph-node-hub"

    def generate(self, finding: AnalysisFinding) -> AnalysisRecommendation:
        remediation = (
            "Break down this file/module into smaller, single-responsibility modules "
            "to simplify the connection topology."
        )
        h = hashlib.sha256(f"{finding.id}:{remediation}".encode("utf-8")).hexdigest()[:12]
        return AnalysisRecommendation(
            id=f"rec-hub-{h}",
            finding_id=finding.id,
            remediation=remediation,
            status=RecommendationStatus.OPEN,
            metadata={"priority": "medium"},
        )


class ArchIssueStrategy(RecommendationStrategy):
    """Remediation for layering violation findings."""

    def can_handle(self, finding: AnalysisFinding) -> bool:
        return finding.rule_id is not None and finding.rule_id.startswith("arch-")

    def generate(self, finding: AnalysisFinding) -> AnalysisRecommendation:
        remediation = (
            "Refactor imports or dependencies to align with layering boundaries "
            "defined in the architecture ruleset."
        )
        h = hashlib.sha256(f"{finding.id}:{remediation}".encode("utf-8")).hexdigest()[:12]
        return AnalysisRecommendation(
            id=f"rec-arch-{h}",
            finding_id=finding.id,
            remediation=remediation,
            status=RecommendationStatus.OPEN,
            metadata={"priority": "high"},
        )


class DefaultStrategy(RecommendationStrategy):
    """Fallback strategy for all unmapped rule findings."""

    def can_handle(self, finding: AnalysisFinding) -> bool:
        return True

    def generate(self, finding: AnalysisFinding) -> AnalysisRecommendation:
        remediation = "Review the code location and address the highlighted issue accordingly."
        h = hashlib.sha256(f"{finding.id}:{remediation}".encode("utf-8")).hexdigest()[:12]
        return AnalysisRecommendation(
            id=f"rec-default-{h}",
            finding_id=finding.id,
            remediation=remediation,
            status=RecommendationStatus.OPEN,
            metadata={"priority": "low"},
        )


# --- Recommendation Engine Core ---


class RecommendationEngine:
    """Stateless generator that transforms codebase findings into actionable AI recommendations."""

    def __init__(self, strategies: Optional[List[RecommendationStrategy]] = None) -> None:
        """Initializes the engine with custom or default strategies."""
        self.strategies = strategies if strategies is not None else self._get_default_strategies()

    def _get_default_strategies(self) -> List[RecommendationStrategy]:
        return [
            EmptyRepoStrategy(),
            MultiLangStrategy(),
            AfferentCouplingStrategy(),
            EfferentCouplingStrategy(),
            GraphHubStrategy(),
            ArchIssueStrategy(),
            DefaultStrategy(),  # Fallback must be last
        ]

    def generate_recommendations(self, result: AnalysisResult) -> AnalysisResult:
        """Processes an AnalysisResult and generates recommendations for its findings.

        Returns a new immutable AnalysisResult containing the generated recommendations.
        """
        recommendations: List[AnalysisRecommendation] = []
        diagnostics = list(result.diagnostics)
        diagnostics.append("Started recommendation generation phase.")

        seen_rec_ids = set()

        for finding in result.findings:
            # Find the first matching strategy
            for strategy in self.strategies:
                if strategy.can_handle(finding):
                    rec = strategy.generate(finding)
                    # Deduplicate recommendations by ID
                    if rec.id not in seen_rec_ids:
                        seen_rec_ids.add(rec.id)
                        recommendations.append(rec)
                    break

        # Sort recommendations deterministically by ID
        recommendations.sort(key=lambda x: x.id)

        diagnostics.append(
            f"Successfully compiled recommendations. TotalRecommendations={len(recommendations)}."
        )

        # Construct new immutable AnalysisResult
        return AnalysisResult(
            id=result.id,
            analysis_type=result.analysis_type,
            summary=result.summary,
            findings=result.findings,
            recommendations=recommendations,
            diagnostics=diagnostics,
            metadata=result.metadata,
        )
