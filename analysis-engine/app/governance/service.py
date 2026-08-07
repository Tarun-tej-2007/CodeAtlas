"""Governance service implementation coordinating definitions, evaluations, and compliance scoring."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple

from app.governance.enums import GovernanceStatus, ViolationSeverity
from app.governance.exceptions import (
    GovernanceError,
    GovernanceValidationError,
    PolicyEvaluationError,
)
from app.governance.interfaces import (
    ComplianceScorer,
    GovernanceOrchestrator,
    GovernancePersistence,
    PolicyRuleEvaluator,
    ViolationAnalyzer,
)
from app.governance.models import (
    GovernanceAnalysisResult,
    GovernancePolicy,
    GovernanceRequest,
    GovernanceResult,
    GovernanceViolationReport,
)


class GovernanceService(GovernanceOrchestrator):
    """Concrete GovernanceOrchestrator service executing end-to-end architecture governance workflows."""

    def __init__(
        self,
        policy_evaluator: PolicyRuleEvaluator,
        violation_analyzer: ViolationAnalyzer,
        compliance_scorer: ComplianceScorer,
        persistence: Optional[GovernancePersistence] = None,
    ) -> None:
        """Initializes the GovernanceService with injected components.

        Args:
            policy_evaluator: Component evaluating rules to locate raw violations.
            violation_analyzer: Component enriching raw violations into diagnostic reports.
            compliance_scorer: Component computing compliance scores and trends.
            persistence: Optional persistence repository component for saving/loading results.
        """
        if policy_evaluator is None:
            raise ValueError("policy_evaluator must not be None.")
        if not isinstance(policy_evaluator, PolicyRuleEvaluator):
            raise TypeError("policy_evaluator must inherit from PolicyRuleEvaluator.")

        if violation_analyzer is None:
            raise ValueError("violation_analyzer must not be None.")
        if not isinstance(violation_analyzer, ViolationAnalyzer):
            raise TypeError("violation_analyzer must inherit from ViolationAnalyzer.")

        if compliance_scorer is None:
            raise ValueError("compliance_scorer must not be None.")
        if not isinstance(compliance_scorer, ComplianceScorer):
            raise TypeError("compliance_scorer must inherit from ComplianceScorer.")

        if persistence is not None and not isinstance(persistence, GovernancePersistence):
            raise TypeError("persistence must inherit from GovernancePersistence.")

        self.policy_evaluator = policy_evaluator
        self.violation_analyzer = violation_analyzer
        self.compliance_scorer = compliance_scorer
        self.persistence = persistence

    def verify_governance(
        self,
        request: GovernanceRequest,
    ) -> GovernanceAnalysisResult:
        """Orchestrates policy evaluations, violation enrichment, scoring and persistence.

        Args:
            request: The immutable GovernanceRequest detailing the project and policies.

        Returns:
            The compiled immutable GovernanceAnalysisResult.

        Raises:
            GovernanceValidationError: If request validation fails.
            GovernanceError: For failures in evaluation, analysis, scoring or persistence.
        """
        if request is None:
            raise GovernanceValidationError("request must not be None.")
        if not isinstance(request, GovernanceRequest):
            raise GovernanceValidationError("request must be a valid GovernanceRequest instance.")

        # Fail-fast validation of policies list contents
        for idx, policy in enumerate(request.policies):
            if not isinstance(policy, GovernancePolicy):
                raise GovernanceValidationError(
                    f"Policy at index {idx} is not a valid GovernancePolicy instance."
                )

        from app.governance.cache import execution_cache
        token = execution_cache.set({})

        try:
            # 1. Evaluate policies to obtain raw violations
            try:
                eval_result = self.policy_evaluator.evaluate_request(request)
            except GovernanceError:
                raise
            except Exception as e:
                raise PolicyEvaluationError(f"Unexpected error during policy evaluation: {e}") from e

            # Fail-fast checks on evaluation result DTO
            if not isinstance(eval_result, GovernanceResult):
                raise GovernanceValidationError(
                    "policy_evaluator returned an invalid non-GovernanceResult object."
                )

            # 2. Downstream violation analysis
            # SHORT-CIRCUIT PATH: if there are no violations, bypass violation analyzer execution
            if not eval_result.violations:
                violation_report = GovernanceViolationReport(
                    report_id=uuid.uuid4(),
                    project_id=request.project_id,
                    commit_id=request.commit_id,
                    generated_at=datetime.now(timezone.utc),
                    violations=(),
                    violations_by_rule={},
                    violations_by_severity={
                        ViolationSeverity.ERROR.value: 0,
                        ViolationSeverity.WARNING.value: 0,
                        ViolationSeverity.INFO.value: 0,
                    },
                    extra_info={},
                )
            else:
                try:
                    violation_report = self.violation_analyzer.analyze_violations(
                        project_id=request.project_id,
                        commit_id=request.commit_id,
                        violations=eval_result.violations,
                    )
                except GovernanceError:
                    raise
                except Exception as e:
                    raise PolicyEvaluationError(f"Unexpected error during violation analysis: {e}") from e

            # 3. Retrieve historical result context for trend-aware compliance scoring
            history = None
            if self.persistence is not None:
                try:
                    history = self.persistence.list_results(request.project_id)
                except Exception as e:
                    # Defensive programming: log and fallback to None history so scoring can continue
                    history = None

            # 4. Calculate compliance scoring and report
            try:
                compliance_report = self.compliance_scorer.calculate_compliance(
                    violation_report=violation_report,
                    history=history,
                )
            except GovernanceError:
                raise
            except Exception as e:
                raise PolicyEvaluationError(f"Unexpected error during compliance scoring calculation: {e}") from e

            # 5. Persist run outputs to the repository/database (if persistence component is injected)
            if self.persistence is not None:
                try:
                    self.persistence.save_result(eval_result)
                    self.persistence.save_violation_report(violation_report)
                    self.persistence.save_compliance_report(compliance_report)
                except Exception as e:
                    # Defensive programming: raise as GovernancePersistenceError to report write failure
                    from app.governance.exceptions import GovernancePersistenceError
                    raise GovernancePersistenceError(f"Persistence layer failed to save governance run data: {e}") from e

            # 6. Return the compiled immutable GovernanceAnalysisResult DTO representing the complete assessment
            return GovernanceAnalysisResult(
                result_id=uuid.uuid4(),
                project_id=request.project_id,
                commit_id=request.commit_id,
                status=eval_result.status,
                evaluation_result=eval_result,
                violation_report=violation_report,
                compliance_report=compliance_report,
                created_at=datetime.now(timezone.utc),
                extra_info={},
            )
        finally:
            execution_cache.reset(token)
