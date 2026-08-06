"""Abstract interfaces for the Architecture Governance subsystem."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from app.governance.models import (
    ComplianceReport,
    ComplianceScore,
    EnrichedViolation,
    GovernanceAnalysisResult,
    GovernancePolicy,
    GovernanceRequest,
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

    @abstractmethod
    def evaluate_request(self, request: GovernanceRequest) -> GovernanceResult:
        """Evaluates all policies defined in the GovernanceRequest and compiles the final GovernanceResult.

        Args:
            request: Injected GovernanceRequest payload.

        Returns:
            The compiled immutable GovernanceResult.

        Raises:
            GovernanceValidationError: If request parameter is invalid.
            PolicyEvaluationError: If rule execution fails.
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
    def save_violation_report(self, report: GovernanceViolationReport) -> None:
        """Saves an enriched violation report to repository storage.

        Args:
            report: Immutable GovernanceViolationReport domain object.

        Raises:
            GovernancePersistenceError: If repository write fails.
        """
        pass

    @abstractmethod
    def get_violation_report(self, report_id: uuid.UUID) -> Optional[GovernanceViolationReport]:
        """Retrieves an enriched violation report by its unique identifier.

        Args:
            report_id: Unique report identifier.

        Returns:
            GovernanceViolationReport model if found, else None.

        Raises:
            GovernancePersistenceError: If repository query fails.
        """
        pass

    @abstractmethod
    def save_compliance_report(self, report: ComplianceReport) -> None:
        """Saves a compliance score report to repository storage.

        Args:
            report: Immutable ComplianceReport domain object.

        Raises:
            GovernancePersistenceError: If repository write fails.
        """
        pass

    @abstractmethod
    def get_compliance_report(self, report_id: uuid.UUID) -> Optional[ComplianceReport]:
        """Retrieves a compliance score report by its unique identifier.

        Args:
            report_id: Unique report identifier.

        Returns:
            ComplianceReport model if found, else None.

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

    @abstractmethod
    def list_policies(self) -> Tuple[GovernancePolicy, ...]:
        """Lists all registered governance policies.

        Returns:
            An immutable tuple of GovernancePolicy objects.

        Raises:
            GovernancePersistenceError: If repository query fails.
        """
        pass

    @abstractmethod
    def update_policy(self, policy: GovernancePolicy) -> None:
        """Updates an existing governance policy.

        Args:
            policy: The updated GovernancePolicy domain object.

        Raises:
            GovernancePersistenceError: If repository update fails.
        """
        pass

    @abstractmethod
    def save_analysis_result(self, result: GovernanceAnalysisResult) -> None:
        """Saves a complete governance analysis result containing reports and scores.

        Args:
            result: Immutable GovernanceAnalysisResult domain object.

        Raises:
            GovernancePersistenceError: If repository write fails.
        """
        pass

    @abstractmethod
    def get_analysis_result(self, result_id: uuid.UUID) -> Optional[GovernanceAnalysisResult]:
        """Retrieves a complete governance analysis result by its unique identifier.

        Args:
            result_id: Unique analysis result identifier.

        Returns:
            GovernanceAnalysisResult if found, else None.

        Raises:
            GovernancePersistenceError: If repository query fails.
        """
        pass


class GovernanceOrchestrator(ABC):
    """Abstract interface defining the orchestration of governance evaluations."""

    @abstractmethod
    def verify_governance(
        self,
        request: GovernanceRequest,
    ) -> GovernanceAnalysisResult:
        """Orchestrates policy evaluations, violation enrichment, compliance scoring and persistence.

        Args:
            request: The immutable GovernanceRequest detailing project and policies.

        Returns:
            The compiled immutable GovernanceAnalysisResult.

        Raises:
            GovernanceValidationError: If request validation fails.
            GovernanceError: For failures in evaluation, analysis, scoring or persistence.
        """
        pass
