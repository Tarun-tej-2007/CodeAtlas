"""Call visitor module.

Provides the CallVisitor class for walking an ASTDocument, detecting function,
method, constructor, and static calls, tracking caller scope context, and resolving callees.
"""

from pathlib import Path
from app.parser.ast import ASTNode, ASTVisitor
from app.parser.symbols import Symbol, SymbolTable
from app.analyzer.resolution.models import ResolutionResult
from app.analyzer.calls.models import CallKind, CallReference


class CallVisitor(ASTVisitor):
    """Walks AST, tracks enclosing caller symbols, and extracts call invocation references."""

    def __init__(
        self,
        document_path: Path,
        symbol_table: SymbolTable,
        resolution_result: ResolutionResult | None = None,
    ) -> None:
        """Initializes CallVisitor with document path, symbol table, and resolution result.

        Args:
            document_path: Absolute path to the document.
            symbol_table: Extracted SymbolTable for the document.
            resolution_result: Optional ResolutionResult containing resolved references.
        """
        self.document_path = document_path
        self.symbol_table = symbol_table
        self.resolution_result = resolution_result
        self.calls: list[CallReference] = []
        self._current_caller_id: str | None = None
        self._call_counter = 0

        # Pre-index symbols by name and line
        self._symbols_by_name_line: dict[tuple[str, int], Symbol] = {
            (s.name, s.start_line): s for s in symbol_table.symbols
        }
        self._symbols_by_name: dict[str, list[Symbol]] = {}
        for s in symbol_table.symbols:
            self._symbols_by_name.setdefault(s.name, []).append(s)

        # Pre-index resolved references by (name, line, col)
        self._resolved_refs_map: dict[tuple[str, int, int], str] = {}
        if resolution_result:
            for ref in resolution_result.references:
                if ref.resolved and ref.resolved_symbol_id:
                    self._resolved_refs_map[(ref.name, ref.line, ref.column)] = ref.resolved_symbol_id

    def _generate_call_id(self, callee_name: str, line: int, col: int, kind: CallKind) -> str:
        self._call_counter += 1
        return f"call_{line}_{col}_{kind.value}_{callee_name}_{self._call_counter}"

    def visit(self, node: ASTNode) -> None:
        """Custom AST traversal tracking caller context and detecting call expressions."""
        node_type = node.type

        # Track Caller Context: Function or Method Declaration
        if node_type in ("function_declaration", "generator_function_declaration", "method_definition"):
            self._visit_enclosing_declaration(node)
            return

        # Detect Constructor Call: new User()
        if node_type == "new_expression":
            self._handle_new_expression(node)

        # Detect Function / Method / Static Method Call: foo(), obj.run(), Logger.create()
        elif node_type == "call_expression":
            self._handle_call_expression(node)

        for child in node.children:
            self.visit(child)

    def _visit_enclosing_declaration(self, node: ASTNode) -> None:
        """Tracks current caller symbol ID while visiting enclosing declaration bodies."""
        decl_name = self._get_identifier_text(node)
        caller_symbol: Symbol | None = None

        if decl_name:
            if (decl_name, node.start_line) in self._symbols_by_name_line:
                caller_symbol = self._symbols_by_name_line[(decl_name, node.start_line)]
            elif decl_name in self._symbols_by_name:
                caller_symbol = self._symbols_by_name[decl_name][0]

        previous_caller_id = self._current_caller_id
        if caller_symbol:
            self._current_caller_id = caller_symbol.id

        for child in node.children:
            self.visit(child)

        self._current_caller_id = previous_caller_id

    def _handle_new_expression(self, node: ASTNode) -> None:
        """Processes new_expression into a CallKind.CONSTRUCTOR reference."""
        callee_name, callee_node = self._extract_callee_info(node)
        if callee_name and callee_node:
            self._record_call(
                callee_name=callee_name,
                callee_node=callee_node,
                kind=CallKind.CONSTRUCTOR,
            )

    def _handle_call_expression(self, node: ASTNode) -> None:
        """Processes call_expression into FUNCTION, METHOD, or STATIC_METHOD reference."""
        if not node.children:
            return

        invoked = node.children[0]

        if invoked.type in ("identifier", "type_identifier"):
            callee_name = invoked.text
            self._record_call(
                callee_name=callee_name,
                callee_node=invoked,
                kind=CallKind.FUNCTION,
            )

        elif invoked.type == "member_expression":
            obj_name, prop_name, prop_node = self._extract_member_parts(invoked)
            if prop_name and prop_node:
                # Check if static method call (object name starts with uppercase)
                is_static = bool(obj_name and obj_name[0].isupper())
                kind = CallKind.STATIC_METHOD if is_static else CallKind.METHOD

                self._record_call(
                    callee_name=prop_name,
                    callee_node=prop_node,
                    kind=kind,
                )

    def _record_call(self, callee_name: str, callee_node: ASTNode, kind: CallKind) -> None:
        """Resolves callee and appends a CallReference to self.calls."""
        callee_symbol_id = self._resolve_callee_symbol_id(callee_name, callee_node)
        resolved = callee_symbol_id is not None

        call_id = self._generate_call_id(callee_name, callee_node.start_line, callee_node.start_column, kind)

        self.calls.append(
            CallReference(
                id=call_id,
                caller_symbol_id=self._current_caller_id,
                callee_name=callee_name,
                callee_symbol_id=callee_symbol_id,
                kind=kind,
                path=self.document_path,
                line=callee_node.start_line,
                column=callee_node.start_column,
                resolved=resolved,
            )
        )

    def _resolve_callee_symbol_id(self, callee_name: str, callee_node: ASTNode) -> str | None:
        """Resolves callee symbol ID via resolution_result map or symbol table lookup."""
        key = (callee_name, callee_node.start_line, callee_node.start_column)
        if key in self._resolved_refs_map:
            return self._resolved_refs_map[key]

        # Lookup by name in symbol_table
        candidates = self._symbols_by_name.get(callee_name, [])
        if candidates:
            return candidates[0].id

        return None

    def _extract_callee_info(self, node: ASTNode) -> tuple[str | None, ASTNode | None]:
        """Extracts callee identifier name and AST node from new_expression."""
        for child in node.children:
            if child.type in ("identifier", "type_identifier"):
                return child.text, child
            if child.type == "member_expression":
                _, prop_name, prop_node = self._extract_member_parts(child)
                return prop_name, prop_node
        return None, None

    def _extract_member_parts(self, member_node: ASTNode) -> tuple[str | None, str | None, ASTNode | None]:
        """Extracts object name, property name, and property AST node from member_expression."""
        obj_name: str | None = None
        prop_name: str | None = None
        prop_node: ASTNode | None = None

        if len(member_node.children) >= 3:
            obj_child = member_node.children[0]
            prop_child = member_node.children[2]
            obj_name = obj_child.text
            prop_name = prop_child.text
            prop_node = prop_child
        elif len(member_node.children) >= 2:
            obj_child = member_node.children[0]
            prop_child = member_node.children[1]
            obj_name = obj_child.text
            prop_name = prop_child.text
            prop_node = prop_child

        return obj_name, prop_name, prop_node

    def _get_identifier_text(self, node: ASTNode) -> str | None:
        for child in node.children:
            if child.type in ("identifier", "property_identifier", "type_identifier"):
                return child.text
        return None
