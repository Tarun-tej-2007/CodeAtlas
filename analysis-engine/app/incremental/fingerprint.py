"""File Fingerprint Generator Service Module."""

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

from app.incremental.exceptions import (
    IncrementalAnalysisValidationError,
    IncrementalAnalysisFileSystemError,
)
from app.incremental.interfaces import FingerprintGenerator
from app.incremental.models import FileFingerprint


class SHA256FingerprintGenerator(FingerprintGenerator):
    """Concrete FingerprintGenerator implementation producing immutable FileFingerprint value objects using SHA-256."""

    def __init__(self, base_dir: Optional[Union[Path, str]] = None) -> None:
        """Initializes the generator with optional base_dir to relativize path metadata.

        Args:
            base_dir: Optional workspace root directory.
        """
        self.base_dir = Path(base_dir).resolve() if base_dir is not None else None

    def generate_fingerprint(self, file_path: str, relative_path: Optional[str] = None) -> FileFingerprint:
        """Generates an immutable FileFingerprint for the given file.

        Args:
            file_path: Filesystem path to the target file.
            relative_path: Optional pre-calculated relative path. If not provided,
                           resolves relative to base_dir if configured.

        Returns:
            The generated FileFingerprint value object.

        Raises:
            IncrementalAnalysisValidationError if validation fails or file is missing.
        """
        if file_path is None or not str(file_path).strip():
            raise IncrementalAnalysisValidationError("file_path must be a non-empty string.")

        target_path = Path(file_path).resolve()
        if not target_path.exists():
            raise IncrementalAnalysisValidationError(f"File does not exist: {target_path}")
        if not target_path.is_file():
            raise IncrementalAnalysisValidationError(f"Path is not a regular file: {target_path}")

        # Normalize path
        if relative_path is not None:
            norm_path = str(relative_path).replace("\\", "/")
        elif self.base_dir is not None:
            try:
                norm_path = str(target_path.relative_to(self.base_dir)).replace("\\", "/")
            except ValueError:
                norm_path = target_path.name
        else:
            norm_path = target_path.name

        from app.incremental.cache import execution_cache

        # Check execution cache first to avoid duplicate fingerprint generation in the same run
        cache = execution_cache.get()
        if cache is not None:
            cache_key = f"fp:{norm_path}"
            if cache_key in cache:
                return cache[cache_key]

        try:
            stat_info = target_path.stat()
            size = stat_info.st_size
            mtime_utc = datetime.fromtimestamp(stat_info.st_mtime, tz=timezone.utc)

            # Check if we can reuse previously computed immutable hash from previous snapshot
            sha256_hash = None
            if cache is not None and "previous_snapshot" in cache:
                prev_snap: RepositorySnapshot = cache["previous_snapshot"]
                if norm_path in prev_snap.fingerprints:
                    prev_fp = prev_snap.fingerprints[norm_path]
                    # Compare mtime and size. If they match exactly, we can safely reuse the hash
                    if prev_fp.size == size and prev_fp.last_modified == mtime_utc:
                        sha256_hash = prev_fp.hash

            # Calculate hash only if it could not be safely reused
            if sha256_hash is None:
                sha256_hash = self._calculate_sha256(target_path)

            fp = FileFingerprint(
                path=norm_path,
                hash=sha256_hash,
                size=size,
                last_modified=mtime_utc,
            )

            # Cache the generated fingerprint in execution cache context
            if cache is not None:
                cache[f"fp:{norm_path}"] = fp

            return fp
        except FileNotFoundError as e:
            # Handle transient filesystem race (e.g. deletion during processing)
            raise IncrementalAnalysisFileSystemError(
                f"Transient filesystem deletion race occurred for '{norm_path}': {e}"
            ) from e
        except Exception as e:
            raise IncrementalAnalysisFileSystemError(
                f"Failed to generate fingerprint for '{norm_path}': {e}"
            ) from e

    def generate_fingerprints_batch(self, file_paths: list[str]) -> list[FileFingerprint]:
        """Performs optimized batch fingerprint generation preserving deterministic alphabetical order.

        Args:
            file_paths: Collection of file paths to process.

        Returns:
            List of FileFingerprint DTOs sorted by relative path.
        """
        results = []
        for path in file_paths:
            try:
                results.append(self.generate_fingerprint(path))
            except Exception:
                continue
        # Ensure output is deterministically ordered by path
        results.sort(key=lambda fp: fp.path)
        return results

    def _calculate_sha256(self, target_path: Path) -> str:
        """Computes SHA-256 hash using chunked buffered reading."""
        sha256_algo = hashlib.sha256()
        with open(target_path, "rb") as f:
            while chunk := f.read(65536):  # Efficient 64KB chunks
                sha256_algo.update(chunk)
        return sha256_algo.hexdigest()
