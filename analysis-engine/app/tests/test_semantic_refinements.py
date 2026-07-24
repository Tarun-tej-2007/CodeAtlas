"""Hardening, integration, and refinements tests for the semantic subsystem."""

import unittest
from pathlib import Path
from pydantic import ValidationError

from app.scanner.models import Language
from app.parser.models import ParseResult
from app.semantic.enums import ScopeKind, SymbolKind, ReferenceKind, VisibilityKind
from app.semantic.exceptions import SemanticModelError
from app.semantic import (
    Location,
    SemanticSymbol,
    SemanticReference,
    ScopeNode,
    ScopeManager,
    SymbolTable,
    ReferenceResolver,
    SemanticAnalysisContext,
    SemanticAnalysisPlugin,
    SemanticPipeline,
)


class DeeplyNestedShadowingPlugin(SemanticAnalysisPlugin):
    """Simulates a complex program with nested lexical scopes, shadowing, and references."""

    def build_scopes_and_symbols(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        loc = Location(start_line=1, start_column=0, end_line=100, end_column=0)

        # 1. Global "x"
        sym_global = SemanticSymbol(
            id="sym-global",
            name="x",
            qualified_name="global.x",
            kind=SymbolKind.VARIABLE,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=loc,
            scope_id="global",
        )
        context.symbol_table.register_symbol(sym_global)
        context.scope_manager.register_symbol("sym-global")

        # 2. Outer function scope "outer"
        outer_scope = context.scope_manager.create_scope(id="scope-outer", kind=ScopeKind.FUNCTION, location=loc)
        sym_outer = SemanticSymbol(
            id="sym-outer",
            name="outer",
            qualified_name="global.outer",
            kind=SymbolKind.FUNCTION,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=loc,
            scope_id="global",
        )
        context.symbol_table.register_symbol(sym_outer)
        context.scope_manager.register_symbol("sym-outer")

        # Enter outer function
        context.scope_manager.enter_scope(outer_scope)

        # 3. Inner nested class scope "InnerClass" shadowing outer names or defining nested "x"
        inner_class_scope = context.scope_manager.create_scope(
            id="scope-inner-class", kind=ScopeKind.CLASS, location=loc
        )
        sym_inner_class = SemanticSymbol(
            id="sym-inner-class",
            name="InnerClass",
            qualified_name="global.outer.InnerClass",
            kind=SymbolKind.CLASS,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=loc,
            scope_id="scope-outer",
            parent_symbol_id="sym-outer",
        )
        context.symbol_table.register_symbol(sym_inner_class)
        context.scope_manager.register_symbol("sym-inner-class")

        # Enter InnerClass
        context.scope_manager.enter_scope(inner_class_scope)

        # 4. Shadowed local "x"
        sym_shadowed = SemanticSymbol(
            id="sym-shadowed",
            name="x",  # Shadowing global "x"
            qualified_name="global.outer.InnerClass.x",
            kind=SymbolKind.VARIABLE,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=loc,
            scope_id="scope-inner-class",
            parent_symbol_id="sym-inner-class",
        )
        context.symbol_table.register_symbol(sym_shadowed)
        context.scope_manager.register_symbol("sym-shadowed")

        # Exit class & function
        context.scope_manager.exit_scope()  # Exit class
        context.scope_manager.exit_scope()  # Exit outer

    def resolve_references(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        loc = Location(start_line=15, start_column=0, end_line=15, end_column=10)

        # 1. Resolve from outer function (ascends to global to find "x")
        context.scope_manager.enter_scope(context.scope_manager.get_scope_by_id("scope-outer"))
        context.reference_resolver.resolve_reference(name="x", location=loc)
        context.scope_manager.exit_scope()

        # 2. Resolve from inner class (resolves to shadowed local "x" instead of global)
        context.scope_manager.enter_scope(context.scope_manager.get_scope_by_id("scope-outer"))
        context.scope_manager.enter_scope(context.scope_manager.get_scope_by_id("scope-inner-class"))
        context.reference_resolver.resolve_reference(name="x", location=loc)
        context.scope_manager.exit_scope()
        context.scope_manager.exit_scope()

        # 3. Resolve unresolved identifier
        context.reference_resolver.resolve_reference(name="unresolved_var", location=loc)

    def extract_type_metadata(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        pass


class TestSemanticRefinements(unittest.TestCase):
    """Tests the full integrated semantic execution passes, nested scopes shadow correctness, and DTO immutability."""

    def setUp(self) -> None:
        self.parse_result = ParseResult(parsed_count=1, failed_count=0, files=[])

    def test_complete_pipeline_shadowing_and_diagnostics_integration(self) -> None:
        plugin = DeeplyNestedShadowingPlugin()
        pipeline = SemanticPipeline(plugin=plugin)

        result = pipeline.execute(self.parse_result)

        # 1. Aggregation checks
        self.assertEqual(len(result.symbols), 4)  # global x, outer, InnerClass, local x
        self.assertEqual(len(result.references), 2)  # global resolution and local shadowed resolution
        self.assertEqual(len(result.scopes), 3)  # global, outer, InnerClass
        self.assertEqual(len(result.diagnostics), 1)  # unresolved_var diagnostic

        # 2. Shadowing correctness verification
        # Reference 1 (outer scope) resolves to global x
        ref_outer = result.references[0]
        self.assertEqual(ref_outer.symbol_id, "sym-global")

        # Reference 2 (inner class scope) resolves to local shadowed x
        ref_inner = result.references[1]
        self.assertEqual(ref_inner.symbol_id, "sym-shadowed")

        # 3. Immutability checks on the generated result DTO (frozen BaseModel checks)
        with self.assertRaises((TypeError, ValidationError)):
            result.symbols[0].name = "modified"  # type: ignore

    def test_empty_analysis_inputs(self) -> None:
        class EmptyPlugin(SemanticAnalysisPlugin):
            def build_scopes_and_symbols(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
                pass

            def resolve_references(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
                pass

            def extract_type_metadata(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
                pass

        pipeline = SemanticPipeline(plugin=EmptyPlugin())
        result = pipeline.execute(self.parse_result)

        # Basic defaults
        self.assertEqual(len(result.symbols), 0)
        self.assertEqual(len(result.references), 0)
        self.assertEqual(len(result.scopes), 1)  # only global root scope node
        self.assertEqual(len(result.diagnostics), 0)


if __name__ == "__main__":
    unittest.main()
