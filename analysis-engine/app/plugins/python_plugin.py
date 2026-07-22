"""Python language plugin implementation."""

from app.scanner.models import Language
from app.plugins.base import LanguagePlugin


class PythonPlugin(LanguagePlugin):
    """Concrete LanguagePlugin for the Python programming language."""

    @property
    def language(self) -> Language:
        return Language.PYTHON

    @property
    def extensions(self) -> set[str]:
        return {".py"}
