"""Incremental Analysis Domain Interfaces Module."""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from app.incremental.models import (
    ChangedFile,
    FileFingerprint,
    IncrementalAnalysisResult,
    RepositorySnapshot,
)


class FingerprintGenerator(ABC):
    """Abstract interface generating fingerprints for files."""

    @abstractmethod
    def generate_fingerprint(self, file_path: str) -> FileFingerprint:
        """Generates file fingerprint containing hashing signature details.

        Args:
            file_path: Relative string path.

        Returns:
            The generated FileFingerprint value object.
        """
        pass


class SnapshotCalculator(ABC):
    """Abstract interface generating repository snapshots for specified code bases or commits."""

    @abstractmethod
    def calculate_snapshot(self, commit_id: str) -> RepositorySnapshot:
        """Walks repository and builds snapshot index.

        Args:
            commit_id: Identifier commit hash.

        Returns:
            The compiled RepositorySnapshot domain model.
        """
        pass


class SnapshotDifferenceEngine(ABC):
    """Abstract engine generating list of file changes between snapshot benchmarks."""

    @abstractmethod
    def diff_snapshots(
        self, old_snapshot: RepositorySnapshot, new_snapshot: RepositorySnapshot
    ) -> Tuple[ChangedFile, ...]:
        """Calculates difference list of file revisions.

        Args:
            old_snapshot: Reference baseline snapshot.
            new_snapshot: Current/target snapshot.

        Returns:
            An immutable tuple of ChangedFile descriptors.
        """
        pass


class IncrementalAnalysisPersistence(ABC):
    """Abstract persistence repository contract for saving and retrieving incremental results."""

    @abstractmethod
    def save_result(self, result: IncrementalAnalysisResult) -> None:
        """Persists the result object.

        Args:
            result: The completed incremental result model.
        """
        pass

    @abstractmethod
    def get_result(self, analysis_id: uuid.UUID) -> Optional[IncrementalAnalysisResult]:
        """Retrieves a result by tracking identifier.

        Args:
            analysis_id: Tracking UUID.

        Returns:
            The stored IncrementalAnalysisResult or None.
        """
        pass

    @abstractmethod
    def save_snapshot(self, snapshot: RepositorySnapshot) -> None:
        """Persists the RepositorySnapshot object.

        Args:
            snapshot: Repository snapshot to store.
        """
        pass

    @abstractmethod
    def get_snapshot(self, commit_id: str) -> Optional[RepositorySnapshot]:
        """Retrieves a RepositorySnapshot by commit ID.

        Args:
            commit_id: Unique commit hash identifier.

        Returns:
            The stored RepositorySnapshot or None.
        """
        pass
