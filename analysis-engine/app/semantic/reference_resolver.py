"""Reference Resolution Engine module."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.semantic.enums import ReferenceKind
from app.semantic.models import Location, SemanticReference, SemanticSymbol
from app.semantic.scope_manager import ScopeManager
from app.semantic.symbol_table import SymbolTable
from app.semantic.project_symbol_index import ProjectSymbolIndex
from app.semantic.import_export_resolver import ImportExportResolver
from app.semantic.project_models import (
    ProjectSymbol,
    SymbolReference,
    ProjectFile,
)

logger = logging.getLogger("analysis-engine")


class ReferenceResolver:
    """Resolves identifier references to declared symbols using lexical scope and symbol table lookups."""

    def __init__(self, scope_manager: ScopeManager, symbol_table: SymbolTable) -> None:
        """Initializes the ReferenceResolver with ScopeManager and SymbolTable dependencies.

        Args:
            scope_manager: Reusable scope manager tracking lexical scopes.
            symbol_table: Reusable symbol table storing symbols declarations.
        """
        self.scope_manager = scope_manager
        self.symbol_table = symbol_table
        self._resolved_references: List[SemanticReference] = []
        self._unresolved_references: List[Tuple[str, Location]] = []
        self._diagnostics: List[str] = []

    def resolve_reference(
        self,
        name: str,
        location: Location,
        start_scope_id: Optional[str] = None,
        reference_kind: ReferenceKind = ReferenceKind.READ,
    ) -> Optional[SemanticSymbol]:
        """Resolves an identifier reference by name to its declaring SemanticSymbol.

        Ascends the lexical scope hierarchy starting from the specified or active scope.

        Args:
            name: The identifier name to resolve.
            location: The location where the identifier usage occurred.
            start_scope_id: Optional scope ID to start the search from.
                            Defaults to the scope manager's current active scope.
            reference_kind: The kind of reference relationship (e.g. READ, CALL).

        Returns:
            The resolved SemanticSymbol, or None if the identifier cannot be resolved.
        """
        # Determine starting scope node
        if start_scope_id is not None:
            curr_scope = self.scope_manager.get_scope_by_id(start_scope_id)
            if curr_scope is None:
                msg = f"Invalid starting scope ID '{start_scope_id}' during resolution of '{name}' at line {location.start_line}."
                self._diagnostics.append(msg)
                logger.warning(msg)
                self._unresolved_references.append((name, location))
                return None
        else:
            curr_scope = self.scope_manager.get_current_scope()

        # Ascend the scope parent hierarchy
        visited_scopes = []
        curr = curr_scope
        while curr is not None:
            visited_scopes.append(curr.id)
            # Query SymbolTable for the name in the current scope level
            symbol = self.symbol_table.get_symbol_by_name_in_scope(curr.id, name)
            if symbol is not None:
                # Successfully resolved reference!
                ref = SemanticReference(
                    symbol_id=symbol.id,
                    reference_kind=reference_kind,
                    location=location,
                )
                self._resolved_references.append(ref)
                return symbol

            curr = curr.parent

        # Global fallback (if the root scope is not in the stack chain for some reason,
        # check global scope anyway)
        root_scope = self.scope_manager.get_root_scope()
        if root_scope.id not in visited_scopes:
            symbol = self.symbol_table.get_symbol_by_name_in_scope(root_scope.id, name)
            if symbol is not None:
                ref = SemanticReference(
                    symbol_id=symbol.id,
                    reference_kind=reference_kind,
                    location=location,
                )
                self._resolved_references.append(ref)
                return symbol

        # If we reach here, the reference is unresolved
        self._unresolved_references.append((name, location))
        diagnostic_msg = f"Unresolved reference to identifier '{name}' at line {location.start_line}, column {location.start_column}."
        self._diagnostics.append(diagnostic_msg)
        logger.info(diagnostic_msg)
        return None

    def get_resolved_references(self) -> List[SemanticReference]:
        """Returns the list of all successfully resolved SemanticReference objects.

        Returns:
            List of SemanticReference instances.
        """
        return list(self._resolved_references)

    def get_unresolved_references(self) -> List[Tuple[str, Location]]:
        """Returns all unresolved reference name and Location pairs.

        Returns:
            List of unresolved reference tuples.
        """
        return list(self._unresolved_references)

    def get_diagnostics(self) -> List[str]:
        """Returns generated diagnostics warnings for unresolved or invalid references.

        Returns:
            List of diagnostic strings.
        """
        return list(self._diagnostics)

    def get_references_for_symbol(self, symbol_id: str) -> List[SemanticReference]:
        """Retrieves all successfully resolved references pointing to the given symbol ID.

        Args:
            symbol_id: The target symbol identifier.

        Returns:
            List of SemanticReference instances.
        """
        return [ref for ref in self._resolved_references if ref.symbol_id == symbol_id]

    def clear(self) -> None:
        """Clears all recorded reference resolution histories and diagnostics."""
        self._resolved_references.clear()
        self._unresolved_references.clear()
        self._diagnostics.clear()


class ResolvedReference(BaseModel):
    """Represents a resolved identifier reference mapping to its target ProjectSymbol."""

    reference: SymbolReference = Field(..., description="The source symbol reference.")
    target_symbol: ProjectSymbol = Field(..., description="The resolved symbol definition.")

    model_config = ConfigDict(frozen=True)


class ReferenceResolutionResult(BaseModel):
    """Contains the results and diagnostics of a cross-file reference resolution run."""

    resolved_references: List[ResolvedReference] = Field(
        default_factory=list, description="All successfully resolved references."
    )
    unresolved_references: List[SymbolReference] = Field(
        default_factory=list, description="All unresolved references."
    )
    diagnostics: List[str] = Field(
        default_factory=list, description="Resolution warnings and diagnostics."
    )

    model_config = ConfigDict(frozen=True)


class CrossFileReferenceResolver:
    """Resolves identifier reference usages to declared symbols across multiple project files."""

    def __init__(self, index: ProjectSymbolIndex, import_resolver: ImportExportResolver) -> None:
        """Initializes the CrossFileReferenceResolver with index and import resolver dependencies.

        Args:
            index: Read-only ProjectSymbolIndex.
            import_resolver: Reusable ImportExportResolver.
        """
        self.index = index
        self.import_resolver = import_resolver

    def resolve_project_references(self, files: Dict[Path, ProjectFile]) -> ReferenceResolutionResult:
        """Resolves all identifier references across the project.

        Args:
            files: Dict mapping project file paths to their ProjectFile declarations.

        Returns:
            A ReferenceResolutionResult containing resolved links and diagnostics.
        """
        resolved_references: List[ResolvedReference] = []
        unresolved_references: List[SymbolReference] = []
        diagnostics: List[str] = []

        # 1. Resolve project-wide imports
        imports_result = self.import_resolver.resolve_project_imports(files)
        diagnostics.extend(imports_result.diagnostics)

        # Map: (importing_file_path, local_alias_or_name) -> target ProjectSymbol
        resolved_imports_map: Dict[Tuple[Path, str], ProjectSymbol] = {}
        for resolved_imp in imports_result.resolved_imports:
            imp_decl = resolved_imp.import_declaration
            file_path = imp_decl.location.file_path
            local_name = imp_decl.local_alias if imp_decl.local_alias else imp_decl.imported_name
            resolved_imports_map[(file_path, local_name)] = resolved_imp.target_symbol

        # 2. Iterate through each file and resolve references
        for file_path, project_file in files.items():
            for ref in project_file.references:
                # Check resolved imports first
                import_key = (file_path, ref.name)
                if import_key in resolved_imports_map:
                    resolved_references.append(
                        ResolvedReference(reference=ref, target_symbol=resolved_imports_map[import_key])
                    )
                    continue

                # Check local symbols in the same file
                local_matches = [sym for sym in project_file.symbols if sym.name == ref.name]
                if len(local_matches) == 1:
                    resolved_references.append(
                        ResolvedReference(reference=ref, target_symbol=local_matches[0])
                    )
                elif len(local_matches) > 1:
                    # Ambiguous local reference
                    unresolved_references.append(ref)
                    diagnostics.append(
                        f"Ambiguous local reference to name '{ref.name}' in file {file_path} (multiple declarations found)."
                    )
                else:
                    # Unresolved reference
                    unresolved_references.append(ref)
                    diagnostics.append(
                        f"Unresolved reference to name '{ref.name}' in file {file_path}."
                    )

        return ReferenceResolutionResult(
            resolved_references=resolved_references,
            unresolved_references=unresolved_references,
            diagnostics=diagnostics,
        )

