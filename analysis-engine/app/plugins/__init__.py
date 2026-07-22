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
from app.plugins.python_plugin import PythonPlugin
from app.plugins.javascript_plugin import JavaScriptPlugin
from app.plugins.typescript_plugin import TypeScriptPlugin

__all__ = [
    "LanguagePlugin",
    "PluginRegistry",
    "PluginError",
    "DuplicatePluginError",
    "PluginNotFoundError",
    "PythonPlugin",
    "JavaScriptPlugin",
    "TypeScriptPlugin",
]
