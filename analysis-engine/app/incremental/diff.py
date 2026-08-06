"""Snapshot Difference Engine Module."""

from typing import Tuple

from app.incremental.enums import ChangeType
from app.incremental.exceptions import IncrementalAnalysisValidationError
from app.incremental.interfaces import SnapshotDifferenceEngine
from app.incremental.models import ChangedFile, RepositorySnapshot


class SHA256SnapshotDifferenceEngine(SnapshotDifferenceEngine):
    """Concrete implementation of SnapshotDifferenceEngine comparing file fingerprints."""

    def diff_snapshots(
        self, old_snapshot: RepositorySnapshot, new_snapshot: RepositorySnapshot
    ) -> Tuple[ChangedFile, ...]:
        """Compares old and new RepositorySnapshots, returning sorted ChangedFile DTOs.

        Args:
            old_snapshot: Baseline repository snapshot state.
            new_snapshot: Updated repository snapshot state.

        Returns:
            An immutable tuple of ChangedFile objects sorted alphabetically by normalized path.

        Raises:
            IncrementalAnalysisValidationError if inputs are None or invalid.
        """
        if old_snapshot is None or new_snapshot is None:
            raise IncrementalAnalysisValidationError("Both old_snapshot and new_snapshot must not be None.")
        if not isinstance(old_snapshot, RepositorySnapshot) or not isinstance(new_snapshot, RepositorySnapshot):
            raise IncrementalAnalysisValidationError("Inputs must be instances of RepositorySnapshot.")

        old_keys = set(old_snapshot.fingerprints.keys())
        new_keys = set(new_snapshot.fingerprints.keys())

        # Determine path sets
        added_paths = new_keys - old_keys
        deleted_paths = old_keys - new_keys
        common_paths = old_keys & new_keys

        changed_files_list = []

        # Process Added Files
        for path in added_paths:
            new_fp = new_snapshot.fingerprints[path]
            changed_files_list.append(
                ChangedFile(
                    path=path,
                    change_type=ChangeType.ADDED,
                    old_fingerprint=None,
                    new_fingerprint=new_fp,
                )
            )

        # Process Deleted Files
        for path in deleted_paths:
            old_fp = old_snapshot.fingerprints[path]
            changed_files_list.append(
                ChangedFile(
                    path=path,
                    change_type=ChangeType.DELETED,
                    old_fingerprint=old_fp,
                    new_fingerprint=None,
                )
            )

        # Process Common Files (Modified / Unchanged)
        for path in common_paths:
            old_fp = old_snapshot.fingerprints[path]
            new_fp = new_snapshot.fingerprints[path]

            if old_fp.hash != new_fp.hash:
                change_type = ChangeType.MODIFIED
            else:
                change_type = ChangeType.UNCHANGED

            changed_files_list.append(
                ChangedFile(
                    path=path,
                    change_type=change_type,
                    old_fingerprint=old_fp,
                    new_fingerprint=new_fp,
                )
            )

        # Sort alphabetically by normalized path to ensure deterministic output ordering
        changed_files_list.sort(key=lambda cf: cf.path)

        return tuple(changed_files_list)
