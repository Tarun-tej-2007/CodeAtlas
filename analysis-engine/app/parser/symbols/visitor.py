"""Symbol visitor module.

Provides the SymbolVisitor class responsible for traversing normalized ASTDocument
trees and extracting top-level and nested declaration symbols.
"""

from pathlib import Path
from app.parser.ast import ASTNode, ASTVisitor
from app.parser.language import Language
from app.parser.symbols.models import Symbol, SymbolKind


class SymbolVisitor(ASTVisitor):
    """Traverses an ASTDocument and extracts declaration symbols."""

    def __init__(self, document_path: Path, language: Language) -> None:
        """Initializes SymbolVisitor with document path and language context.

        Args:
            document_path: Absolute path to the source document.
            language: Canonical Language enum.
        """
        self.document_path = document_path
        self.language = language
        self.symbols: list[Symbol] = []
        self._current_parent_class_id: str | None = None
        self._symbol_counter = 0

    def _generate_symbol_id(self, name: str, kind: SymbolKind, start_line: int) -> str:
        """Generates a deterministic symbol ID string."""
        self._symbol_counter += 1
        return f"sym_{self.language.value}_{start_line}_{kind.value}_{name}_{self._symbol_counter}"

    def _get_identifier_name(
        self,
        node: ASTNode,
        target_types: tuple[str, ...] = ("identifier", "property_identifier", "type_identifier"),
    ) -> str | None:
        """Helper to find the text of the first matching child identifier node."""
        for child in node.children:
            if child.type in target_types:
                return child.text
        return None

    def visit(self, node: ASTNode) -> None:
        """Performs custom depth-first AST traversal with class context tracking."""
        node_type = node.type

        if node_type in ("class_declaration", "class"):
            self._handle_class_declaration(node)
            return

        if node_type in ("function_declaration", "generator_function_declaration"):
            self._handle_function_declaration(node)

        elif node_type in ("method_definition", "method_signature", "abstract_method_signature"):
            self._handle_method_definition(node)

        elif node_type in ("lexical_declaration", "variable_declaration"):
            self._handle_variable_declaration(node)

        elif node_type == "interface_declaration":
            self._handle_interface_declaration(node)

        elif node_type == "type_alias_declaration":
            self._handle_type_alias_declaration(node)

        elif node_type == "enum_declaration":
            self._handle_enum_declaration(node)

        elif node_type in ("module", "internal_module"):
            self._handle_namespace_declaration(node)

        # Traverse child nodes for further declarations
        for child in node.children:
            self.visit(child)

    def _handle_class_declaration(self, node: ASTNode) -> None:
        """Extracts class declaration symbol and manages parent class scope for methods."""
        name = self._get_identifier_name(node)
        class_symbol: Symbol | None = None

        if name:
            symbol_id = self._generate_symbol_id(name, SymbolKind.CLASS, node.start_line)
            class_symbol = Symbol(
                id=symbol_id,
                name=name,
                kind=SymbolKind.CLASS,
                language=self.language,
                path=self.document_path,
                parent_symbol_id=None,
                start_line=node.start_line,
                end_line=node.end_line,
            )
            self.symbols.append(class_symbol)

        previous_parent_id = self._current_parent_class_id
        if class_symbol:
            self._current_parent_class_id = class_symbol.id

        for child in node.children:
            self.visit(child)

        self._current_parent_class_id = previous_parent_id

    def _handle_function_declaration(self, node: ASTNode) -> None:
        """Extracts function declaration symbol."""
        name = self._get_identifier_name(node)
        if name:
            symbol_id = self._generate_symbol_id(name, SymbolKind.FUNCTION, node.start_line)
            self.symbols.append(
                Symbol(
                    id=symbol_id,
                    name=name,
                    kind=SymbolKind.FUNCTION,
                    language=self.language,
                    path=self.document_path,
                    parent_symbol_id=None,
                    start_line=node.start_line,
                    end_line=node.end_line,
                )
            )

    def _handle_method_definition(self, node: ASTNode) -> None:
        """Extracts method definition symbol with class parent ID attachment."""
        name = self._get_identifier_name(node)
        if name:
            symbol_id = self._generate_symbol_id(name, SymbolKind.METHOD, node.start_line)
            self.symbols.append(
                Symbol(
                    id=symbol_id,
                    name=name,
                    kind=SymbolKind.METHOD,
                    language=self.language,
                    path=self.document_path,
                    parent_symbol_id=self._current_parent_class_id,
                    start_line=node.start_line,
                    end_line=node.end_line,
                )
            )

    def _handle_variable_declaration(self, node: ASTNode) -> None:
        """Extracts variable declaration symbols from lexical/variable declarators."""
        for child in node.children:
            if child.type == "variable_declarator":
                var_name = self._get_identifier_name(child)
                if not var_name and child.children:
                    # Fallback to first identifier child
                    for sub in child.children:
                        if sub.type == "identifier":
                            var_name = sub.text
                            break

                if var_name:
                    symbol_id = self._generate_symbol_id(
                        var_name, SymbolKind.VARIABLE, child.start_line
                    )
                    self.symbols.append(
                        Symbol(
                            id=symbol_id,
                            name=var_name,
                            kind=SymbolKind.VARIABLE,
                            language=self.language,
                            path=self.document_path,
                            parent_symbol_id=None,
                            start_line=child.start_line,
                            end_line=child.end_line,
                        )
                    )

    def _handle_interface_declaration(self, node: ASTNode) -> None:
        """Extracts TypeScript interface declaration symbol."""
        name = self._get_identifier_name(node)
        if name:
            symbol_id = self._generate_symbol_id(name, SymbolKind.INTERFACE, node.start_line)
            self.symbols.append(
                Symbol(
                    id=symbol_id,
                    name=name,
                    kind=SymbolKind.INTERFACE,
                    language=self.language,
                    path=self.document_path,
                    parent_symbol_id=None,
                    start_line=node.start_line,
                    end_line=node.end_line,
                )
            )

    def _handle_type_alias_declaration(self, node: ASTNode) -> None:
        """Extracts TypeScript type alias declaration symbol."""
        name = self._get_identifier_name(node)
        if name:
            symbol_id = self._generate_symbol_id(name, SymbolKind.TYPE_ALIAS, node.start_line)
            self.symbols.append(
                Symbol(
                    id=symbol_id,
                    name=name,
                    kind=SymbolKind.TYPE_ALIAS,
                    language=self.language,
                    path=self.document_path,
                    parent_symbol_id=None,
                    start_line=node.start_line,
                    end_line=node.end_line,
                )
            )

    def _handle_enum_declaration(self, node: ASTNode) -> None:
        """Extracts TypeScript enum declaration symbol."""
        name = self._get_identifier_name(node)
        if name:
            symbol_id = self._generate_symbol_id(name, SymbolKind.ENUM, node.start_line)
            self.symbols.append(
                Symbol(
                    id=symbol_id,
                    name=name,
                    kind=SymbolKind.ENUM,
                    language=self.language,
                    path=self.document_path,
                    parent_symbol_id=None,
                    start_line=node.start_line,
                    end_line=node.end_line,
                )
            )

    def _handle_namespace_declaration(self, node: ASTNode) -> None:
        """Extracts TypeScript module/namespace declaration symbol."""
        name = self._get_identifier_name(node, ("identifier", "string"))
        if name:
            # Clean string quotes if name was a string literal
            name = name.strip('"\'')
            symbol_id = self._generate_symbol_id(name, SymbolKind.NAMESPACE, node.start_line)
            self.symbols.append(
                Symbol(
                    id=symbol_id,
                    name=name,
                    kind=SymbolKind.NAMESPACE,
                    language=self.language,
                    path=self.document_path,
                    parent_symbol_id=None,
                    start_line=node.start_line,
                    end_line=node.end_line,
                )
            )
