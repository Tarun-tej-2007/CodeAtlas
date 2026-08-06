"""Architecture Governance Persistence Layer."""

import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from app.governance.exceptions import GovernancePersistenceError, GovernanceValidationError
from app.governance.interfaces import GovernancePersistence
from app.governance.models import (
    ComplianceReport,
    GovernanceAnalysisResult,
    GovernancePolicy,
    GovernanceResult,
    GovernanceViolationReport,
)


class GovernanceRepository(ABC):
    """Abstract repository contract separating database implementation details from governance domain concerns."""

    @abstractmethod
    def save_policy(self, policy_id: uuid.UUID, policy_data: Dict[str, Any]) -> None:
        """Saves policy payload mapping data to database."""
        pass

    @abstractmethod
    def get_policy(self, policy_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Retrieves raw policy payload data from database."""
        pass

    @abstractmethod
    def list_policies(self) -> Tuple[Dict[str, Any], ...]:
        """Lists all raw policies payload data from database."""
        pass

    @abstractmethod
    def update_policy(self, policy_id: uuid.UUID, policy_data: Dict[str, Any]) -> None:
        """Updates mapped policy payload data in database."""
        pass

    @abstractmethod
    def save_result(self, result_id: uuid.UUID, project_id: uuid.UUID, result_data: Dict[str, Any]) -> None:
        """Saves mapped result run data to database."""
        pass

    @abstractmethod
    def get_result(self, result_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Retrieves raw result run data from database."""
        pass

    @abstractmethod
    def list_results(self, project_id: uuid.UUID) -> Tuple[Dict[str, Any], ...]:
        """Lists all raw results data for a project scope from database."""
        pass

    @abstractmethod
    def save_violation_report(self, report_id: uuid.UUID, report_data: Dict[str, Any]) -> None:
        """Saves mapped violation report data to database."""
        pass

    @abstractmethod
    def get_violation_report(self, report_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Retrieves raw violation report data from database."""
        pass

    @abstractmethod
    def save_compliance_report(self, report_id: uuid.UUID, report_data: Dict[str, Any]) -> None:
        """Saves mapped compliance report data to database."""
        pass

    @abstractmethod
    def get_compliance_report(self, report_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Retrieves raw compliance report data from database."""
        pass

    @abstractmethod
    def save_analysis_result(self, result_id: uuid.UUID, result_data: Dict[str, Any]) -> None:
        """Saves complete governance analysis result data to database."""
        pass

    @abstractmethod
    def get_analysis_result(self, result_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Retrieves complete governance analysis result data from database."""
        pass


class GovernancePersistenceService(GovernancePersistence):
    """Concrete persistence service implementing the GovernancePersistence domain contract."""

    def __init__(self, repository: GovernanceRepository) -> None:
        """Initializes service using constructor dependency injection.

        Args:
            repository: Dependency-injected abstract repository for physical database operations.
        """
        if repository is None:
            raise ValueError("GovernanceRepository must not be None.")
        if not isinstance(repository, GovernanceRepository):
            raise TypeError("repository must inherit from GovernanceRepository ABC.")
        self.repository = repository

    def save_policy(self, policy: GovernancePolicy) -> None:
        if policy is None:
            raise GovernanceValidationError("policy must not be None.")
        if not isinstance(policy, GovernancePolicy):
            raise GovernanceValidationError("policy must be a valid GovernancePolicy instance.")

        try:
            self.repository.save_policy(policy.policy_id, policy.model_dump())
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to save policy: {e}") from e

    def get_policy(self, policy_id: uuid.UUID) -> Optional[GovernancePolicy]:
        if policy_id is None or not isinstance(policy_id, uuid.UUID):
            raise GovernanceValidationError("policy_id must be a valid UUID.")

        try:
            data = self.repository.get_policy(policy_id)
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to get policy: {e}") from e

        if data is None:
            return None

        try:
            return GovernancePolicy.model_validate(data)
        except Exception as e:
            raise GovernanceValidationError(f"Invalid persisted policy payload: {e}") from e

    def list_policies(self) -> Tuple[GovernancePolicy, ...]:
        try:
            raw_list = self.repository.list_policies()
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to list policies: {e}") from e

        policies = []
        for item in raw_list:
            try:
                policies.append(GovernancePolicy.model_validate(item))
            except Exception as e:
                raise GovernanceValidationError(f"Invalid persisted policy in list: {e}") from e

        # Sorting deterministically by policy_id
        policies.sort(key=lambda p: str(p.policy_id))
        return tuple(policies)

    def update_policy(self, policy: GovernancePolicy) -> None:
        if policy is None:
            raise GovernanceValidationError("policy must not be None.")
        if not isinstance(policy, GovernancePolicy):
            raise GovernanceValidationError("policy must be a valid GovernancePolicy instance.")

        try:
            # Check if policy exists first to guarantee update semantics
            existing = self.repository.get_policy(policy.policy_id)
            if existing is None:
                raise GovernanceValidationError(f"Policy with ID '{policy.policy_id}' does not exist to update.")
            self.repository.update_policy(policy.policy_id, policy.model_dump())
        except GovernanceValidationError:
            raise
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to update policy: {e}") from e

    def save_result(self, result: GovernanceResult) -> None:
        if result is None:
            raise GovernanceValidationError("result must not be None.")
        if not isinstance(result, GovernanceResult):
            raise GovernanceValidationError("result must be a valid GovernanceResult instance.")

        try:
            self.repository.save_result(result.result_id, result.project_id, result.model_dump())
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to save result: {e}") from e

    def get_result(self, result_id: uuid.UUID) -> Optional[GovernanceResult]:
        if result_id is None or not isinstance(result_id, uuid.UUID):
            raise GovernanceValidationError("result_id must be a valid UUID.")

        try:
            data = self.repository.get_result(result_id)
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to get result: {e}") from e

        if data is None:
            return None

        try:
            return GovernanceResult.model_validate(data)
        except Exception as e:
            raise GovernanceValidationError(f"Invalid persisted result payload: {e}") from e

    def list_results(self, project_id: uuid.UUID) -> Tuple[GovernanceResult, ...]:
        if project_id is None or not isinstance(project_id, uuid.UUID):
            raise GovernanceValidationError("project_id must be a valid UUID.")

        try:
            raw_list = self.repository.list_results(project_id)
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to list results: {e}") from e

        results = []
        for item in raw_list:
            try:
                results.append(GovernanceResult.model_validate(item))
            except Exception as e:
                raise GovernanceValidationError(f"Invalid persisted result payload in list: {e}") from e

        # Sort chronologically by created_at deterministically
        results.sort(key=lambda r: r.created_at)
        return tuple(results)

    def save_violation_report(self, report: GovernanceViolationReport) -> None:
        if report is None:
            raise GovernanceValidationError("report must not be None.")
        if not isinstance(report, GovernanceViolationReport):
            raise GovernanceValidationError("report must be a valid GovernanceViolationReport instance.")

        try:
            self.repository.save_violation_report(report.report_id, report.model_dump())
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to save violation report: {e}") from e

    def get_violation_report(self, report_id: uuid.UUID) -> Optional[GovernanceViolationReport]:
        if report_id is None or not isinstance(report_id, uuid.UUID):
            raise GovernanceValidationError("report_id must be a valid UUID.")

        try:
            data = self.repository.get_violation_report(report_id)
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to get violation report: {e}") from e

        if data is None:
            return None

        try:
            return GovernanceViolationReport.model_validate(data)
        except Exception as e:
            raise GovernanceValidationError(f"Invalid persisted violation report payload: {e}") from e

    def save_compliance_report(self, report: ComplianceReport) -> None:
        if report is None:
            raise GovernanceValidationError("report must not be None.")
        if not isinstance(report, ComplianceReport):
            raise GovernanceValidationError("report must be a valid ComplianceReport instance.")

        try:
            self.repository.save_compliance_report(report.report_id, report.model_dump())
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to save compliance report: {e}") from e

    def get_compliance_report(self, report_id: uuid.UUID) -> Optional[ComplianceReport]:
        if report_id is None or not isinstance(report_id, uuid.UUID):
            raise GovernanceValidationError("report_id must be a valid UUID.")

        try:
            data = self.repository.get_compliance_report(report_id)
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to get compliance report: {e}") from e

        if data is None:
            return None

        try:
            return ComplianceReport.model_validate(data)
        except Exception as e:
            raise GovernanceValidationError(f"Invalid persisted compliance report payload: {e}") from e

    def save_analysis_result(self, result: GovernanceAnalysisResult) -> None:
        if result is None:
            raise GovernanceValidationError("result must not be None.")
        if not isinstance(result, GovernanceAnalysisResult):
            raise GovernanceValidationError("result must be a valid GovernanceAnalysisResult instance.")

        try:
            self.repository.save_analysis_result(result.result_id, result.model_dump())
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to save analysis result: {e}") from e

    def get_analysis_result(self, result_id: uuid.UUID) -> Optional[GovernanceAnalysisResult]:
        if result_id is None or not isinstance(result_id, uuid.UUID):
            raise GovernanceValidationError("result_id must be a valid UUID.")

        try:
            data = self.repository.get_analysis_result(result_id)
        except Exception as e:
            raise GovernancePersistenceError(f"Failed to get analysis result: {e}") from e

        if data is None:
            return None

        try:
            return GovernanceAnalysisResult.model_validate(data)
        except Exception as e:
            raise GovernanceValidationError(f"Invalid persisted analysis result payload: {e}") from e
