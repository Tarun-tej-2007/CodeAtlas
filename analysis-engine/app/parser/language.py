"""Language enum module.

Defines canonical programming language identifiers for the CodeAtlas parser subsystem.
"""

from enum import StrEnum
from app.parser.exceptions import UnsupportedLanguageError


class Language(StrEnum):
    """Canonical programming language identifiers supported by the parser engine."""

    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"

    @classmethod
    def from_str(cls, value: str) -> "Language":
        """Maps string representation or file extension to a canonical Language enum.

        Args:
            value: Language string name (e.g. 'JavaScript', 'typescript') or extension ('.js', '.ts').

        Returns:
            Language enum member.

        Raises:
            UnsupportedLanguageError: If string cannot be mapped to a supported Language.
        """
        normalized = value.strip().lower()
        if normalized in ("javascript", "js", ".js", ".jsx"):
            return cls.JAVASCRIPT
        if normalized in ("typescript", "ts", ".ts", ".tsx"):
            return cls.TYPESCRIPT
        raise UnsupportedLanguageError(f"Unsupported programming language: '{value}'")
