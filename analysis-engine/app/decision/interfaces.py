"""Abstract interfaces defining operations for Decision build, traceability, and persistence."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, Tuple

from app.decision.enums import DecisionCategory, DecisionPriority, DecisionStatus
from app.decision.models import (
    ArchitectureDecision,
    DecisionMetadata,
    DecisionRelationship,
    DecisionRequest,
    DecisionTraceGraph,
    DecisionDriftReport,
    DecisionHealthReport,
    DecisionAnalysisResult,
)


class DecisionBuilder(ABC):
    """Abstract interface defining operations for building and normalizing Architecture Decisions."""

    @abstractmethod
    def build_from_request(self, request: DecisionRequest) -> ArchitectureDecision:
        """Constructs and normalizes an ArchitectureDecision from a DecisionRequest.

        Args:
            request: The decision registration request.

        Returns:
            The normalized immutable ArchitectureDecision.

        Raises:
            DecisionValidationError: If validation fails.
        """
        pass

    @abstractmethod
    def build_decision(
        self,
        title: str,
        category: DecisionCategory,
        status: DecisionStatus,
        priority: DecisionPriority,
        context: str,
        decision_text: str,
        consequences: str,
        metadata: DecisionMetadata,
        relationships: Tuple[DecisionRelationship, ...] = (),
    ) -> ArchitectureDecision:
        """Constructs, validates, and normalizes an immutable ArchitectureDecision instance.

        Args:
            title: Decision title.
            category: Domain classification category.
            status: Initial status phase.
            priority: Priority scale.
            context: Problem statement context.
            decision_text: Selected resolution strategy text.
            consequences: Resulting outcomes or trade-offs.
            metadata: Associated author metadata DTO.
            relationships: Set of linked decisions.

        Returns:
            The immutable ArchitectureDecision.

        Raises:
            DecisionValidationError: If validation checks fail.
        """
        pass


class DecisionTraceabilityProvider(ABC):
    """Abstract interface defining capabilities for linking code modules/files to decisions."""

    @abstractmethod
    def trace_decisions(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        decisions: Tuple[ArchitectureDecision, ...],
    ) -> DecisionTraceGraph:
        """Maps codebase file paths/modules back to associated decision identifiers and builds trace graph.

        Args:
            project_id: Unique project tracker.
            commit_id: Baseline target commit hash.
            decisions: Collection of decisions.

        Returns:
            The compiled immutable DecisionTraceGraph DTO.

        Raises:
            DecisionTraceabilityError: If traceability extraction fails.
        """
        pass


class DecisionPersistence(ABC):
    """Abstract interface defining repository persistence contracts for decisions."""

    @abstractmethod
    def save_decision(self, project_id: uuid.UUID, decision: ArchitectureDecision) -> None:
        """Saves an architecture decision to database/repository storage.

        Args:
            project_id: Associated project identifier.
            decision: Target ArchitectureDecision instance.

        Raises:
            DecisionPersistenceError: If repository save fails.
        """
        pass

    @abstractmethod
    def get_decision(self, decision_id: uuid.UUID) -> Optional[ArchitectureDecision]:
        """Retrieves an architecture decision by its unique identifier.

        Args:
            decision_id: Target decision UUID.

        Returns:
            ArchitectureDecision if found, else None.

        Raises:
            DecisionPersistenceError: If query fails.
        """
        pass

    @abstractmethod
    def list_decisions(self, project_id: uuid.UUID) -> Tuple[ArchitectureDecision, ...]:
        """Lists all decisions associated with a project scope.

        Args:
            project_id: Associated project UUID.

        Returns:
            An immutable tuple of decisions.

        Raises:
            DecisionPersistenceError: If query fails.
        """
        pass

    @abstractmethod
    def save_trace_graph(self, project_id: uuid.UUID, graph: DecisionTraceGraph) -> None:
        """Saves a decision trace graph.

        Args:
            project_id: Associated project UUID.
            graph: The trace graph.

        Raises:
            DecisionPersistenceError: If save fails.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def save_drift_report(self, project_id: uuid.UUID, report: DecisionDriftReport) -> None:
        """Saves a decision drift report.

        Args:
            project_id: Associated project UUID.
            report: The drift report.

        Raises:
            DecisionPersistenceError: If save fails.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def save_health_report(self, project_id: uuid.UUID, report: DecisionHealthReport) -> None:
        """Saves a decision health report.

        Args:
            project_id: Associated project UUID.
            report: The health report.

        Raises:
            DecisionPersistenceError: If save fails.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def save_analysis_result(self, project_id: uuid.UUID, result: DecisionAnalysisResult) -> None:
        """Saves a decision analysis result.

        Args:
            project_id: Associated project UUID.
            result: The analysis result.

        Raises:
            DecisionPersistenceError: If save fails.
        """
        pass

    @abstractmethod
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
        pass


class DecisionDriftAnalyzer(ABC):
    """Abstract interface defining capabilities for detecting decision divergence drift."""

    @abstractmethod
    def analyze_drift(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        decisions: Tuple[ArchitectureDecision, ...],
        trace_graph: DecisionTraceGraph,
        dependency_graph: Optional[Any] = None,
        arch_result: Optional[Any] = None,
        governance_result: Optional[Any] = None,
        evolution_result: Optional[Any] = None,
    ) -> DecisionDriftReport:
        """Analyzes divergence between architectural intent and implementation state.

        Args:
            project_id: Associated project identifier.
            commit_id: Associated Git commit hash.
            decisions: Registered decisions to evaluate.
            trace_graph: Traceability graph mapping decisions to code targets.
            dependency_graph: Optional dependency graph output.
            arch_result: Optional architecture analysis result.
            governance_result: Optional governance check result.
            evolution_result: Optional evolution trend result.

        Returns:
            The compiled DecisionDriftReport DTO.

        Raises:
            DecisionValidationError: If inputs are invalid or contradictory.
            DecisionError: For general subsystem failures.
        """
        pass


class DecisionHealthAnalyzer(ABC):
    """Abstract interface defining capabilities for evaluating decision health metrics."""

    @abstractmethod
    def analyze_health(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        decisions: Tuple[ArchitectureDecision, ...],
        drift_report: DecisionDriftReport,
        trace_graph: DecisionTraceGraph,
        evolution_result: Optional[Any] = None,
        governance_result: Optional[Any] = None,
    ) -> DecisionHealthReport:
        """Evaluates health, compliance quality, and document completeness of decisions.

        Args:
            project_id: Associated project identifier.
            commit_id: Associated Git commit hash.
            decisions: Collection of decisions.
            drift_report: Compiled drift analysis report.
            trace_graph: Traceability graph.
            evolution_result: Optional evolution trend result.
            governance_result: Optional governance result.

        Returns:
            The compiled DecisionHealthReport DTO.

        Raises:
            DecisionValidationError: If parameters fail validation.
            DecisionError: For general subsystem failures.
        """
        pass


class DecisionIntelligenceOrchestrator(ABC):
    """Abstract interface for coordinating the complete Architecture Decision Intelligence pipeline."""

    @abstractmethod
    def analyze_project_decisions(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        requests: Tuple[DecisionRequest, ...],
        dependency_graph: Optional[Any] = None,
        arch_result: Optional[Any] = None,
        governance_result: Optional[Any] = None,
        evolution_result: Optional[Any] = None,
        correlation_id: Optional[str] = None,
    ) -> DecisionAnalysisResult:
        """Runs decision compilation, traceability, drift, and health analysis orchestration.

        Args:
            project_id: Unique project scoping ID.
            commit_id: Target commit hash.
            requests: Registered or new decision build requests.
            dependency_graph: Codebase dependency graph.
            arch_result: Quality analyzer outputs.
            governance_result: Active compliance violations.
            evolution_result: Codebase history metrics.

        Returns:
            The immutable compiled DecisionAnalysisResult aggregate payload.

        Raises:
            DecisionValidationError: For invalid workflow parameters.
            DecisionPersistenceError: For database/infrastructure save/load exceptions.
            DecisionTraceabilityError: For traceback resolution failures.
            DecisionError: For general subsystem failures.
        """
        pass


class DecisionRepository(ABC):
    """Abstract interface defining data storage/retrieval operations for serialized decision artifacts."""

    @abstractmethod
    def save_data(self, key: str, data: dict) -> None:
        """Saves a data dictionary under a given key.

        Args:
            key: Target unique storage key string.
            data: Payload dictionary to save.

        Raises:
            Exception: If storage fails.
        """
        pass

    @abstractmethod
    def get_data(self, key: str) -> Optional[dict]:
        """Retrieves a data dictionary by key.

        Args:
            key: Target unique storage key string.

        Returns:
            The data dict if found, else None.

        Raises:
            Exception: If retrieval fails.
        """
        pass

    @abstractmethod
    def list_keys_starting_with(self, prefix: str) -> Tuple[str, ...]:
        """Lists keys matching a given prefix.

        Args:
            prefix: Key prefix to filter by.

        Returns:
            An immutable tuple of matching keys.

        Raises:
            Exception: If list query fails.
        """
        pass
