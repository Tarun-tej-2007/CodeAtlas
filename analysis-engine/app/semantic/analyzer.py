"""Abstract semantic analyzer interface module."""

from abc import ABC, abstractmethod

from app.parser.models import ParseResult
from app.semantic.models import SemanticResult


class SemanticAnalyzer(ABC):
    """Abstract interface defining the contract for all programming language semantic analyzers."""

    @abstractmethod
    def analyze(self, parse_result: ParseResult) -> SemanticResult:
        """Performs semantic resolution, extracting symbols, lexical scopes, and cross-references.

        Args:
            parse_result: The aggregated parser pipeline outputs.

        Returns:
            The resolved SemanticResult representation.

        Raises:
            SemanticAnalysisError: If semantic analysis or symbol extraction fails.
        """
        pass
