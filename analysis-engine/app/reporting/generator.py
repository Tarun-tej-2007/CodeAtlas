"""Report Domain Generator Interface Module."""

from abc import ABC, abstractmethod
from typing import Any

from app.reporting.enums import ReportFormat
from app.reporting.models import AnalysisReport


class ReportGenerator(ABC):
    """Pure abstract base class establishing the contract for Report Generators."""

    @abstractmethod
    def generate(
        self, *, project_name: str, context: Any, format: ReportFormat, **kwargs
    ) -> AnalysisReport:
        """Generates an AnalysisReport dynamically based on project context and format.

        Args:
            project_name: The target project identifier.
            context: The shared context containing input results.
            format: Target output layout format.

        Returns:
            An immutable AnalysisReport instance.
        """
        pass
