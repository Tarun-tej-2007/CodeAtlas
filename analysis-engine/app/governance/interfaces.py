"""Abstract interfaces for the Architecture Governance subsystem."""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from app.governance.models import (
    ComplianceReport,
    ComplianceScore,
    EnrichedViolation,
    GovernancePolicy,
    GovernanceResult,
    GovernanceViolationReport,
    PolicyRule,
    PolicyViolation,
)


class ComplianceScorer(ABC):
    """Abstract interface defining compliance scoring computations."""

    @abstractmethod
    def calculate_compliance(
        self,
        violation_report: GovernanceViolationReport,
        history: Optional[Tuple[Any, ...]] = None,
    ) -> ComplianceReport:
        """Computes compliance metrics scoring from the GovernanceViolationReport.

        Args:
            violation_report: Enriched GovernanceViolationReport input.
            history: Optional trailing historical trend context list to adjust score.

        Returns:
            The compiled ComplianceReport DTO.

        Raises:
            GovernanceValidationError: If validation checks fail.
        """
        pass


class ViolationAnalyzer(ABC):
    """Abstract interface defining operations for analyzing policy violation items."""

    @abstractmethod
    def analyze_violations(
        self,
        project_id: uuid.UUID,
        commit_id: str,
        violations: Tuple[PolicyViolation, ...],
    ) -> GovernanceViolationReport:
        """Analyzes a collection of PolicyViolation objects, enriching them with governance diagnostics.

        Args:
            project_id: Associated project scope identifier.
            commit_id: Git commit hash identifier representing target codebase state.
            violations: Immutable tuple of raw PolicyViolation objects.

        Returns:
            The compiled immutable GovernanceViolationReport.

        Raises:
            GovernanceValidationError: If validation fails or inconsistency is detected.
        """
        pass


class PolicyRuleEvaluator(ABC):
    """Abstract interface defining operations for rule evaluation engines."""

    @abstractmethod
    def evaluate_rule(self, commit_id: str, rule: PolicyRule) -> Tuple[PolicyViolation, ...]:
        """Evaluates a single policy rule against codebase structure at the given commit.

        Args:
            commit_id: Git commit hash identifier representing target code point.
            rule: Injected PolicyRule domain model.

        Returns:
            An immutable tuple of PolicyViolation items.

        Raises:
            PolicyEvaluationError: If rule evaluation fails during execution.
        """
        pass


class GovernancePersistence(ABC):
    """Abstract interface defining repository persistence contracts for governance data."""

    @abstractmethod
    def save_result(self, result: GovernanceResult) -> None:
        """Saves a governance verification run result to repository storage.

        Args:
            result: Immutable GovernanceResult domain object.

        Raises:
            GovernancePersistenceError: If repository write fails.
        """
        pass

    @abstractmethod
    def get_result(self, result_id: uuid.UUID) -> Optional[GovernanceResult]:
        """Retrieves a governance verification run result by its unique identifier.

        Args:
            result_id: Unique result identifier.

        Returns:
            GovernanceResult model if found, else None.

        Raises:
            GovernancePersistenceError: If repository query fails.
        """
        pass

    @abstractmethod
    def list_results(self, project_id: uuid.UUID) -> Tuple[GovernanceResult, ...]:
        """Lists all historical governance verification results for a project scope.

        Args:
            project_id: Project scope identifier.

        Returns:
            An immutable tuple of GovernanceResult items.

        Raises:
            GovernancePersistenceError: If repository query fails.
        """
        pass

    @abstractmethod
    def save_policy(self, policy: GovernancePolicy) -> None:
        """Saves a governance policy to repository storage.

        Args:
            policy: Immutable GovernancePolicy domain object.

        Raises:
            GovernancePersistenceError: If repository write fails.
        """
        pass

    @abstractmethod
    def get_policy(self, policy_id: uuid.UUID) -> Optional[GovernancePolicy]:
        """Retrieves a governance policy by its unique identifier.

        Args:
            policy_id: Unique policy identifier.

        Returns:
            GovernancePolicy model if found, else None.

        Raises:
            GovernancePersistenceError: If repository query fails.
        """
        pass
