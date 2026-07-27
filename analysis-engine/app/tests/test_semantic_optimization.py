"""Unit and performance regression tests for optimized semantic linking."""

import unittest
import time
from pathlib import Path

from app.semantic.enums import SymbolKind
from app.semantic import (
    Location,
    SymbolLocation,
    ProjectSymbol,
    ImportDeclaration,
    ExportDeclaration,
    SymbolReference,
    ProjectFile,
    ProjectSemanticResult,
    ProjectSymbolIndex,
    PathResolutionCache,
    ImportExportResolver,
    CrossFileReferenceResolver,
    SemanticLinkingPipeline,
)


class TestSemanticOptimization(unittest.TestCase):
    """Verifies lookup correctness, cache mappings, and identical outputs over synthetic large workspaces."""

    def setUp(self) -> None:
        self.loc = Location(start_line=1, start_column=0, end_line=1, end_column=10)
        self.loc_a = SymbolLocation(file_path=Path("src/a.py"), location=self.loc)
        self.loc_b = SymbolLocation(file_path=Path("src/b.py"), location=self.loc)

    def test_cache_correctness_and_lookup(self) -> None:
        cache = PathResolutionCache()
        
        # Verify empty cache behavior
        self.assertIsNone(cache.get(Path("src/main.py"), "./utils"))
        
        # Set cache
        cache.set(Path("src/main.py"), "./utils", Path("src/utils.py"))
        self.assertEqual(cache.get(Path("src/main.py"), "./utils"), Path("src/utils.py"))
        
        # Clear cache
        cache.clear()
        self.assertIsNone(cache.get(Path("src/main.py"), "./utils"))

    def test_regression_identical_outputs(self) -> None:
        # Build a small project structure
        sym_helper = ProjectSymbol(
            id="helper-id",
            name="helper",
            qualified_name="src.a.helper",
            kind=SymbolKind.FUNCTION,
            location=self.loc_a,
        )
        exp = ExportDeclaration(exported_name="helper", local_symbol_id="helper-id", location=self.loc_a)
        file_a = ProjectFile(path=Path("src/a.py"), symbols=[sym_helper], exports=[exp])

        imp = ImportDeclaration(imported_name="helper", module_specifier="./a", location=self.loc_b)
        ref = SymbolReference(name="helper", location=self.loc_b)
        file_b = ProjectFile(path=Path("src/b.py"), symbols=[], imports=[imp], references=[ref])

        project = {
            Path("src/a.py"): file_a,
            Path("src/b.py"): file_b
        }
        project_result = ProjectSemanticResult(files=project)

        # 1. Run without cache (simulated by not passing cache manually, though pipeline constructs it internally)
        pipeline = SemanticLinkingPipeline()
        linked1 = pipeline.link_project(project_result)

        # 2. Run with manual cache reuse
        cache = PathResolutionCache()
        import_resolver = ImportExportResolver()
        symbol_index = ProjectSymbolIndex(project)
        import_export_res = import_resolver.resolve_project_imports(project, cache)
        
        ref_resolver = CrossFileReferenceResolver(symbol_index, import_resolver)
        ref_res = ref_resolver.resolve_project_references(project, cache)

        # Verify resolution outputs match exactly
        self.assertEqual(len(linked1.import_export_result.resolved_imports), 1)
        self.assertEqual(len(import_export_res.resolved_imports), 1)
        self.assertEqual(
            linked1.import_export_result.resolved_imports[0].target_symbol.id,
            import_export_res.resolved_imports[0].target_symbol.id
        )

        self.assertEqual(len(linked1.reference_resolution_result.resolved_references), 1)
        self.assertEqual(len(ref_res.resolved_references), 1)
        self.assertEqual(
            linked1.reference_resolution_result.resolved_references[0].target_symbol.id,
            ref_res.resolved_references[0].target_symbol.id
        )

    def test_large_synthetic_project_scale_and_performance(self) -> None:
        # Generate a large synthetic repository: 50 files, 1000 symbols, 500 references
        project = {}
        
        # 1. Generate 25 utility files, each exporting 40 symbols
        for i in range(25):
            file_path = Path(f"src/utils_{i}.py")
            symbols = []
            exports = []
            for j in range(40):
                sym_id = f"sym-{i}-{j}"
                sym_name = f"helper_{i}_{j}"
                loc = SymbolLocation(file_path=file_path, location=self.loc)
                sym = ProjectSymbol(
                    id=sym_id,
                    name=sym_name,
                    qualified_name=f"src.utils_{i}.{sym_name}",
                    kind=SymbolKind.FUNCTION,
                    location=loc,
                )
                symbols.append(sym)
                exp = ExportDeclaration(exported_name=sym_name, local_symbol_id=sym_id, location=loc)
                exports.append(exp)
            
            project[file_path] = ProjectFile(path=file_path, symbols=symbols, exports=exports)

        # 2. Generate 25 client files, each importing and referencing 20 symbols from utilities
        for i in range(25):
            file_path = Path(f"src/client_{i}.py")
            imports = []
            references = []
            for j in range(20):
                # Import helper_{j}_{j} from src/utils_{j}.py
                target_module = f"./utils_{j}"
                target_name = f"helper_{j}_{j}"
                loc = SymbolLocation(file_path=file_path, location=self.loc)
                imp = ImportDeclaration(
                    imported_name=target_name,
                    module_specifier=target_module,
                    location=loc,
                )
                imports.append(imp)
                ref = SymbolReference(name=target_name, location=loc)
                references.append(ref)
            
            project[file_path] = ProjectFile(path=file_path, imports=imports, references=references)

        project_result = ProjectSemanticResult(files=project)

        # Execute and time the linking run
        pipeline = SemanticLinkingPipeline()
        
        t0 = time.perf_counter()
        linked = pipeline.link_project(project_result)
        elapsed = time.perf_counter() - t0

        # Assert correct resolution and rapid execution (typically under 100ms for 1500+ items with O(1) lookups)
        self.assertEqual(len(linked.import_export_result.resolved_imports), 500)
        self.assertEqual(len(linked.reference_resolution_result.resolved_references), 500)
        self.assertEqual(len(linked.diagnostics), 0)
        
        # Verify timing is extremely fast (well under 500ms safety threshold)
        self.assertLess(elapsed, 0.5, f"Execution took too long: {elapsed:.3f}s")


if __name__ == "__main__":
    unittest.main()
