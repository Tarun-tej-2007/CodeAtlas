"""JavaScript language plugin implementation."""

from app.scanner.models import Language
from app.plugins.base import LanguagePlugin
from app.parser import SourceCodeParser, JavaScriptParser


class JavaScriptPlugin(LanguagePlugin):
    """Concrete LanguagePlugin for the JavaScript programming language."""

    def __init__(self) -> None:
        """Initializes the JavaScript plugin and sets up parser cache."""
        self._parser: JavaScriptParser | None = None

    @property
    def language(self) -> Language:
        return Language.JAVASCRIPT

    @property
    def extensions(self) -> set[str]:
        return {".js", ".jsx"}

    def get_parser(self) -> SourceCodeParser:
        """Returns the JavaScript Tree-sitter parser instance."""
        if self._parser is None:
            self._parser = JavaScriptParser()
        return self._parser

