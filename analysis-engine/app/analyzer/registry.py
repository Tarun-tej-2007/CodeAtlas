"""Analyzer registry module.

Provides the AnalyzerRegistry class for registering and retrieving static analyzers.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.analyzer.analyzer import BaseAnalyzer


class AnalyzerRegistry:
    """Registry managing static analyzer implementations."""

    def __init__(self) -> None:
        """Initializes an empty analyzer registry."""
        self._analyzers: list["BaseAnalyzer"] = []

    def register(self, analyzer: "BaseAnalyzer") -> None:
        """Registers a static analyzer instance.

        Args:
            analyzer: Concrete instance of BaseAnalyzer.
        """
        self._analyzers.append(analyzer)

    def get_all(self) -> list["BaseAnalyzer"]:
        """Returns a list of all registered static analyzers.

        Returns:
            List of BaseAnalyzer instances.
        """
        return list(self._analyzers)

    def clear(self) -> None:
        """Clears all registered static analyzers."""
        self._analyzers.clear()
