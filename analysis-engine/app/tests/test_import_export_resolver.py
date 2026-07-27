"""Unit tests for the Import & Export Resolution Engine."""

import unittest
from pathlib import Path

from app.semantic.enums import SymbolKind
from app.semantic import (
    Location,
    SymbolLocation,
    ProjectSymbol,
    ImportDeclaration,
    ExportDeclaration,
    ProjectFile,
    ImportExportResolver,
)


class TestImportExportResolver(unittest.TestCase):
    """Tests explicit import matching, alias resolutions, duplicate exports, and resolver statelessness."""

    def setUp(self) -> None:
        self.resolver = ImportExportResolver()
        self.loc = Location(start_line=1, start_column=0, end_line=1, end_column=10)

        # Build some common locations
        self.loc_utils = SymbolLocation(file_path=Path("src/utils.py"), location=self.loc)
        self.loc_main = SymbolLocation(file_path=Path("src/main.py"), location=self.loc)

        # 1. Define utility symbols
        self.sym_helper = ProjectSymbol(
            id="sym-helper",
            name="helper",
            qualified_name="src.utils.helper",
            kind=SymbolKind.FUNCTION,
            location=self.loc_utils,
        )

        self.sym_config = ProjectSymbol(
            id="sym-config",
            name="config",
            qualified_name="src.utils.config",
            kind=SymbolKind.VARIABLE,
            location=self.loc_utils,
        )

    def test_successful_import_resolution(self) -> None:
        # File A (src/utils.py): exports helper and config
        exp_helper = ExportDeclaration(exported_name="helper", local_symbol_id="sym-helper", location=self.loc_utils)
        exp_config = ExportDeclaration(exported_name="config", local_symbol_id="sym-config", location=self.loc_utils)
        
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[self.sym_helper, self.sym_config],
            imports=[],
            exports=[exp_helper, exp_config]
        )

        # File B (src/main.py): imports helper from "./utils"
        imp_helper = ImportDeclaration(
            imported_name="helper",
            module_specifier="./utils",
            location=self.loc_main
        )

        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[],
            imports=[imp_helper],
            exports=[]
        )

        # Execute resolution
        project = {
            Path("src/utils.py"): file_utils,
            Path("src/main.py"): file_main
        }
        result = self.resolver.resolve_project_imports(project)

        # Assertions
        self.assertEqual(len(result.resolved_imports), 1)
        self.assertEqual(len(result.unresolved_imports), 0)
        self.assertEqual(len(result.diagnostics), 0)

        resolved = result.resolved_imports[0]
        self.assertEqual(resolved.import_declaration, imp_helper)
        self.assertEqual(resolved.target_file, Path("src/utils.py"))
        self.assertEqual(resolved.target_symbol.id, "sym-helper")

    def test_alias_resolution(self) -> None:
        # File A exports helper
        exp_helper = ExportDeclaration(exported_name="helper", local_symbol_id="sym-helper", location=self.loc_utils)
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[self.sym_helper],
            imports=[],
            exports=[exp_helper]
        )

        # File B imports helper as 'h'
        imp_alias = ImportDeclaration(
            imported_name="helper",
            module_specifier="./utils",
            local_alias="h",
            location=self.loc_main
        )
        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[],
            imports=[imp_alias],
            exports=[]
        )

        project = {
            Path("src/utils.py"): file_utils,
            Path("src/main.py"): file_main
        }
        result = self.resolver.resolve_project_imports(project)

        # Verification
        self.assertEqual(len(result.resolved_imports), 1)
        resolved = result.resolved_imports[0]
        self.assertEqual(resolved.import_declaration.local_alias, "h")
        self.assertEqual(resolved.target_symbol.id, "sym-helper")

    def test_unresolved_imports(self) -> None:
        # File A empty
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[],
            imports=[],
            exports=[]
        )

        # File B imports:
        # 1. non-existent module specifier
        imp_bad_module = ImportDeclaration(
            imported_name="helper",
            module_specifier="./non_existent",
            location=self.loc_main
        )
        # 2. non-existent export name in known module
        imp_bad_name = ImportDeclaration(
            imported_name="ghost",
            module_specifier="./utils",
            location=self.loc_main
        )

        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[],
            imports=[imp_bad_module, imp_bad_name],
            exports=[]
        )

        project = {
            Path("src/utils.py"): file_utils,
            Path("src/main.py"): file_main
        }
        result = self.resolver.resolve_project_imports(project)

        # Verification
        self.assertEqual(len(result.resolved_imports), 0)
        self.assertEqual(len(result.unresolved_imports), 2)
        self.assertEqual(len(result.diagnostics), 2)
        
        # Verify specific diagnostic warnings
        self.assertTrue(any("non_existent" in d for d in result.diagnostics))
        self.assertTrue(any("ghost" in d for d in result.diagnostics))

    def test_duplicate_exports_handling(self) -> None:
        # File A exports 'helper' twice (conflict/ambiguity)
        exp_helper1 = ExportDeclaration(exported_name="helper", local_symbol_id="sym-helper", location=self.loc_utils)
        exp_helper2 = ExportDeclaration(exported_name="helper", local_symbol_id="sym-config", location=self.loc_utils)
        
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[self.sym_helper, self.sym_config],
            imports=[],
            exports=[exp_helper1, exp_helper2]
        )

        # File B imports helper from A
        imp_helper = ImportDeclaration(
            imported_name="helper",
            module_specifier="./utils",
            location=self.loc_main
        )
        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[],
            imports=[imp_helper],
            exports=[]
        )

        project = {
            Path("src/utils.py"): file_utils,
            Path("src/main.py"): file_main
        }
        result = self.resolver.resolve_project_imports(project)

        # Verification: duplication causes resolution failure and warning
        self.assertEqual(len(result.resolved_imports), 0)
        self.assertEqual(len(result.unresolved_imports), 1)
        self.assertTrue(any("Duplicate export" in d for d in result.diagnostics))
        self.assertTrue(any("Ambiguous import" in d for d in result.diagnostics))

    def test_resolver_statelessness_and_repeated_executions(self) -> None:
        # Verify that executing the resolver multiple times does not leak state
        exp_helper = ExportDeclaration(exported_name="helper", local_symbol_id="sym-helper", location=self.loc_utils)
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[self.sym_helper],
            imports=[],
            exports=[exp_helper]
        )
        imp_helper = ImportDeclaration(
            imported_name="helper",
            module_specifier="./utils",
            location=self.loc_main
        )
        file_main = ProjectFile(
            path=Path("src/main.py"),
            symbols=[],
            imports=[imp_helper],
            exports=[]
        )

        project = {
            Path("src/utils.py"): file_utils,
            Path("src/main.py"): file_main
        }

        # Run 1
        res1 = self.resolver.resolve_project_imports(project)
        # Run 2
        res2 = self.resolver.resolve_project_imports(project)

        self.assertEqual(len(res1.resolved_imports), 1)
        self.assertEqual(len(res2.resolved_imports), 1)
        self.assertEqual(res1.resolved_imports[0].target_symbol.id, res2.resolved_imports[0].target_symbol.id)


if __name__ == "__main__":
    unittest.main()
