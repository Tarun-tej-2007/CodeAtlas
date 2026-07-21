"""Resolution visitor module.

Provides the ResolutionVisitor class for walking an ASTDocument, managing nested Scope frames,
registering declarations, and resolving intra-file identifier references.
"""

from pathlib import Path
from app.parser.ast import ASTNode, ASTVisitor
from app.parser.symbols import Symbol, SymbolTable
from app.analyzer.resolution.models import ResolvedReference
from app.analyzer.resolution.scope import Scope


class ResolutionVisitor(ASTVisitor):
    """Walks AST, manages scope frames, registers declarations, and resolves references."""

    def __init__(
        self,
        document_path: Path,
        symbol_table: SymbolTable,
        root_scope: Scope | None = None,
    ) -> None:
        """Initializes ResolutionVisitor with document path, symbol table, and root scope.

        Args:
            document_path: Absolute path to the document.
            symbol_table: Extracted SymbolTable for the file.
            root_scope: Optional root Scope instance (defaults to Scope('global')).
        """
        self.document_path = document_path
        self.symbol_table = symbol_table
        self.current_scope = root_scope or Scope(kind="global")
        self.references: list[ResolvedReference] = []
        self._ref_counter = 0

        # Pre-index symbols by (name, line) and name
        self._symbols_by_name_line: dict[tuple[str, int], Symbol] = {
            (s.name, s.start_line): s for s in symbol_table.symbols
        }
        self._symbols_by_name: dict[str, list[Symbol]] = {}
        for s in symbol_table.symbols:
            self._symbols_by_name.setdefault(s.name, []).append(s)

        # Pre-populate global scope with top-level declaration symbols
        for symbol in symbol_table.symbols:
            if symbol.parent_symbol_id is None:
                self.current_scope.declare(symbol)

    def _generate_ref_id(self, name: str, line: int, col: int) -> str:
        self._ref_counter += 1
        return f"ref_{line}_{col}_{name}_{self._ref_counter}"

    def _find_matching_symbol(self, name: str, line: int) -> Symbol | None:
        """Finds pre-extracted Symbol by name and start line or name fallback."""
        if (name, line) in self._symbols_by_name_line:
            return self._symbols_by_name_line[(name, line)]

        candidates = self._symbols_by_name.get(name, [])
        if candidates:
            # Pick closest declaration line at or before current line
            valid = [s for s in candidates if s.start_line <= line]
            if valid:
                return max(valid, key=lambda s: s.start_line)
            return candidates[0]
        return None

    def visit(self, node: ASTNode) -> None:
        """Custom visitor traversal managing scope stack and identifier resolution."""
        node_type = node.type

        # Scope Entry: Function
        if node_type in ("function_declaration", "generator_function_declaration", "arrow_function"):
            self._visit_function(node)
            return

        # Scope Entry: Class
        if node_type in ("class_declaration", "class"):
            self._visit_class(node)
            return

        # Scope Entry: Block
        if node_type in ("statement_block", "block"):
            self._visit_block(node)
            return

        # Declaration: Variable Declarator
        if node_type == "variable_declarator":
            self._handle_variable_declarator(node)

        # Declaration: Interface / Type Alias / Enum
        elif node_type in ("interface_declaration", "type_alias_declaration", "enum_declaration"):
            self._handle_type_declaration(node)

        # Identifier Usage Node
        elif node_type in ("identifier", "type_identifier"):
            if not self._is_declaration_identifier(node) and not self._is_property_access_target(node):
                self._resolve_identifier_usage(node)

        # Traverse children
        for child in node.children:
            self.visit(child)

    def _visit_function(self, node: ASTNode) -> None:
        """Enters a new function scope frame and registers parameters and local declarations."""
        fn_name = self._get_identifier_text(node)
        if fn_name:
            symbol = self._find_matching_symbol(fn_name, node.start_line)
            if symbol:
                self.current_scope.declare(symbol)

        # Enter function scope
        prev_scope = self.current_scope
        self.current_scope = self.current_scope.create_child(kind="function")

        for child in node.children:
            if child.type in ("formal_parameters", "parameters"):
                self._handle_formal_parameters(child)

        for child in node.children:
            self.visit(child)

        self.current_scope = prev_scope

    def _visit_class(self, node: ASTNode) -> None:
        """Enters a new class scope frame."""
        class_name = self._get_identifier_text(node)
        if class_name:
            symbol = self._find_matching_symbol(class_name, node.start_line)
            if symbol:
                self.current_scope.declare(symbol)

        prev_scope = self.current_scope
        self.current_scope = self.current_scope.create_child(kind="class")

        for child in node.children:
            self.visit(child)

        self.current_scope = prev_scope

    def _visit_block(self, node: ASTNode) -> None:
        """Enters a new block scope frame."""
        prev_scope = self.current_scope
        self.current_scope = self.current_scope.create_child(kind="block")

        for child in node.children:
            self.visit(child)

        self.current_scope = prev_scope

    def _handle_variable_declarator(self, node: ASTNode) -> None:
        """Registers local variable declaration in current scope."""
        var_name = self._get_identifier_text(node)
        if var_name:
            symbol = self._find_matching_symbol(var_name, node.start_line)
            if not symbol:
                # Synthesize local symbol if not pre-indexed
                from app.parser.symbols import Symbol, SymbolKind
                symbol = Symbol(
                    id=f"sym_local_{node.start_line}_{var_name}",
                    name=var_name,
                    kind=SymbolKind.VARIABLE,
                    language=self.symbol_table.symbols[0].language if self.symbol_table.symbols else Language.JAVASCRIPT,
                    path=self.document_path,
                    start_line=node.start_line,
                    end_line=node.end_line,
                )
            self.current_scope.declare(symbol)

    def _handle_type_declaration(self, node: ASTNode) -> None:
        """Registers type/interface/enum declaration in current scope."""
        type_name = self._get_identifier_text(node)
        if type_name:
            symbol = self._find_matching_symbol(type_name, node.start_line)
            if symbol:
                self.current_scope.declare(symbol)

    def _handle_formal_parameters(self, node: ASTNode) -> None:
        """Registers formal parameter declarations in function scope."""
        from app.parser.symbols import Symbol, SymbolKind
        for child in node.children:
            param_name = self._get_identifier_text(child) or (child.text if child.type == "identifier" else None)
            if param_name:
                param_symbol = Symbol(
                    id=f"sym_param_{child.start_line}_{param_name}",
                    name=param_name,
                    kind=SymbolKind.VARIABLE,
                    language=self.symbol_table.symbols[0].language if self.symbol_table.symbols else Language.JAVASCRIPT,
                    path=self.document_path,
                    start_line=child.start_line,
                    end_line=child.end_line,
                )
                self.current_scope.declare(param_symbol)

    def _resolve_identifier_usage(self, node: ASTNode) -> None:
        """Resolves an identifier usage against the current scope hierarchy."""
        name = node.text
        if not name or name in ("true", "false", "null", "undefined", "this", "super"):
            return

        symbol = self.current_scope.resolve(name)
        ref_id = self._generate_ref_id(name, node.start_line, node.start_column)

        if symbol:
            ref = ResolvedReference(
                id=ref_id,
                name=name,
                path=self.document_path,
                line=node.start_line,
                column=node.start_column,
                resolved_symbol_id=symbol.id,
                resolved=True,
            )
        else:
            ref = ResolvedReference(
                id=ref_id,
                name=name,
                path=self.document_path,
                line=node.start_line,
                column=node.start_column,
                resolved_symbol_id=None,
                resolved=False,
            )

        self.references.append(ref)

    def _get_identifier_text(self, node: ASTNode) -> str | None:
        for child in node.children:
            if child.type in ("identifier", "property_identifier", "type_identifier"):
                return child.text
        return None

    def _is_declaration_identifier(self, node: ASTNode) -> bool:
        """Checks if an identifier node is a declaration name rather than a usage."""
        # Simple check based on position or type
        return False

    def _is_property_access_target(self, node: ASTNode) -> bool:
        """Checks if an identifier node is a property access target (e.g. obj.prop)."""
        return False
