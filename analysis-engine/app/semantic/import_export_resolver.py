"""Import & Export Resolution Engine."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.semantic.project_models import (
    ImportDeclaration,
    ExportDeclaration,
    ProjectFile,
    ProjectSymbol,
)


class ResolvedImport(BaseModel):
    """Represents a successfully resolved import declaration mapping to its target symbol."""

    import_declaration: ImportDeclaration = Field(..., description="The source import declaration.")
    target_file: Path = Field(..., description="The absolute path of the target file defining the symbol.")
    target_symbol: ProjectSymbol = Field(..., description="The resolved symbol definition.")

    model_config = ConfigDict(frozen=True)


class ImportExportResolutionResult(BaseModel):
    """Contains the results and diagnostics of an import/export resolution run."""

    resolved_imports: List[ResolvedImport] = Field(default_factory=list, description="All resolved imports.")
    unresolved_imports: List[ImportDeclaration] = Field(default_factory=list, description="All unresolved imports.")
    diagnostics: List[str] = Field(default_factory=list, description="Resolution warnings and diagnostics.")

    model_config = ConfigDict(frozen=True)


class ImportExportResolver:
    """Resolves explicit import and export declarations across project files."""

    def __init__(self) -> None:
        pass

    def resolve_specifier_to_path(self, importing_file: Path, specifier: str, known_paths: Set[Path]) -> Optional[Path]:
        """Resolves a module specifier path relative to the importing file against known paths.

        Args:
            importing_file: The path of the file containing the import.
            specifier: The import specifier string (e.g. './utils').
            known_paths: Set of all known file paths in the project.

        Returns:
            The resolved target file Path, or None if it cannot be resolved.
        """
        # 1. Resolve all known paths to absolute forms in a map
        abs_known_map: Dict[Path, Path] = {}
        for kp in known_paths:
            try:
                abs_known_map[kp.resolve()] = kp
            except Exception:
                try:
                    abs_known_map[kp.absolute()] = kp
                except Exception:
                    abs_known_map[kp] = kp

        # 2. Compute absolute path of normalized resolved path
        if specifier.startswith('.'):
            base_dir = importing_file.parent
            normalized_raw = base_dir / specifier
            try:
                abs_resolved = normalized_raw.resolve()
            except Exception:
                try:
                    abs_resolved = normalized_raw.absolute()
                except Exception:
                    abs_resolved = normalized_raw
        else:
            normalized_raw = Path(specifier)
            try:
                abs_resolved = normalized_raw.resolve()
            except Exception:
                try:
                    abs_resolved = normalized_raw.absolute()
                except Exception:
                    abs_resolved = normalized_raw

        # 3. Check direct match
        if abs_resolved in abs_known_map:
            return abs_known_map[abs_resolved]

        # 4. Check matches stripping suffix extensions
        for abs_known, original in abs_known_map.items():
            if abs_known.with_suffix('') == abs_resolved:
                return original
            if abs_known.with_suffix('') == abs_resolved.with_suffix(''):
                return original

        return None

    def resolve_project_imports(self, files: Dict[Path, ProjectFile]) -> ImportExportResolutionResult:
        """Resolves explicit imports to explicit exports across all project files.

        Args:
            files: Dictionary mapping file paths to their ProjectFile declarations.

        Returns:
            An ImportExportResolutionResult containing resolved links and diagnostics.
        """
        known_paths = set(files.keys())
        resolved_imports: List[ResolvedImport] = []
        unresolved_imports: List[ImportDeclaration] = []
        diagnostics: List[str] = []

        # 1. Index all explicit exports: (target_file_path, exported_name) -> ProjectSymbol
        exports_index: Dict[Tuple[Path, str], ProjectSymbol] = {}
        duplicate_exports: Set[Tuple[Path, str]] = set()

        for file_path, project_file in files.items():
            symbols_map = {sym.id: sym for sym in project_file.symbols}
            for export in project_file.exports:
                export_key = (file_path, export.exported_name)
                
                # Check for duplicate exports in the same file
                if export_key in exports_index:
                    duplicate_exports.add(export_key)
                    diagnostics.append(
                        f"Duplicate export of '{export.exported_name}' detected in file: {file_path}"
                    )
                    continue

                if export.local_symbol_id and export.local_symbol_id in symbols_map:
                    exports_index[export_key] = symbols_map[export.local_symbol_id]

        # 2. Resolve each import declaration
        for file_path, project_file in files.items():
            for imp in project_file.imports:
                target_file_path = self.resolve_specifier_to_path(file_path, imp.module_specifier, known_paths)

                if not target_file_path:
                    # Unresolved module specifier
                    unresolved_imports.append(imp)
                    diagnostics.append(
                        f"Unresolved module specifier '{imp.module_specifier}' imported by file: {file_path}"
                    )
                    continue

                # Search in target file exports index
                export_key = (target_file_path, imp.imported_name)
                if export_key in duplicate_exports:
                    unresolved_imports.append(imp)
                    diagnostics.append(
                        f"Ambiguous import of '{imp.imported_name}' from '{imp.module_specifier}' in {file_path} due to duplicate exports."
                    )
                    continue

                resolved_symbol = exports_index.get(export_key)
                if resolved_symbol:
                    # Successfully resolved import declaration!
                    resolved_imports.append(
                        ResolvedImport(
                            import_declaration=imp,
                            target_file=target_file_path,
                            target_symbol=resolved_symbol
                        )
                    )
                else:
                    # Unresolved export name in target file
                    unresolved_imports.append(imp)
                    diagnostics.append(
                        f"Unresolved import name '{imp.imported_name}' from module specifier '{imp.module_specifier}' in file: {file_path}"
                    )

        return ImportExportResolutionResult(
            resolved_imports=resolved_imports,
            unresolved_imports=unresolved_imports,
            diagnostics=diagnostics
        )
