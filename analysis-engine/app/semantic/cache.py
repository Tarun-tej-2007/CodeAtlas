"""Thread-safe, in-memory caching utilities module."""

import threading
from pathlib import Path
from typing import Dict, Optional, Tuple


class PathResolutionCache:
    """Thread-safe in-memory cache for resolved import path specifiers."""

    def __init__(self) -> None:
        """Initializes the PathResolutionCache with reentrant lock for thread safety."""
        self._cache: Dict[Tuple[Path, str], Optional[Path]] = {}
        self._lock = threading.RLock()

    def get(self, importing_file: Path, specifier: str) -> Optional[Path]:
        """Gets a cached resolved path if present.

        Args:
            importing_file: The path of the file containing the import.
            specifier: The import specifier string.

        Returns:
            The cached Path, or None.
        """
        with self._lock:
            return self._cache.get((importing_file, specifier))

    def set(self, importing_file: Path, specifier: str, resolved_path: Optional[Path]) -> None:
        """Sets a cached resolved path.

        Args:
            importing_file: The path of the file containing the import.
            specifier: The import specifier string.
            resolved_path: The resolved target file Path.
        """
        with self._lock:
            self._cache[(importing_file, specifier)] = resolved_path

    def clear(self) -> None:
        """Clears all cached resolved paths."""
        with self._lock:
            self._cache.clear()
