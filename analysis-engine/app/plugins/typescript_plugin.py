"""TypeScript language plugin implementation."""

from app.scanner.models import Language
from app.plugins.base import LanguagePlugin
from app.parser import SourceCodeParser, TypeScriptParser


class TypeScriptPlugin(LanguagePlugin):
    """Concrete LanguagePlugin for the TypeScript programming language."""

    def __init__(self) -> None:
        """Initializes the TypeScript plugin and sets up parser cache."""
        self._parser: TypeScriptParser | None = None

    @property
    def language(self) -> Language:
        return Language.TYPESCRIPT

    @property
    def extensions(self) -> set[str]:
        return {".ts", ".tsx"}

    def get_parser(self) -> SourceCodeParser:
        """Returns the TypeScript Tree-sitter parser instance."""
        if self._parser is None:
            self._parser = TypeScriptParser()
        return self._parser

