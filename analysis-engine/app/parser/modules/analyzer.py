"""Module analyzer module.

Provides the ModuleAnalyzer class responsible for extracting import and export symbols
from an ASTDocument into an immutable ModuleMetadata container.
"""

from app.parser.ast import ASTDocument
from app.parser.modules.exceptions import ModuleAnalysisError
from app.parser.modules.models import ModuleMetadata
from app.parser.modules.visitor import ModuleVisitor


class ModuleAnalyzer:
    """Analyzes module import and export declarations within an ASTDocument."""

    def __init__(self) -> None:
        """Initializes the ModuleAnalyzer."""
        pass

    def analyze(self, document: ASTDocument) -> ModuleMetadata:
        """Analyzes an ASTDocument and extracts import/export declaration symbols.

        Args:
            document: Normalized ASTDocument instance.

        Returns:
            An immutable ModuleMetadata object.

        Raises:
            ModuleAnalysisError: If import/export analysis fails.
        """
        try:
            if not document or not document.root:
                raise ModuleAnalysisError("Invalid or missing ASTDocument root node.")

            visitor = ModuleVisitor(document_path=document.path)
            visitor.visit(document.root)

            return ModuleMetadata(
                imports=visitor.imports,
                exports=visitor.exports,
                import_count=len(visitor.imports),
                export_count=len(visitor.exports),
            )
        except ModuleAnalysisError:
            raise
        except Exception as err:
            raise ModuleAnalysisError(
                f"Failed to analyze module import/exports for '{document.path}': {err}"
            ) from err
