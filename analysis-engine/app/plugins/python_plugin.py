"""Python language plugin implementation."""

from app.scanner.models import Language
from app.plugins.base import LanguagePlugin
from app.parser import SourceCodeParser, PythonParser


class PythonPlugin(LanguagePlugin):
    """Concrete LanguagePlugin for the Python programming language."""

    def __init__(self) -> None:
        """Initializes the Python plugin and sets up parser cache."""
        self._parser: PythonParser | None = None

    @property
    def language(self) -> Language:
        return Language.PYTHON

    @property
    def extensions(self) -> set[str]:
        return {".py"}

    def get_parser(self) -> SourceCodeParser:
        """Returns the Python Tree-sitter parser instance."""
        if self._parser is None:
            self._parser = PythonParser()
        return self._parser

