"""Module visitor module.

Provides the ModuleVisitor class responsible for traversing normalized ASTDocument
trees and extracting import and export declarations.
"""

from pathlib import Path
from app.parser.ast import ASTNode, ASTVisitor
from app.parser.modules.models import (
    ExportKind,
    ExportSymbol,
    ImportKind,
    ImportSymbol,
)


class ModuleVisitor(ASTVisitor):
    """Traverses an ASTDocument and extracts module boundary imports and exports."""

    def __init__(self, document_path: Path) -> None:
        """Initializes ModuleVisitor with document path context.

        Args:
            document_path: Absolute path to the source document.
        """
        self.document_path = document_path
        self.imports: list[ImportSymbol] = []
        self.exports: list[ExportSymbol] = []
        self._import_counter = 0
        self._export_counter = 0

    def _generate_import_id(self, module: str, name: str, kind: ImportKind, line: int) -> str:
        self._import_counter += 1
        clean_mod = module.replace("/", "_").replace(".", "_").replace("-", "_").replace("@", "_")
        return f"imp_{line}_{kind.value}_{clean_mod}_{name}_{self._import_counter}"

    def _generate_export_id(self, name: str, kind: ExportKind, line: int) -> str:
        self._export_counter += 1
        return f"exp_{line}_{kind.value}_{name}_{self._export_counter}"

    def _clean_string_literal(self, text: str) -> str:
        """Removes single or double quotes from string literal text."""
        return text.strip("'\"`")

    def visit(self, node: ASTNode) -> None:
        """Inspects nodes for import and export statements during traversal."""
        if node.type == "import_statement":
            self._handle_import_statement(node)

        elif node.type == "export_statement":
            self._handle_export_statement(node)

        for child in node.children:
            self.visit(child)

    def _handle_import_statement(self, node: ASTNode) -> None:
        """Parses import_statement node into one or more ImportSymbol objects."""
        # Find module string specifier
        module_name = ""
        import_clause: ASTNode | None = None

        for child in node.children:
            if child.type in ("string", "string_fragment"):
                module_name = self._clean_string_literal(child.text)
            elif child.type == "import_clause":
                import_clause = child

        if not module_name:
            return

        # Side-effect import (e.g. import './styles.css';)
        if not import_clause:
            symbol_id = self._generate_import_id(module_name, "*", ImportKind.SIDE_EFFECT, node.start_line)
            self.imports.append(
                ImportSymbol(
                    id=symbol_id,
                    module=module_name,
                    name="*",
                    alias=None,
                    kind=ImportKind.SIDE_EFFECT,
                    path=self.document_path,
                    start_line=node.start_line,
                )
            )
            return

        # Process children of import_clause
        for child in import_clause.children:
            # Default import (e.g. import React from 'react';)
            if child.type == "identifier":
                default_name = child.text
                symbol_id = self._generate_import_id(module_name, default_name, ImportKind.DEFAULT, node.start_line)
                self.imports.append(
                    ImportSymbol(
                        id=symbol_id,
                        module=module_name,
                        name=default_name,
                        alias=None,
                        kind=ImportKind.DEFAULT,
                        path=self.document_path,
                        start_line=node.start_line,
                    )
                )

            # Namespace import (e.g. import * as utils from './utils';)
            elif child.type == "namespace_import":
                ns_alias = None
                for sub in child.children:
                    if sub.type == "identifier":
                        ns_alias = sub.text
                if ns_alias:
                    symbol_id = self._generate_import_id(module_name, "*", ImportKind.NAMESPACE, node.start_line)
                    self.imports.append(
                        ImportSymbol(
                            id=symbol_id,
                            module=module_name,
                            name="*",
                            alias=ns_alias,
                            kind=ImportKind.NAMESPACE,
                            path=self.document_path,
                            start_line=node.start_line,
                        )
                    )

            # Named imports (e.g. import { a, b as c } from 'foo';)
            elif child.type == "named_imports":
                for spec in child.children:
                    if spec.type == "import_specifier":
                        identifiers = [sub.text for sub in spec.children if sub.type in ("identifier", "type_identifier")]
                        if len(identifiers) == 1:
                            imp_name = identifiers[0]
                            symbol_id = self._generate_import_id(module_name, imp_name, ImportKind.NAMED, node.start_line)
                            self.imports.append(
                                ImportSymbol(
                                    id=symbol_id,
                                    module=module_name,
                                    name=imp_name,
                                    alias=None,
                                    kind=ImportKind.NAMED,
                                    path=self.document_path,
                                    start_line=node.start_line,
                                )
                            )
                        elif len(identifiers) >= 2:
                            imp_name = identifiers[0]
                            imp_alias = identifiers[1]
                            symbol_id = self._generate_import_id(module_name, imp_name, ImportKind.NAMED, node.start_line)
                            self.imports.append(
                                ImportSymbol(
                                    id=symbol_id,
                                    module=module_name,
                                    name=imp_name,
                                    alias=imp_alias,
                                    kind=ImportKind.NAMED,
                                    path=self.document_path,
                                    start_line=node.start_line,
                                )
                            )

    def _handle_export_statement(self, node: ASTNode) -> None:
        """Parses export_statement node into one or more ExportSymbol objects."""
        is_default = any(child.type == "default" for child in node.children)
        is_export_all = any(child.type == "*" for child in node.children)

        # Export * (e.g. export * from './components';)
        if is_export_all:
            target_module = next((self._clean_string_literal(child.text) for child in node.children if child.type in ("string", "string_fragment")), None)
            symbol_id = self._generate_export_id("*", ExportKind.ALL, node.start_line)
            self.exports.append(
                ExportSymbol(
                    id=symbol_id,
                    name="*",
                    alias=target_module,
                    kind=ExportKind.ALL,
                    path=self.document_path,
                    start_line=node.start_line,
                )
            )
            return


        # Export Default (e.g. export default App;)
        if is_default:
            export_name = "default"
            for child in node.children:
                if child.type in ("identifier", "type_identifier"):
                    export_name = child.text
                    break

            symbol_id = self._generate_export_id("default", ExportKind.DEFAULT, node.start_line)
            self.exports.append(
                ExportSymbol(
                    id=symbol_id,
                    name="default",
                    alias=export_name if export_name != "default" else None,
                    kind=ExportKind.DEFAULT,
                    path=self.document_path,
                    start_line=node.start_line,
                )
            )
            return

        # Export Clause (e.g. export { a, b as c };)
        export_clause = next((child for child in node.children if child.type == "export_clause"), None)
        if export_clause:
            for spec in export_clause.children:
                if spec.type == "export_specifier":
                    identifiers = [sub.text for sub in spec.children if sub.type in ("identifier", "type_identifier", "property_identifier")]
                    if len(identifiers) == 1:
                        exp_name = identifiers[0]
                        symbol_id = self._generate_export_id(exp_name, ExportKind.NAMED, node.start_line)
                        self.exports.append(
                            ExportSymbol(
                                id=symbol_id,
                                name=exp_name,
                                alias=None,
                                kind=ExportKind.NAMED,
                                path=self.document_path,
                                start_line=node.start_line,
                            )
                        )
                    elif len(identifiers) >= 2:
                        exp_name = identifiers[0]
                        exp_alias = identifiers[1]
                        symbol_id = self._generate_export_id(exp_name, ExportKind.NAMED, node.start_line)
                        self.exports.append(
                            ExportSymbol(
                                id=symbol_id,
                                name=exp_name,
                                alias=exp_alias,
                                kind=ExportKind.NAMED,
                                path=self.document_path,
                                start_line=node.start_line,
                            )
                        )
            return

        # Export Declaration (e.g. export const x = 1; export function foo() {})
        for child in node.children:
            if child.type in ("function_declaration", "generator_function_declaration", "class_declaration", "interface_declaration", "type_alias_declaration", "enum_declaration"):
                exp_name = next((sub.text for sub in child.children if sub.type in ("identifier", "type_identifier")), None)
                if exp_name:
                    symbol_id = self._generate_export_id(exp_name, ExportKind.NAMED, node.start_line)
                    self.exports.append(
                        ExportSymbol(
                            id=symbol_id,
                            name=exp_name,
                            alias=None,
                            kind=ExportKind.NAMED,
                            path=self.document_path,
                            start_line=node.start_line,
                        )
                    )
            elif child.type in ("lexical_declaration", "variable_declaration"):
                for var_decl in child.children:
                    if var_decl.type == "variable_declarator":
                        exp_name = next((sub.text for sub in var_decl.children if sub.type == "identifier"), None)
                        if exp_name:
                            symbol_id = self._generate_export_id(exp_name, ExportKind.NAMED, node.start_line)
                            self.exports.append(
                                ExportSymbol(
                                    id=symbol_id,
                                    name=exp_name,
                                    alias=None,
                                    kind=ExportKind.NAMED,
                                    path=self.document_path,
                                    start_line=node.start_line,
                                )
                            )
