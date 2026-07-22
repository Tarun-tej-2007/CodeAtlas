"""Unit tests for Python, JavaScript, and TypeScript concrete plugins and registry integration."""

import unittest

from app.scanner.models import Language
from app.plugins import (
    PythonPlugin,
    JavaScriptPlugin,
    TypeScriptPlugin,
    PluginRegistry,
    DuplicatePluginError,
    PluginNotFoundError,
)


class TestConcretePlugins(unittest.TestCase):
    """Tests metadata definitions, extensions, and registration behavior for concrete plugins."""

    def setUp(self) -> None:
        self.registry = PluginRegistry()
        self.py_plugin = PythonPlugin()
        self.js_plugin = JavaScriptPlugin()
        self.ts_plugin = TypeScriptPlugin()

    def test_python_plugin_metadata(self) -> None:
        # 1. Python plugin metadata
        self.assertEqual(self.py_plugin.language, Language.PYTHON)
        self.assertEqual(self.py_plugin.extensions, {".py"})

    def test_javascript_plugin_metadata(self) -> None:
        # 2. JavaScript plugin metadata
        self.assertEqual(self.js_plugin.language, Language.JAVASCRIPT)
        self.assertEqual(self.js_plugin.extensions, {".js", ".jsx"})

    def test_typescript_plugin_metadata(self) -> None:
        # 3. TypeScript plugin metadata
        self.assertEqual(self.ts_plugin.language, Language.TYPESCRIPT)
        self.assertEqual(self.ts_plugin.extensions, {".ts", ".tsx"})

    def test_successful_registration(self) -> None:
        # 4. Successful registration
        self.registry.register(self.py_plugin)
        self.registry.register(self.js_plugin)
        self.registry.register(self.ts_plugin)

        all_registered = self.registry.get_all_plugins()
        self.assertEqual(len(all_registered), 3)
        self.assertIn(self.py_plugin, all_registered)
        self.assertIn(self.js_plugin, all_registered)
        self.assertIn(self.ts_plugin, all_registered)

    def test_successful_lookup(self) -> None:
        # 5. Successful lookup
        self.registry.register(self.py_plugin)
        self.registry.register(self.js_plugin)
        self.registry.register(self.ts_plugin)

        self.assertEqual(self.registry.get_plugin(Language.PYTHON), self.py_plugin)
        self.assertEqual(self.registry.get_plugin(Language.JAVASCRIPT), self.js_plugin)
        self.assertEqual(self.registry.get_plugin(Language.TYPESCRIPT), self.ts_plugin)

    def test_duplicate_registration_rejection(self) -> None:
        # 6. Duplicate registration rejection
        self.registry.register(self.py_plugin)
        with self.assertRaises(DuplicatePluginError):
            self.registry.register(PythonPlugin())

        self.registry.register(self.js_plugin)
        with self.assertRaises(DuplicatePluginError):
            self.registry.register(JavaScriptPlugin())

        self.registry.register(self.ts_plugin)
        with self.assertRaises(DuplicatePluginError):
            self.registry.register(TypeScriptPlugin())


if __name__ == "__main__":
    unittest.main()
