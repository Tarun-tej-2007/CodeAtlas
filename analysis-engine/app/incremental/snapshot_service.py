"""Repository Snapshot Service Module."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Union

from app.incremental.exceptions import IncrementalAnalysisValidationError
from app.incremental.models import FileFingerprint, RepositorySnapshot
from app.scanner.pipeline import ScannerPipeline


class RepositorySnapshotService:
    """Service responsible for scanning the repository workspace and compiling an immutable RepositorySnapshot."""

    def __init__(self, scanner_pipeline: ScannerPipeline | None = None) -> None:
        """Initializes the snapshot service with injected ScannerPipeline."""
        self.scanner_pipeline = scanner_pipeline or ScannerPipeline()

    def create_snapshot(self, repository_root: Union[Path, str], commit_id: str) -> RepositorySnapshot:
        """Enumerate repository workspace files and compiles a deterministic RepositorySnapshot.

        Args:
            repository_root: Path to codebase root directory.
            commit_id: Git commit hash identifier representing target code point.

        Returns:
            An immutable RepositorySnapshot instance.
        """
        if repository_root is None:
            raise IncrementalAnalysisValidationError("repository_root must not be None.")
        if commit_id is None or not commit_id.strip():
            raise IncrementalAnalysisValidationError("commit_id must not be empty or whitespace.")

        root_path = Path(repository_root).resolve()
        if not root_path.exists():
            raise IncrementalAnalysisValidationError(f"Repository root directory does not exist: {root_path}")
        if not root_path.is_dir():
            raise IncrementalAnalysisValidationError(f"Repository root path is not a directory: {root_path}")

        # Execute existing ScannerPipeline
        # Reuses exclusion/filtering rules automatically configured in discovery_service
        scan_res = self.scanner_pipeline.scan(root_path)
        if scan_res.discovery_result is None or not scan_res.discovery_result.files:
            # Handle empty repositories or fully ignored repository paths
            return RepositorySnapshot(commit_id=commit_id, fingerprints={})

        fingerprints: Dict[str, FileFingerprint] = {}

        # Order files deterministically by relative path to guarantee output stability
        sorted_files = sorted(
            scan_res.discovery_result.files,
            key=lambda f: str(f.relative_path).replace("\\", "/"),
        )

        for discovered_file in sorted_files:
            abs_path = discovered_file.absolute_path
            rel_path_str = str(discovered_file.relative_path).replace("\\", "/")

            if not abs_path.exists():
                # Defend against filesystem changes/race deletions
                continue

            try:
                # 1. Calculate SHA-256 fingerprint hash
                sha256_hash = self._calculate_sha256(abs_path)

                # 2. Extract UTC modification metadata
                stat_info = abs_path.stat()
                mtime_utc = datetime.fromtimestamp(stat_info.st_mtime, tz=timezone.utc)

                fingerprints[rel_path_str] = FileFingerprint(
                    path=rel_path_str,
                    hash=sha256_hash,
                    size=discovered_file.size,
                    last_modified=mtime_utc,
                )
            except Exception as e:
                # Log or propagate file access failures defensively
                raise IncrementalAnalysisValidationError(
                    f"Failed to generate fingerprint metadata for file '{rel_path_str}': {e}"
                ) from e

        return RepositorySnapshot(
            commit_id=commit_id,
            fingerprints=fingerprints,
        )

    def _calculate_sha256(self, file_path: Path) -> str:
        """Helper computing SHA-256 checksums from binary blocks."""
        sha256_algo = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256_algo.update(chunk)
        return sha256_algo.hexdigest()
