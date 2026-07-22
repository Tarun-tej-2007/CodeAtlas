"""Base parser abstraction module."""

from abc import ABC, abstractmethod
from typing import Any

from app.scanner.models import Language


class SourceCodeParser(ABC):
    """Abstract base class that all programming language parsers must implement."""

    @property
    @abstractmethod
    def parser_id(self) -> str:
        """Returns the unique identifier of the parser implementation."""
        pass

    @property
    @abstractmethod
    def language(self) -> Language:
        """Returns the programming language supported by this parser instance."""
        pass

    @abstractmethod
    def parse(self, source_code: str) -> Any:
        """Parses the raw source code string into a syntax tree representation.

        Args:
            source_code: The raw source code to parse.

        Returns:
            The parsed AST structure.

        Raises:
            ParseError: If parsing fails due to syntax or structural issues.
        """
        pass
