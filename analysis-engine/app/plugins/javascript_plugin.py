"""JavaScript language plugin implementation."""

from app.scanner.models import Language
from app.plugins.base import LanguagePlugin


class JavaScriptPlugin(LanguagePlugin):
    """Concrete LanguagePlugin for the JavaScript programming language."""

    @property
    def language(self) -> Language:
        return Language.JAVASCRIPT

    @property
    def extensions(self) -> set[str]:
        return {".js", ".jsx"}
