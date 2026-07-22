"""TypeScript language plugin implementation."""

from app.scanner.models import Language
from app.plugins.base import LanguagePlugin


class TypeScriptPlugin(LanguagePlugin):
    """Concrete LanguagePlugin for the TypeScript programming language."""

    @property
    def language(self) -> Language:
        return Language.TYPESCRIPT

    @property
    def extensions(self) -> set[str]:
        return {".ts", ".tsx"}
