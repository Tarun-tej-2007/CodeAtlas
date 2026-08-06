"""Repository Snapshot Service Module."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Union

from app.incremental.exceptions import IncrementalAnalysisValidationError
from app.incremental.models import FileFingerprint, RepositorySnapshot
from app.incremental.interfaces import FingerprintGenerator
from app.incremental.fingerprint import SHA256FingerprintGenerator
from app.scanner.pipeline import ScannerPipeline


class RepositorySnapshotService:
    """Service responsible for scanning the repository workspace and compiling an immutable RepositorySnapshot."""

    def __init__(
        self,
        scanner_pipeline: ScannerPipeline | None = None,
        fingerprint_generator: FingerprintGenerator | None = None,
    ) -> None:
        """Initializes the snapshot service with injected ScannerPipeline and FingerprintGenerator."""
        self.scanner_pipeline = scanner_pipeline or ScannerPipeline()
        self.fingerprint_generator = fingerprint_generator or SHA256FingerprintGenerator()

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
                # Delegate to injected fingerprint generator
                fp = self.fingerprint_generator.generate_fingerprint(
                    str(abs_path), relative_path=rel_path_str
                )
                fingerprints[rel_path_str] = fp
            except Exception as e:
                # Log or propagate file access failures defensively
                raise IncrementalAnalysisValidationError(
                    f"Failed to generate fingerprint metadata for file '{rel_path_str}': {e}"
                ) from e

        return RepositorySnapshot(
            commit_id=commit_id,
            fingerprints=fingerprints,
        )
