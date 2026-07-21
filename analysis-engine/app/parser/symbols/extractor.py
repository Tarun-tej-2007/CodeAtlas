"""Symbol extraction engine module.

Provides the SymbolExtractor class responsible for extracting declarations
from an ASTDocument into an immutable SymbolTable.
"""

from app.parser.ast import ASTDocument
from app.parser.symbols.exceptions import SymbolExtractionError
from app.parser.symbols.models import SymbolTable
from app.parser.symbols.visitor import SymbolVisitor


class SymbolExtractor:
    """Extracts declaration symbols from normalized AST documents."""

    def __init__(self) -> None:
        """Initializes the SymbolExtractor."""
        pass

    def extract(self, document: ASTDocument) -> SymbolTable:
        """Extracts all declaration symbols from an ASTDocument.

        Args:
            document: Normalized ASTDocument instance.

        Returns:
            An immutable SymbolTable containing extracted Symbol objects.

        Raises:
            SymbolExtractionError: If symbol extraction fails.
        """
        try:
            if not document or not document.root:
                raise SymbolExtractionError("Invalid or missing ASTDocument root node.")

            visitor = SymbolVisitor(document_path=document.path, language=document.language)
            visitor.visit(document.root)

            return SymbolTable(
                symbols=visitor.symbols,
                count=len(visitor.symbols),
            )
        except SymbolExtractionError:
            raise
        except Exception as err:
            raise SymbolExtractionError(
                f"Failed to extract symbols from ASTDocument for '{document.path}': {err}"
            ) from err
