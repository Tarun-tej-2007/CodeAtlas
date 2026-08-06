"""Pure abstract interface contracts for Architecture Evolution."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from app.evolution.models import (
    ArchitecturalChange,
    ArchitectureSnapshot,
    EvolutionResult,
)


class ArchitectureSnapshotCalculator(ABC):
    """Abstract interface for calculating structural ArchitectureSnapshots."""

    @abstractmethod
    def calculate_snapshot(self, commit_id: str) -> ArchitectureSnapshot:
        """Resolves structural workspace composition.

        Args:
            commit_id: Git commit hash identifier representing target code point.

        Returns:
            The compiled ArchitectureSnapshot domain DTO.
        """
        pass


class EvolutionDifferenceEngine(ABC):
    """Abstract engine comparing benchmark snapshot objects to compile component changes."""

    @abstractmethod
    def diff_snapshots(
        self, old_snapshot: ArchitectureSnapshot, new_snapshot: ArchitectureSnapshot
    ) -> Tuple[ArchitecturalChange, ...]:
        """Compares baseline and target snapshots, resolving component modifications.

        Args:
            old_snapshot: Reference baseline snapshot state.
            new_snapshot: Updated snapshot comparison state.

        Returns:
            Immutable collection tuple of ArchitecturalChange items.
        """
        pass


class EvolutionPersistence(ABC):
    """Abstract repository contract boundary isolating storage concerns from evolution domain."""

    @abstractmethod
    def save_result(self, result: EvolutionResult) -> None:
        """Persists the result data object.

        Args:
            result: Completed EvolutionResult DTO.
        """
        pass

    @abstractmethod
    def get_result(self, evolution_id: uuid.UUID) -> Optional[EvolutionResult]:
        """Retrieves result data object by tracking ID.

        Args:
            evolution_id: Tracking result UUID.

        Returns:
            The stored EvolutionResult DTO or None.
        """
        pass

    @abstractmethod
    def save_snapshot(self, snapshot: ArchitectureSnapshot) -> None:
        """Persists the ArchitectureSnapshot object.

        Args:
            snapshot: Snapshot DTO to store.
        """
        pass

    @abstractmethod
    def get_snapshot(self, commit_id: str) -> Optional[ArchitectureSnapshot]:
        """Retrieves snapshot details by commit identifier.

        Args:
            commit_id: Git commit hash identifier.

        Returns:
            The stored ArchitectureSnapshot DTO or None.
        """
        pass


class ArchitectureAnalysisProvider(ABC):
    """Abstract interface defining the retrieval boundary for codebase analysis reports."""

    @abstractmethod
    def get_dependency_graph(self, commit_id: str) -> Optional[Any]:
        """Retrieves the DependencyGraph compiled for the target commit."""
        pass

    @abstractmethod
    def get_architecture_result(self, commit_id: str) -> Optional[Any]:
        """Retrieves the ArchitectureAnalysisResult compiled for the target commit."""
        pass

    @abstractmethod
    def get_quality_report(self, commit_id: str) -> Optional[Any]:
        """Retrieves the QualityReport compiled for the target commit."""
        pass

    @abstractmethod
    def get_technical_debt_report(self, commit_id: str) -> Optional[Any]:
        """Retrieves the TechnicalDebtReport compiled for the target commit."""
        pass
