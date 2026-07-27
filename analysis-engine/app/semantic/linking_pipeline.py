"""Project-wide Semantic Linking Pipeline."""

from typing import Callable, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.semantic.project_models import ProjectSemanticResult
from app.semantic.project_symbol_index import ProjectSymbolIndex
from app.semantic.import_export_resolver import (
    ImportExportResolutionResult,
    ImportExportResolver,
)
from app.semantic.reference_resolver import (
    ReferenceResolutionResult,
    CrossFileReferenceResolver,
)


class LinkedSemanticResult(BaseModel):
    """Immutable, language-agnostic result containing the aggregated outputs of the semantic linking pipeline."""

    original_result: ProjectSemanticResult = Field(
        ..., description="The original project-level semantic result input."
    )
    symbol_index: ProjectSymbolIndex = Field(
        ..., description="The constructed read-only project symbol index lookup."
    )
    import_export_result: ImportExportResolutionResult = Field(
        ..., description="Result of explicit imports and exports resolution."
    )
    reference_resolution_result: ReferenceResolutionResult = Field(
        ..., description="Result of cross-file reference resolution."
    )
    diagnostics: List[str] = Field(
        default_factory=list, description="Aggregated diagnostic warning messages from all stages."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class SemanticLinkingPipeline:
    """Orchestrates project-wide import/export mapping, indexing, and cross-file reference resolution."""

    def __init__(
        self,
        import_resolver: Optional[ImportExportResolver] = None,
        reference_resolver_factory: Optional[
            Callable[[ProjectSymbolIndex, ImportExportResolver], CrossFileReferenceResolver]
        ] = None,
    ) -> None:
        """Initializes the SemanticLinkingPipeline with optional dependency injections.

        Args:
            import_resolver: Optional custom ImportExportResolver instance.
            reference_resolver_factory: Optional custom factory producing CrossFileReferenceResolver.
        """
        self._import_resolver = import_resolver or ImportExportResolver()
        self._reference_resolver_factory = reference_resolver_factory or (
            lambda idx, imp: CrossFileReferenceResolver(idx, imp)
        )

    def link_project(self, project_result: ProjectSemanticResult) -> LinkedSemanticResult:
        """Runs the semantic linking stages over the project semantic result.

        Execution Flow:
            1. Construct ProjectSymbolIndex.
            2. Resolve explicit imports and exports.
            3. Resolve cross-file identifier references.
            4. Compile and order diagnostic warnings.
            5. Return LinkedSemanticResult.

        Args:
            project_result: The aggregated semantic analysis results for all project files.

        Returns:
            LinkedSemanticResult container mapping cross-file references and index lookups.
        """
        # 1. Construct index
        symbol_index = ProjectSymbolIndex(project_result.files)

        # 2. Run Import/Export Resolver
        import_export_res = self._import_resolver.resolve_project_imports(project_result.files)

        # 3. Run Reference Resolver
        ref_resolver = self._reference_resolver_factory(symbol_index, self._import_resolver)
        ref_res = ref_resolver.resolve_project_references(project_result.files)

        # 4. Aggregate diagnostics in a deterministic order
        diagnostics: List[str] = []
        diagnostics.extend(symbol_index.diagnostics)
        diagnostics.extend(import_export_res.diagnostics)
        diagnostics.extend(ref_res.diagnostics)

        # Ensure order is preserved and diagnostics are deduplicated (while keeping order)
        seen = set()
        deduped_diagnostics = []
        for diag in diagnostics:
            if diag not in seen:
                seen.add(diag)
                deduped_diagnostics.append(diag)

        return LinkedSemanticResult(
            original_result=project_result,
            symbol_index=symbol_index,
            import_export_result=import_export_res,
            reference_resolution_result=ref_res,
            diagnostics=deduped_diagnostics,
        )
