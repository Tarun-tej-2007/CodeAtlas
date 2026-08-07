"""Abstract interfaces defining operations for Decision build, traceability, and persistence."""

import uuid
from abc import ABC, abstractmethod
from typing import Mapping, Optional, Tuple

from app.decision.enums import DecisionCategory, DecisionPriority, DecisionStatus
from app.decision.models import (
    ArchitectureDecision,
    DecisionMetadata,
    DecisionRelationship,
    DecisionRequest,
    DecisionTraceGraph,
    DecisionDriftReport,
    DecisionHealthReport,
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
