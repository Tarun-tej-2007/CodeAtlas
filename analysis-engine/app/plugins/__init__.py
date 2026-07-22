"""Language plugin foundation package.

Provides abstract LanguagePlugin structures and PluginRegistry containers.
"""

from app.plugins.base import LanguagePlugin
from app.plugins.registry import PluginRegistry
from app.plugins.exceptions import (
    PluginError,
    DuplicatePluginError,
    PluginNotFoundError,
)

__all__ = [
    "LanguagePlugin",
    "PluginRegistry",
    "PluginError",
    "DuplicatePluginError",
    "PluginNotFoundError",
]
