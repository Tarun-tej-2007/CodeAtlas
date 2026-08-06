"""Architecture Evolution Persistence Layer."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from app.evolution.exceptions import EvolutionPersistenceError, EvolutionValidationError
from app.evolution.interfaces import EvolutionPersistence
from app.evolution.models import (
    ArchitecturalRiskReport,
    ArchitectureSnapshot,
    EvolutionResult,
    EvolutionTrendResult,
)


class ArchitectureEvolutionRepository(ABC):
    """Abstract repository isolating physical storage databases from domain concerns."""

    @abstractmethod
    def save_result(self, result_id: uuid.UUID, result_data: Dict[str, Any]) -> None:
        """Saves mapped result payload data to database."""
        pass

    @abstractmethod
    def get_result(self, result_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Retrieves raw result payload data from database by identifier."""
        pass

    @abstractmethod
    def list_results(self) -> Tuple[Dict[str, Any], ...]:
        """Retrieves all raw result payload data from database."""
        pass

    @abstractmethod
    def save_snapshot(self, commit_id: str, snapshot_data: Dict[str, Any]) -> None:
        """Saves mapped snapshot payload data to database."""
        pass

    @abstractmethod
    def get_snapshot(self, commit_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves raw snapshot payload data from database by commit hash."""
        pass

    @abstractmethod
    def save_trend(self, trend_id: uuid.UUID, trend_data: Dict[str, Any]) -> None:
        """Saves mapped trend payload data to database."""
        pass

    @abstractmethod
    def get_trend(self, trend_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Retrieves raw trend payload data from database by identifier."""
        pass

    @abstractmethod
    def save_risk_report(self, report_id: uuid.UUID, report_data: Dict[str, Any]) -> None:
        """Saves mapped risk report payload data to database."""
        pass

    @abstractmethod
    def get_risk_report(self, report_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Retrieves raw risk report payload data from database by identifier."""
        pass


class ArchitectureEvolutionPersistenceService(EvolutionPersistence):
    """Concrete persistence coordinator service translating evolution models into database states."""

    def __init__(self, repository: ArchitectureEvolutionRepository) -> None:
        """Initializes persistence coordinator with constructor-injected repository database.

        Args:
            repository: Thread-safe repository database implementation.
        """
        if repository is None:
            raise ValueError("ArchitectureEvolutionRepository dependency must not be None.")
        if not isinstance(repository, ArchitectureEvolutionRepository):
            raise TypeError("Dependency must inherit from ArchitectureEvolutionRepository abstract contract.")
        self.repository = repository

    def save_result(self, result: EvolutionResult) -> None:
        """Maps and saves EvolutionResult to database.

        Args:
            result: EvolutionResult DTO.
        """
        if result is None:
            raise EvolutionValidationError("result must not be None.")
        if not isinstance(result, EvolutionResult):
            raise EvolutionValidationError("result must be an instance of EvolutionResult.")

        serialized_data = result.model_dump()
        try:
            self.repository.save_result(result.evolution_id, serialized_data)
        except Exception as e:
            raise EvolutionPersistenceError(f"Database write error during save_result: {e}") from e

    def get_result(self, evolution_id: uuid.UUID) -> Optional[EvolutionResult]:
        """Retrieves and deserializes EvolutionResult by identifier.

        Args:
            evolution_id: Tracking result UUID.

        Returns:
            The stored EvolutionResult DTO or None.
        """
        if evolution_id is None or not isinstance(evolution_id, uuid.UUID):
            raise EvolutionValidationError("evolution_id must be a valid UUID.")

        try:
            data = self.repository.get_result(evolution_id)
        except Exception as e:
            raise EvolutionPersistenceError(f"Database read error during get_result: {e}") from e

        if data is None:
            return None

        try:
            return EvolutionResult.model_validate(data)
        except Exception as e:
            raise EvolutionValidationError(f"Failed to deserialize or validate EvolutionResult payload: {e}") from e

    def list_results(self) -> Tuple[EvolutionResult, ...]:
        """Retrieves all stored EvolutionResult instances.

        Returns:
            A tuple of EvolutionResult DTOs.
        """
        try:
            raw_list = self.repository.list_results()
        except Exception as e:
            raise EvolutionPersistenceError(f"Database read error during list_results: {e}") from e

        results = []
        for data in raw_list:
            try:
                results.append(EvolutionResult.model_validate(data))
            except Exception as e:
                raise EvolutionValidationError(f"Failed to deserialize or validate historical result: {e}") from e

        # Ensure deterministic chronological sorting by created_at timestamp
        results.sort(key=lambda r: r.metadata.created_at)
        return tuple(results)

    def save_snapshot(self, snapshot: ArchitectureSnapshot) -> None:
        """Maps and saves ArchitectureSnapshot to database.

        Args:
            snapshot: ArchitectureSnapshot DTO.
        """
        if snapshot is None:
            raise EvolutionValidationError("snapshot must not be None.")
        if not isinstance(snapshot, ArchitectureSnapshot):
            raise EvolutionValidationError("snapshot must be an instance of ArchitectureSnapshot.")

        serialized_data = snapshot.model_dump()
        try:
            self.repository.save_snapshot(snapshot.commit_id, serialized_data)
        except Exception as e:
            raise EvolutionPersistenceError(f"Database write error during save_snapshot: {e}") from e

    def get_snapshot(self, commit_id: str) -> Optional[ArchitectureSnapshot]:
        """Retrieves and deserializes ArchitectureSnapshot by commit identifier.

        Args:
            commit_id: Git commit hash identifier.

        Returns:
            The stored ArchitectureSnapshot DTO or None.
        """
        if commit_id is None or not isinstance(commit_id, str) or not commit_id.strip():
            raise EvolutionValidationError("commit_id must be a non-empty string.")

        try:
            data = self.repository.get_snapshot(commit_id)
        except Exception as e:
            raise EvolutionPersistenceError(f"Database read error during get_snapshot: {e}") from e

        if data is None:
            return None

        try:
            return ArchitectureSnapshot.model_validate(data)
        except Exception as e:
            raise EvolutionValidationError(f"Failed to deserialize or validate ArchitectureSnapshot payload: {e}") from e

    def save_trend(self, trend_id: uuid.UUID, trend: EvolutionTrendResult) -> None:
        """Maps and saves EvolutionTrendResult to database.

        Args:
            trend_id: Tracking result UUID.
            trend: EvolutionTrendResult DTO.
        """
        if trend_id is None or not isinstance(trend_id, uuid.UUID):
            raise EvolutionValidationError("trend_id must be a valid UUID.")
        if trend is None or not isinstance(trend, EvolutionTrendResult):
            raise EvolutionValidationError("trend must be an instance of EvolutionTrendResult.")

        serialized_data = trend.model_dump()
        try:
            self.repository.save_trend(trend_id, serialized_data)
        except Exception as e:
            raise EvolutionPersistenceError(f"Database write error during save_trend: {e}") from e

    def get_trend(self, trend_id: uuid.UUID) -> Optional[EvolutionTrendResult]:
        """Retrieves and deserializes EvolutionTrendResult by identifier.

        Args:
            trend_id: Tracking result UUID.

        Returns:
            The stored EvolutionTrendResult DTO or None.
        """
        if trend_id is None or not isinstance(trend_id, uuid.UUID):
            raise EvolutionValidationError("trend_id must be a valid UUID.")

        try:
            data = self.repository.get_trend(trend_id)
        except Exception as e:
            raise EvolutionPersistenceError(f"Database read error during get_trend: {e}") from e

        if data is None:
            return None

        try:
            return EvolutionTrendResult.model_validate(data)
        except Exception as e:
            raise EvolutionValidationError(f"Failed to deserialize or validate EvolutionTrendResult payload: {e}") from e

    def save_risk_report(self, report_id: uuid.UUID, report: ArchitecturalRiskReport) -> None:
        """Maps and saves ArchitecturalRiskReport to database.

        Args:
            report_id: Tracking result UUID.
            report: ArchitecturalRiskReport DTO.
        """
        if report_id is None or not isinstance(report_id, uuid.UUID):
            raise EvolutionValidationError("report_id must be a valid UUID.")
        if report is None or not isinstance(report, ArchitecturalRiskReport):
            raise EvolutionValidationError("report must be an instance of ArchitecturalRiskReport.")

        serialized_data = report.model_dump()
        try:
            self.repository.save_risk_report(report_id, serialized_data)
        except Exception as e:
            raise EvolutionPersistenceError(f"Database write error during save_risk_report: {e}") from e

    def get_risk_report(self, report_id: uuid.UUID) -> Optional[ArchitecturalRiskReport]:
        """Retrieves and deserializes ArchitecturalRiskReport by identifier.

        Args:
            report_id: Tracking result UUID.

        Returns:
            The stored ArchitecturalRiskReport DTO or None.
        """
        if report_id is None or not isinstance(report_id, uuid.UUID):
            raise EvolutionValidationError("report_id must be a valid UUID.")

        try:
            data = self.repository.get_risk_report(report_id)
        except Exception as e:
            raise EvolutionPersistenceError(f"Database read error during get_risk_report: {e}") from e

        if data is None:
            return None

        try:
            return ArchitecturalRiskReport.model_validate(data)
        except Exception as e:
            raise EvolutionValidationError(f"Failed to deserialize or validate ArchitecturalRiskReport payload: {e}") from e
