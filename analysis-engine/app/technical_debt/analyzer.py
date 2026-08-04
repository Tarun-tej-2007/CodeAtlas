"""Technical Debt Analyzer Abstract Interface module."""

from abc import ABC, abstractmethod

from app.technical_debt.models import TechnicalDebtReport


class TechnicalDebtAnalyzer(ABC):
    """Abstract base class defining the contract for codebase technical debt analyzers."""

    @abstractmethod
    def analyze(self, *args, **kwargs) -> TechnicalDebtReport:
        """Executes technical debt evaluations and compiles a TechnicalDebtReport."""
        pass
