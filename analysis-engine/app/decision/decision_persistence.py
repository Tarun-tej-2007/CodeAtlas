"""Decision intelligence persistence service coordinating serialization, deserialization, and repository storage."""

import json
import threading
import uuid
from typing import Any, Optional, Tuple

from app.decision.exceptions import DecisionPersistenceError
from app.decision.interfaces import DecisionPersistence, DecisionRepository
from app.decision.models import (
    ArchitectureDecision,
    DecisionAnalysisResult,
    DecisionDriftReport,
    DecisionHealthReport,
    DecisionTraceGraph,
)


class DecisionPersistenceService(DecisionPersistence):
    """Concrete DecisionPersistence implementation executing thread-safe serialization and repository storage."""

    def __init__(self, repository: DecisionRepository) -> None:
        """Initializes the persistence service using constructor dependency injection."""
        self.repository = repository
        self._lock = threading.Lock()

    def _serialize_model(self, model: Any) -> dict:
        """Helper to serialize a Pydantic model into a JSON-compatible dict."""
        try:
            return json.loads(model.model_dump_json())
        except Exception as e:
            raise DecisionPersistenceError(f"Serialization failure: {str(e)}") from e

    def save_decision(self, project_id: uuid.UUID, decision: ArchitectureDecision) -> None:
        """Saves an architecture decision to storage.

        Args:
            project_id: Associated project identifier.
            decision: Target ArchitectureDecision instance.

        Raises:
            DecisionPersistenceError: If save fails.
        """
        if project_id is None:
            raise DecisionPersistenceError("project_id must not be None.")
        if decision is None:
            raise DecisionPersistenceError("decision must not be None.")

        key = f"decision:{project_id}:{decision.decision_id}"
        serialized = self._serialize_model(decision)

        with self._lock:
            try:
                self.repository.save_data(key, serialized)
            except Exception as e:
                raise DecisionPersistenceError(f"Repository save failure for key '{key}': {str(e)}") from e

    def get_decision(self, decision_id: uuid.UUID) -> Optional[ArchitectureDecision]:
        """Retrieves an architecture decision by its unique identifier.

        Args:
            decision_id: Target decision UUID.

        Returns:
            ArchitectureDecision if found, else None.

        Raises:
            DecisionPersistenceError: If query fails.
        """
        if decision_id is None:
            raise DecisionPersistenceError("decision_id must not be None.")

        # Search for key matching decision_id across any project
        # In a real store we might know the project, or prefix-match key suffixes.
        # Let's search keys using prefix "decision:"
        try:
            keys = self.repository.list_keys_starting_with("decision:")
        except Exception as e:
            raise DecisionPersistenceError(f"Repository query list failure: {str(e)}") from e

        target_suffix = f":{decision_id}"
        matching_key = None
        for k in keys:
            if k.endswith(target_suffix):
                matching_key = k
                break

        if not matching_key:
            return None

        with self._lock:
            try:
                data = self.repository.get_data(matching_key)
            except Exception as e:
                raise DecisionPersistenceError(f"Repository retrieval failure for key '{matching_key}': {str(e)}") from e

        if not data:
            return None

        try:
            return ArchitectureDecision.model_validate(data)
        except Exception as e:
            raise DecisionPersistenceError(f"Deserialization validation failure for decision: {str(e)}") from e

    def list_decisions(self, project_id: uuid.UUID) -> Tuple[ArchitectureDecision, ...]:
        """Lists all decisions associated with a project scope.

        Args:
            project_id: Associated project UUID.

        Returns:
            An immutable tuple of decisions, sorted deterministically by ID.

        Raises:
            DecisionPersistenceError: If query fails.
        """
        if project_id is None:
            raise DecisionPersistenceError("project_id must not be None.")

        prefix = f"decision:{project_id}:"
        try:
            keys = self.repository.list_keys_starting_with(prefix)
        except Exception as e:
            raise DecisionPersistenceError(f"Repository query list failure: {str(e)}") from e

        results = []
        for k in keys:
            with self._lock:
                try:
                    data = self.repository.get_data(k)
                except Exception as e:
                    raise DecisionPersistenceError(f"Repository retrieval failure for key '{k}': {str(e)}") from e

            if data:
                try:
                    dec = ArchitectureDecision.model_validate(data)
                    results.append(dec)
                except Exception as e:
                    raise DecisionPersistenceError(f"Deserialization validation failure for key '{k}': {str(e)}") from e

        # Sort deterministically by decision_id UUID
        results.sort(key=lambda d: str(d.decision_id))
        return tuple(results)

    def save_trace_graph(self, project_id: uuid.UUID, graph: DecisionTraceGraph) -> None:
        """Saves a decision trace graph.

        Args:
            project_id: Associated project UUID.
            graph: The trace graph.

        Raises:
            DecisionPersistenceError: If save fails.
        """
        if project_id is None or graph is None:
            raise DecisionPersistenceError("Parameters project_id and graph must not be None.")

        key = f"trace:{project_id}:{graph.commit_id}"
        serialized = self._serialize_model(graph)

        with self._lock:
            try:
                self.repository.save_data(key, serialized)
            except Exception as e:
                raise DecisionPersistenceError(f"Repository save failure: {str(e)}") from e

    def get_trace_graph(self, project_id: uuid.UUID, commit_id: str) -> Optional[DecisionTraceGraph]:
        """Retrieves a decision trace graph.

        Args:
            project_id: Associated project UUID.
            commit_id: Associated Git commit hash.

        Returns:
            DecisionTraceGraph if found, else None.

        Raises:
            DecisionPersistenceError: If query fails.
        """
        if project_id is None or not commit_id or not commit_id.strip():
            raise DecisionPersistenceError("Parameters project_id and commit_id must not be empty.")

        key = f"trace:{project_id}:{commit_id.strip()}"
        with self._lock:
            try:
                data = self.repository.get_data(key)
            except Exception as e:
                raise DecisionPersistenceError(f"Repository retrieval failure: {str(e)}") from e

        if not data:
            return None

        try:
            return DecisionTraceGraph.model_validate(data)
        except Exception as e:
            raise DecisionPersistenceError(f"Deserialization validation failure: {str(e)}") from e

    def save_drift_report(self, project_id: uuid.UUID, report: DecisionDriftReport) -> None:
        """Saves a decision drift report.

        Args:
            project_id: Associated project UUID.
            report: The drift report.

        Raises:
            DecisionPersistenceError: If save fails.
        """
        if project_id is None or report is None:
            raise DecisionPersistenceError("Parameters project_id and report must not be None.")

        key = f"drift:{project_id}:{report.commit_id}"
        serialized = self._serialize_model(report)

        with self._lock:
            try:
                self.repository.save_data(key, serialized)
            except Exception as e:
                raise DecisionPersistenceError(f"Repository save failure: {str(e)}") from e

    def get_drift_report(self, project_id: uuid.UUID, commit_id: str) -> Optional[DecisionDriftReport]:
        """Retrieves a decision drift report.

        Args:
            project_id: Associated project UUID.
            commit_id: Associated Git commit hash.

        Returns:
            DecisionDriftReport if found, else None.

        Raises:
            DecisionPersistenceError: If query fails.
        """
        if project_id is None or not commit_id or not commit_id.strip():
            raise DecisionPersistenceError("Parameters project_id and commit_id must not be empty.")

        key = f"drift:{project_id}:{commit_id.strip()}"
        with self._lock:
            try:
                data = self.repository.get_data(key)
            except Exception as e:
                raise DecisionPersistenceError(f"Repository retrieval failure: {str(e)}") from e

        if not data:
            return None

        try:
            return DecisionDriftReport.model_validate(data)
        except Exception as e:
            raise DecisionPersistenceError(f"Deserialization validation failure: {str(e)}") from e

    def save_health_report(self, project_id: uuid.UUID, report: DecisionHealthReport) -> None:
        """Saves a decision health report.

        Args:
            project_id: Associated project UUID.
            report: The health report.

        Raises:
            DecisionPersistenceError: If save fails.
        """
        if project_id is None or report is None:
            raise DecisionPersistenceError("Parameters project_id and report must not be None.")

        key = f"health:{project_id}:{report.commit_id}"
        serialized = self._serialize_model(report)

        with self._lock:
            try:
                self.repository.save_data(key, serialized)
            except Exception as e:
                raise DecisionPersistenceError(f"Repository save failure: {str(e)}") from e

    def get_health_report(self, project_id: uuid.UUID, commit_id: str) -> Optional[DecisionHealthReport]:
        """Retrieves a decision health report.

        Args:
            project_id: Associated project UUID.
            commit_id: Associated Git commit hash.

        Returns:
            DecisionHealthReport if found, else None.

        Raises:
            DecisionPersistenceError: If query fails.
        """
        if project_id is None or not commit_id or not commit_id.strip():
            raise DecisionPersistenceError("Parameters project_id and commit_id must not be empty.")

        key = f"health:{project_id}:{commit_id.strip()}"
        with self._lock:
            try:
                data = self.repository.get_data(key)
            except Exception as e:
                raise DecisionPersistenceError(f"Repository retrieval failure: {str(e)}") from e

        if not data:
            return None

        try:
            return DecisionHealthReport.model_validate(data)
        except Exception as e:
            raise DecisionPersistenceError(f"Deserialization validation failure: {str(e)}") from e

    def save_analysis_result(self, project_id: uuid.UUID, result: DecisionAnalysisResult) -> None:
        """Saves a decision analysis result.

        Args:
            project_id: Associated project UUID.
            result: The analysis result.

        Raises:
            DecisionPersistenceError: If save fails.
        """
        if project_id is None or result is None:
            raise DecisionPersistenceError("Parameters project_id and result must not be None.")

        key = f"result:{project_id}:{result.commit_id}"
        serialized = self._serialize_model(result)

        with self._lock:
            try:
                self.repository.save_data(key, serialized)
            except Exception as e:
                raise DecisionPersistenceError(f"Repository save failure: {str(e)}") from e

    def get_analysis_result(self, project_id: uuid.UUID, commit_id: str) -> Optional[DecisionAnalysisResult]:
        """Retrieves a decision analysis result.

        Args:
            project_id: Associated project UUID.
            commit_id: Associated Git commit hash.

        Returns:
            DecisionAnalysisResult if found, else None.

        Raises:
            DecisionPersistenceError: If query fails.
        """
        if project_id is None or not commit_id or not commit_id.strip():
            raise DecisionPersistenceError("Parameters project_id and commit_id must not be empty.")

        key = f"result:{project_id}:{commit_id.strip()}"
        with self._lock:
            try:
                data = self.repository.get_data(key)
            except Exception as e:
                raise DecisionPersistenceError(f"Repository retrieval failure: {str(e)}") from e

        if not data:
            return None

        try:
            return DecisionAnalysisResult.model_validate(data)
        except Exception as e:
            raise DecisionPersistenceError(f"Deserialization validation failure: {str(e)}") from e
