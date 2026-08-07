"""AI Intelligence persistence service coordinating DTO serialization and storage."""

import json
import threading
import uuid
from typing import Any, Optional, Tuple

from app.ai.exceptions import AIPersistenceError
from app.ai.interfaces import AIAnalysisPersistence, AIRepository
from app.ai.models import AIAnalysis, AIResult, ArchitectureReview


class AIAnalysisPersistenceService(AIAnalysisPersistence):
    """Concrete AIAnalysisPersistence execution service using thread-safe serialization."""

    def __init__(self, repository: AIRepository) -> None:
        """Initializes persistence service with storage repository collaborator.

        Args:
            repository: Storage-agnostic repository driver.
        """
        self.repository = repository
        self._lock = threading.Lock()

    def _serialize(self, model: Any) -> dict:
        """Helper to safely serialize a Pydantic model to a JSON-compatible dict."""
        try:
            return json.loads(model.model_dump_json())
        except Exception as e:
            raise AIPersistenceError(f"Serialization failure: {e}") from e

    def _deserialize_result(self, data: dict) -> AIResult:
        """Safely deserializes and reconstructs nested ArchitectureReview inside extra_info."""
        res = AIResult.model_validate(data)
        if "review" in res.extra_info and isinstance(res.extra_info["review"], dict):
            review_data = res.extra_info["review"]
            review_obj = ArchitectureReview.model_validate(review_data)
            extra_info_new = dict(res.extra_info)
            extra_info_new["review"] = review_obj
            res = AIResult(
                project_id=res.project_id,
                commit_id=res.commit_id,
                analysis=res.analysis,
                extra_info=extra_info_new,
            )
        return res

    def save_analysis(self, project_id: uuid.UUID, analysis: AIAnalysis) -> None:
        """Saves an AIAnalysis record.

        Args:
            project_id: Associated project scoping UUID.
            analysis: Target AIAnalysis instance.

        Raises:
            AIPersistenceError: If save fails.
        """
        if project_id is None:
            raise AIPersistenceError("project_id must not be None.")
        if analysis is None:
            raise AIPersistenceError("analysis must not be None.")

        key = f"analysis:{project_id}:{analysis.analysis_id}"
        data = self._serialize(analysis)

        with self._lock:
            try:
                self.repository.save_data(key, data)
            except Exception as e:
                raise AIPersistenceError(f"Failed to persist key '{key}': {e}") from e

    def get_analysis(self, analysis_id: uuid.UUID) -> Optional[AIAnalysis]:
        """Retrieves a previously saved AIAnalysis record.

        Args:
            analysis_id: Target analysis execution UUID.

        Returns:
            AIAnalysis if found, else None.

        Raises:
            AIPersistenceError: If retrieval fails.
        """
        if analysis_id is None:
            raise AIPersistenceError("analysis_id must not be None.")

        target_suffix = f":{analysis_id}"
        with self._lock:
            try:
                keys = self.repository.list_keys("analysis:")
                for k in keys:
                    if k.endswith(target_suffix):
                        data = self.repository.get_data(k)
                        if data:
                            return AIAnalysis.model_validate(data)
            except Exception as e:
                raise AIPersistenceError(f"Failed to query analysis '{analysis_id}': {e}") from e
        return None

    def list_analyses(self, project_id: uuid.UUID) -> Tuple[AIAnalysis, ...]:
        """Lists all AIAnalysis records for a project.

        Args:
            project_id: Associated project scoping UUID.

        Returns:
            An immutable tuple of AIAnalysis records, sorted by started_at descending.

        Raises:
            AIPersistenceError: If listing fails.
        """
        if project_id is None:
            raise AIPersistenceError("project_id must not be None.")

        prefix = f"analysis:{project_id}:"
        analyses = []

        with self._lock:
            try:
                keys = self.repository.list_keys(prefix)
                for k in keys:
                    data = self.repository.get_data(k)
                    if data:
                        analyses.append(AIAnalysis.model_validate(data))
            except Exception as e:
                raise AIPersistenceError(f"Failed to list analyses for project '{project_id}': {e}") from e

        # Deterministic sorting: started_at descending, then analysis_id
        analyses.sort(key=lambda a: (a.started_at, a.analysis_id), reverse=True)
        return tuple(analyses)

    def save_result(self, project_id: uuid.UUID, result: AIResult) -> None:
        """Saves an AIResult record.

        Args:
            project_id: Associated project scoping UUID.
            result: Target AIResult instance.

        Raises:
            AIPersistenceError: If save fails.
        """
        if project_id is None:
            raise AIPersistenceError("project_id must not be None.")
        if result is None:
            raise AIPersistenceError("result must not be None.")

        key = f"result:{project_id}:{result.commit_id}"
        data = self._serialize(result)

        with self._lock:
            try:
                self.repository.save_data(key, data)
            except Exception as e:
                raise AIPersistenceError(f"Failed to persist result key '{key}': {e}") from e

    def get_result(self, project_id: uuid.UUID, commit_id: str) -> Optional[AIResult]:
        """Retrieves a previously saved AIResult record by project and commit.

        Args:
            project_id: Associated project scoping UUID.
            commit_id: Associated commit hash.

        Returns:
            AIResult if found, else None.

        Raises:
            AIPersistenceError: If query fails.
        """
        if project_id is None:
            raise AIPersistenceError("project_id must not be None.")
        if not commit_id or not commit_id.strip():
            raise AIPersistenceError("commit_id must be a non-empty string.")

        key = f"result:{project_id}:{commit_id.strip()}"

        with self._lock:
            try:
                data = self.repository.get_data(key)
                if data:
                    return self._deserialize_result(data)
            except Exception as e:
                raise AIPersistenceError(f"Failed to retrieve result '{key}': {e}") from e
        return None

    def list_results(self, project_id: uuid.UUID) -> Tuple[AIResult, ...]:
        """Lists all AIResult records for a project.

        Args:
            project_id: Associated project scoping UUID.

        Returns:
            An immutable tuple of AIResult records, sorted by commit_id.

        Raises:
            AIPersistenceError: If query fails.
        """
        if project_id is None:
            raise AIPersistenceError("project_id must not be None.")

        prefix = f"result:{project_id}:"
        results = []

        with self._lock:
            try:
                keys = self.repository.list_keys(prefix)
                for k in keys:
                    data = self.repository.get_data(k)
                    if data:
                        results.append(self._deserialize_result(data))
            except Exception as e:
                raise AIPersistenceError(f"Failed to list results for project '{project_id}': {e}") from e

        # Deterministic sorting by commit_id
        results.sort(key=lambda r: r.commit_id)
        return tuple(results)

    def delete_result(self, project_id: uuid.UUID, commit_id: str) -> None:
        """Deletes an AIResult record.

        Args:
            project_id: Associated project scoping UUID.
            commit_id: Associated commit hash.

        Raises:
            AIPersistenceError: If delete fails.
        """
        if project_id is None:
            raise AIPersistenceError("project_id must not be None.")
        if not commit_id or not commit_id.strip():
            raise AIPersistenceError("commit_id must be a non-empty string.")

        key = f"result:{project_id}:{commit_id.strip()}"

        with self._lock:
            try:
                self.repository.delete_data(key)
            except Exception as e:
                raise AIPersistenceError(f"Failed to delete result '{key}': {e}") from e
