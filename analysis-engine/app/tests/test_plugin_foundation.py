"""Unit tests for the Language Plugin Foundation and PluginRegistry."""

import unittest

from app.scanner.models import Language
from app.plugins import (
    LanguagePlugin,
    PluginRegistry,
    DuplicatePluginError,
    PluginNotFoundError,
)


class PythonPluginStub(LanguagePlugin):
    """Stub implementation of a Python LanguagePlugin."""

    @property
    def language(self) -> Language:
        return Language.PYTHON

    @property
    def extensions(self) -> set[str]:
        return {".py"}


class JavaScriptPluginStub(LanguagePlugin):
    """Stub implementation of a JavaScript LanguagePlugin."""

    @property
    def language(self) -> Language:
        return Language.JAVASCRIPT

    @property
    def extensions(self) -> set[str]:
        return {".js", ".jsx"}


class TestPluginFoundation(unittest.TestCase):
    """Tests registry operations, retrieval validation, and test isolation."""

    def setUp(self) -> None:
        # Create a new, isolated registry instance for each test run
        self.registry = PluginRegistry()
        self.py_plugin = PythonPluginStub()
        self.js_plugin = JavaScriptPluginStub()

    def test_successful_plugin_registration(self) -> None:
        # 1. Successful plugin registration
        self.registry.register(self.py_plugin)
        self.assertEqual(self.registry.get_plugin(Language.PYTHON), self.py_plugin)

    def test_duplicate_registration_rejection(self) -> None:
        # 2. Duplicate registration rejection
        self.registry.register(self.py_plugin)
        
        with self.assertRaises(DuplicatePluginError):
            self.registry.register(self.py_plugin)

    def test_plugin_lookup(self) -> None:
        # 3. Plugin lookup
        self.registry.register(self.py_plugin)
        self.registry.register(self.js_plugin)

        self.assertEqual(self.registry.get_plugin(Language.PYTHON), self.py_plugin)
        self.assertEqual(self.registry.get_plugin(Language.JAVASCRIPT), self.js_plugin)

    def test_missing_plugin_lookup_raises_error(self) -> None:
        # 4. Missing plugin lookup
        with self.assertRaises(PluginNotFoundError):
            self.registry.get_plugin(Language.TYPESCRIPT)

    def test_list_registered_plugins(self) -> None:
        # 5. Listing registered plugins
        self.registry.register(self.py_plugin)
        self.registry.register(self.js_plugin)

        all_plugins = self.registry.get_all_plugins()
        self.assertEqual(len(all_plugins), 2)
        self.assertIn(self.py_plugin, all_plugins)
        self.assertIn(self.js_plugin, all_plugins)

    def test_registry_isolation_between_tests(self) -> None:
        # 6. Registry isolation: self.registry is clean and empty
        self.assertEqual(len(self.registry.get_all_plugins()), 0)


if __name__ == "__main__":
    unittest.main()
