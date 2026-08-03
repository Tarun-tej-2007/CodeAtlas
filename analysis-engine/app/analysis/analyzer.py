"""AI Code Analyzer Abstract Interface module.

Defines the core analyzer interface contract for downstream AI analysis services.
"""

from abc import ABC, abstractmethod

from app.analysis.models import AnalysisResult


class CodeAnalyzer(ABC):
    """Abstract base class defining the contract for AI-powered code analyzers."""

    @abstractmethod
    def analyze(self, *args, **kwargs) -> AnalysisResult:
        """Executes source code analysis and constructs a structured AnalysisResult.

        Must be implemented by concrete engine implementations without leaking details of
        specific LLM vendors or parser backends.
        """
        pass
