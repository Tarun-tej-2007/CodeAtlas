"""Normalized AST builder module.

Provides the ASTBuilder class responsible for converting native Tree-sitter AST trees
into CodeAtlas-neutral, normalized ASTNode and ASTDocument domain models.
"""

from typing import Any
from app.parser.ast.exceptions import ASTBuilderError
from app.parser.ast.models import ASTDocument, ASTNode
from app.parser.models import ParsedFile


class ASTBuilder:
    """Builds normalized ASTNode and ASTDocument hierarchies from ParsedFile models."""

    def __init__(self) -> None:
        """Initializes the ASTBuilder."""
        pass

    def build_document(self, parsed_file: ParsedFile) -> ASTDocument:
        """Builds a normalized ASTDocument from a ParsedFile domain model.

        Args:
            parsed_file: ParsedFile instance containing path, language, and Tree-sitter tree.

        Returns:
            An immutable ASTDocument containing the normalized AST root node.

        Raises:
            ASTBuilderError: If building the AST hierarchy fails.
        """
        try:
            if not parsed_file.tree or not hasattr(parsed_file.tree, "root_node"):
                raise ASTBuilderError(
                    f"Invalid or missing Tree-sitter tree for file '{parsed_file.path}'"
                )

            source_bytes = parsed_file.source_code.encode("utf-8")
            root_node = self.build_node(
                ts_node=parsed_file.tree.root_node,
                source_bytes=source_bytes,
                node_index=0,
            )

            return ASTDocument(
                path=parsed_file.path,
                relative_path=parsed_file.relative_path,
                language=parsed_file.language,
                root=root_node,
            )
        except ASTBuilderError:
            raise
        except Exception as err:
            raise ASTBuilderError(
                f"Failed to build ASTDocument for '{parsed_file.path}': {err}"
            ) from err

    def build_node(
        self, ts_node: Any, source_bytes: bytes, node_index: int = 0
    ) -> ASTNode:
        """Recursively converts a Tree-sitter Node into a normalized ASTNode.

        Args:
            ts_node: Tree-sitter Node instance.
            source_bytes: UTF-8 encoded source code bytes.
            node_index: Child index position for deterministic ID generation.

        Returns:
            An immutable ASTNode instance.

        Raises:
            ASTBuilderError: If converting the node fails.
        """
        try:
            start_row = ts_node.start_point[0] if hasattr(ts_node, "start_point") else ts_node.start_point.row
            start_col = ts_node.start_point[1] if hasattr(ts_node, "start_point") else ts_node.start_point.column
            end_row = ts_node.end_point[0] if hasattr(ts_node, "end_point") else ts_node.end_point.row
            end_col = ts_node.end_point[1] if hasattr(ts_node, "end_point") else ts_node.end_point.column

            # Convert 0-indexed line numbers to 1-indexed for standard human readability
            start_line = start_row + 1
            end_line = end_row + 1

            start_byte = ts_node.start_byte
            end_byte = ts_node.end_byte

            text = source_bytes[start_byte:end_byte].decode("utf-8", errors="replace")
            node_type = ts_node.type

            # Deterministic unique node ID string
            node_id = f"ast_{start_line}_{start_col}_{end_line}_{end_col}_{node_type}_{node_index}"

            # Recursively build child nodes in exact order
            children: list[ASTNode] = []
            for idx, child in enumerate(ts_node.children):
                child_ast_node = self.build_node(
                    ts_node=child,
                    source_bytes=source_bytes,
                    node_index=idx,
                )
                children.append(child_ast_node)

            return ASTNode(
                id=node_id,
                type=node_type,
                text=text,
                start_line=start_line,
                start_column=start_col,
                end_line=end_line,
                end_column=end_col,
                children=children,
            )
        except Exception as err:
            raise ASTBuilderError(
                f"Failed to convert Tree-sitter node of type '{getattr(ts_node, 'type', 'unknown')}': {err}"
            ) from err
