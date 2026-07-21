"""Base rule interface module.

Defines the abstract BaseRule interface for all quality rules in CodeAtlas.
"""

from abc import ABC, abstractmethod

from app.analyzer.calls.models import CallAnalysisResult
from app.analyzer.dependencies.models import DependencyResult
from app.analyzer.models import AnalysisContext, Diagnostic
from app.analyzer.resolution.models import ResolutionResult


class BaseRule(ABC):
    """Abstract base class interface for quality rules."""

    @abstractmethod
    def evaluate(
        self,
        context: AnalysisContext,
        dependency_result: DependencyResult | None = None,
        resolution_result: ResolutionResult | None = None,
        call_result: CallAnalysisResult | None = None,
    ) -> list[Diagnostic]:
        """Evaluates static analysis results against the quality rule.

        Args:
            context: AnalysisContext for the target document.
            dependency_result: Optional DependencyResult.
            resolution_result: Optional ResolutionResult.
            call_result: Optional CallAnalysisResult.

        Returns:
            List of emitted Diagnostic models.

        Raises:
            RuleEngineError: If rule evaluation encounters an error.
        """
        pass
