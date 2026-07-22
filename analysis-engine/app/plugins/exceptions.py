"""Plugin exceptions definitions."""


class PluginError(Exception):
    """Base exception class for all language plugin registry errors."""

    pass


class DuplicatePluginError(PluginError):
    """Raised when registering a plugin for a language that already has a registered plugin."""

    pass


class PluginNotFoundError(PluginError):
    """Raised when attempting to retrieve a plugin that is not registered."""

    pass
