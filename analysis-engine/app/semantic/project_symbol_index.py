"""Project-wide Symbol Lookup Index."""

from pathlib import Path
from typing import Dict, List, Optional

from app.semantic.exceptions import SemanticModelError
from app.semantic.project_models import ProjectFile, ProjectSymbol


class ProjectSymbolIndex:
    """An immutable-after-construction lookup index for project-wide symbols."""

    def __init__(self, files: Dict[Path, ProjectFile]) -> None:
        """Initializes the ProjectSymbolIndex by indexing all project symbols.

        Args:
            files: Dictionary mapping file paths to their ProjectFile metadata.

        Raises:
            SemanticModelError: If a duplicate symbol ID is detected.
        """
        # Primary lookup maps
        self._by_id: Dict[str, ProjectSymbol] = {}
        self._by_qualified_name: Dict[str, ProjectSymbol] = {}
        self._by_name: Dict[str, List[ProjectSymbol]] = {}
        self._by_file: Dict[Path, List[ProjectSymbol]] = {}
        self._exported_symbols: List[ProjectSymbol] = []
        self._diagnostics: List[str] = []

        self._build_index(files)

    def _build_index(self, files: Dict[Path, ProjectFile]) -> None:
        """Helper to index all symbols, check for duplicates, and validate consistency."""
        for file_path, project_file in files.items():
            symbols_map = {sym.id: sym for sym in project_file.symbols}

            # 1. Validate export declarations consistency
            for export in project_file.exports:
                if export.local_symbol_id:
                    if export.local_symbol_id not in symbols_map:
                        msg = (
                            f"Inconsistent export mapping: local symbol ID '{export.local_symbol_id}' "
                            f"referenced in export '{export.exported_name}' not found in file: {file_path}"
                        )
                        self._diagnostics.append(msg)
                    else:
                        exported_symbol = symbols_map[export.local_symbol_id]
                        if exported_symbol not in self._exported_symbols:
                            self._exported_symbols.append(exported_symbol)

            # 2. Index all file symbols
            file_symbols: List[ProjectSymbol] = []
            for symbol in project_file.symbols:
                # Validate unique symbol IDs
                if symbol.id in self._by_id:
                    raise SemanticModelError(f"Duplicate symbol ID detected: '{symbol.id}'")

                # Validate unique qualified names (non-fatal warning)
                if symbol.qualified_name in self._by_qualified_name:
                    msg = f"Duplicate qualified name detected: '{symbol.qualified_name}'"
                    self._diagnostics.append(msg)
                else:
                    self._by_qualified_name[symbol.qualified_name] = symbol

                # Index maps
                self._by_id[symbol.id] = symbol

                if symbol.name not in self._by_name:
                    self._by_name[symbol.name] = []
                self._by_name[symbol.name].append(symbol)

                file_symbols.append(symbol)

            self._by_file[file_path] = file_symbols

    def get_symbol_by_id(self, symbol_id: str) -> Optional[ProjectSymbol]:
        """Looks up a project symbol by its unique ID.

        Args:
            symbol_id: The unique symbol identifier.

        Returns:
            The ProjectSymbol instance, or None.
        """
        return self._by_id.get(symbol_id)

    def get_symbol_by_name(self, name: str) -> List[ProjectSymbol]:
        """Looks up project symbols matching a simple name.

        Args:
            name: The simple name of the symbol (e.g. 'helper').

        Returns:
            A list of matching ProjectSymbol instances.
        """
        return list(self._by_name.get(name, []))

    def get_symbol_by_qualified_name(self, qualified_name: str) -> Optional[ProjectSymbol]:
        """Looks up a project symbol by its fully qualified name.

        Args:
            qualified_name: Fully qualified project-level name.

        Returns:
            The ProjectSymbol instance, or None.
        """
        return self._by_qualified_name.get(qualified_name)

    def get_symbols_in_file(self, file_path: Path) -> List[ProjectSymbol]:
        """Looks up all symbols declared within a specific project file.

        Args:
            file_path: The project file path.

        Returns:
            A list of ProjectSymbol instances.
        """
        return list(self._by_file.get(file_path, []))

    def get_exported_symbols(self) -> List[ProjectSymbol]:
        """Retrieves all explicitly exported symbols across the project.

        Returns:
            A list of exported ProjectSymbol instances.
        """
        return list(self._exported_symbols)

    def has_symbol(self, symbol_id: str) -> bool:
        """Checks if a symbol is registered in the index.

        Args:
            symbol_id: The unique symbol identifier.

        Returns:
            True if present, False otherwise.
        """
        return symbol_id in self._by_id

    @property
    def diagnostics(self) -> List[str]:
        """Returns the diagnostics warnings generated during index construction.

        Returns:
            List of diagnostic warning strings.
        """
        return list(self._diagnostics)
