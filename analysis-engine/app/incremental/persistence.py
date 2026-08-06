"""Incremental Analysis Persistence Service and Repository Module."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.incremental.exceptions import IncrementalAnalysisValidationError
from app.incremental.interfaces import IncrementalAnalysisPersistence
from app.incremental.models import IncrementalAnalysisResult, RepositorySnapshot


class IncrementalAnalysisRepository(ABC):
    """Abstract repository boundary class isolating physical storage databases from domain concerns."""

    @abstractmethod
    def save_result(self, result_id: uuid.UUID, result_data: Dict[str, Any]) -> None:
        """Saves mapped result payload data to database."""
        pass

    @abstractmethod
    def get_result(self, result_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Retrieves raw result payload data from database by identifier."""
        pass

    @abstractmethod
    def save_snapshot(self, commit_id: str, snapshot_data: Dict[str, Any]) -> None:
        """Saves mapped snapshot payload data to database, overwriting previous commits atomically."""
        pass

    @abstractmethod
    def get_snapshot(self, commit_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves raw snapshot payload data from database by commit hash."""
        pass


class IncrementalAnalysisPersistenceService(IncrementalAnalysisPersistence):
    """Concrete persistence coordinator service translating incremental analysis models into persistence state."""

    def __init__(self, repository: IncrementalAnalysisRepository) -> None:
        """Initializes persistence coordinator with constructor-injected repository database."""
        if repository is None:
            raise ValueError("IncrementalAnalysisRepository dependency must not be None.")
        if not isinstance(repository, IncrementalAnalysisRepository):
            raise TypeError("Dependency must inherit from IncrementalAnalysisRepository abstract contract.")
        self.repository = repository

    def save_result(self, result: IncrementalAnalysisResult) -> None:
        """Maps and saves IncrementalAnalysisResult to persistence storage."""
        if result is None:
            raise IncrementalAnalysisValidationError("result must not be None.")
        if not isinstance(result, IncrementalAnalysisResult):
            raise IncrementalAnalysisValidationError("result must be an instance of IncrementalAnalysisResult.")

        # Serialize Pydantic model to dictionary
        serialized_data = result.model_dump()
        self.repository.save_result(result.analysis_id, serialized_data)

    def get_result(self, analysis_id: uuid.UUID) -> Optional[IncrementalAnalysisResult]:
        """Retrieves and deserializes IncrementalAnalysisResult from persistence storage."""
        if analysis_id is None or not isinstance(analysis_id, uuid.UUID):
            raise IncrementalAnalysisValidationError("analysis_id must be a valid UUID.")

        data = self.repository.get_result(analysis_id)
        if data is None:
            return None

        try:
            # Map back to domain model DTO, validating constraints
            return IncrementalAnalysisResult.model_validate(data)
        except Exception as e:
            raise IncrementalAnalysisValidationError(
                f"Failed to deserialize or validate IncrementalAnalysisResult payload: {e}"
            ) from e

    def save_snapshot(self, snapshot: RepositorySnapshot) -> None:
        """Maps and saves RepositorySnapshot to persistence storage, overwriting existing records."""
        if snapshot is None:
            raise IncrementalAnalysisValidationError("snapshot must not be None.")
        if not isinstance(snapshot, RepositorySnapshot):
            raise IncrementalAnalysisValidationError("snapshot must be an instance of RepositorySnapshot.")

        # Serialize Pydantic model to dictionary
        serialized_data = snapshot.model_dump()
        self.repository.save_snapshot(snapshot.commit_id, serialized_data)

    def get_snapshot(self, commit_id: str) -> Optional[RepositorySnapshot]:
        """Retrieves and deserializes RepositorySnapshot from persistence storage."""
        if commit_id is None or not commit_id.strip():
            raise IncrementalAnalysisValidationError("commit_id must be a non-empty string.")

        data = self.repository.get_snapshot(commit_id)
        if data is None:
            return None

        try:
            # Map back to domain model DTO, validating constraints
            return RepositorySnapshot.model_validate(data)
        except Exception as e:
            raise IncrementalAnalysisValidationError(
                f"Failed to deserialize or validate RepositorySnapshot payload: {e}"
            ) from e
