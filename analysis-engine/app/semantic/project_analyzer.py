"""Abstract project-level semantic analyzer interface module."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from app.semantic.models import SemanticResult
from app.semantic.project_models import ProjectSemanticResult


class ProjectSemanticAnalyzer(ABC):
    """Abstract interface defining the contract for executing project-wide cross-file semantic analyses."""

    @abstractmethod
    def analyze_project(self, file_results: Dict[Path, SemanticResult]) -> ProjectSemanticResult:
        """Executes project-wide semantic analysis (such as cross-file symbol resolution and import linking).

        Args:
            file_results: Mapping of project file paths to their file-level SemanticResult.

        Returns:
            The aggregated ProjectSemanticResult.

        Raises:
            SemanticAnalysisError: If project-wide analysis fails.
        """
        pass
