"""Architecture Analyzer Interface."""

from abc import ABC, abstractmethod

from app.architecture_analysis.models import ArchitectureReport


class ArchitectureAnalyzer(ABC):
    """Abstract interface defining the contract for executing architecture analysis."""

    @abstractmethod
    def analyze(self, *args, **kwargs) -> ArchitectureReport:
        """Executes architecture analysis and returns an ArchitectureReport.

        Must be implemented by concrete subclasses.
        """
        pass
