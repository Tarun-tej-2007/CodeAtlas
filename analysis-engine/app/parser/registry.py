"""Parser registry module.

Provides the ParserRegistry class for managing and retrieving language-specific parsers.
"""

from app.parser.exceptions import UnsupportedLanguageError
from app.parser.language import Language
from app.parser.parser import BaseParser


class ParserRegistry:
    """Registry managing language-specific parser implementations."""

    def __init__(self) -> None:
        """Initializes an empty parser registry."""
        self._parsers: dict[Language, BaseParser] = {}

    def register(self, language: Language, parser: BaseParser) -> None:
        """Registers a parser instance for a specific Language.

        Args:
            language: Canonical Language enum member.
            parser: Concrete implementation of BaseParser.
        """
        self._parsers[language] = parser

    def get(self, language: Language) -> BaseParser:
        """Retrieves the registered parser for a specific Language.

        Args:
            language: Canonical Language enum member.

        Returns:
            The registered BaseParser instance.

        Raises:
            UnsupportedLanguageError: If no parser is registered for the specified language.
        """
        if language not in self._parsers:
            raise UnsupportedLanguageError(
                f"No parser registered for language: '{language}'"
            )
        return self._parsers[language]

    def supported_languages(self) -> list[Language]:
        """Returns a list of all currently registered languages.

        Returns:
            List of Language enum members.
        """
        return list(self._parsers.keys())

    def clear(self) -> None:
        """Clears all registered parsers."""
        self._parsers.clear()
