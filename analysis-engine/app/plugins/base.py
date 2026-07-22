"""Language plugin abstract base class definition."""

from abc import ABC, abstractmethod

from app.scanner.models import Language
from app.parser.base import SourceCodeParser


class LanguagePlugin(ABC):
    """Abstract base class that all programming language plugins must implement."""

    @property
    @abstractmethod
    def language(self) -> Language:
        """Returns the canonical Language enum value supported by this plugin."""
        pass

    @property
    @abstractmethod
    def extensions(self) -> set[str]:
        """Returns the set of file extensions supported by this plugin (e.g., {'.py'}).

        All extension strings must include the leading dot and be lowercase.
        """
        pass

    @abstractmethod
    def get_parser(self) -> SourceCodeParser:
        """Returns a new or cached SourceCodeParser instance for this language."""
        pass

