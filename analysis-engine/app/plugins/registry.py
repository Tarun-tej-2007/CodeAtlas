"""Language plugin registry class."""

from app.scanner.models import Language
from app.plugins.base import LanguagePlugin
from app.plugins.exceptions import DuplicatePluginError, PluginNotFoundError


class PluginRegistry:
    """Registry container managing registered language plugins."""

    def __init__(self) -> None:
        """Initializes an empty PluginRegistry instance."""
        self._plugins: dict[Language, LanguagePlugin] = {}

    def register(self, plugin: LanguagePlugin) -> None:
        """Registers a language plugin.

        Args:
            plugin: An instance of a LanguagePlugin.

        Raises:
            DuplicatePluginError: If a plugin for this language already exists.
        """
        lang = plugin.language
        if lang in self._plugins:
            raise DuplicatePluginError(f"Plugin for language '{lang.value}' is already registered.")
        self._plugins[lang] = plugin

    def get_plugin(self, language: Language) -> LanguagePlugin:
        """Retrieves the plugin associated with a given Language enum.

        Args:
            language: The Language to look up.

        Returns:
            The registered LanguagePlugin instance.

        Raises:
            PluginNotFoundError: If no plugin is registered for the language.
        """
        if language not in self._plugins:
            raise PluginNotFoundError(f"No plugin registered for language '{language.value}'.")
        return self._plugins[language]

    def get_all_plugins(self) -> list[LanguagePlugin]:
        """Returns all currently registered plugins.

        Returns:
            A list of LanguagePlugin instances.
        """
        return list(self._plugins.values())
