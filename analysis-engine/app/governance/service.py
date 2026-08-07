"""Governance service implementation coordinating definitions, evaluations, and compliance scoring."""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple

from app.governance.enums import GovernanceStatus, ViolationSeverity
from app.governance.exceptions import (
    GovernanceError,
    GovernanceValidationError,
    PolicyEvaluationError,
    GovernancePersistenceError,
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

logger = logging.getLogger("analysis-engine.governance")


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

        corr_id = request.correlation_id or str(uuid.uuid4())
        logger.info("[Correlation-ID: %s] Starting architecture governance validation for project: %s", corr_id, request.project_name)

        from app.governance.cache import execution_cache
        token = execution_cache.set({})

        start_total = time.perf_counter()
        policy_evaluation_ms = 0.0
        violation_analysis_ms = 0.0
        compliance_scoring_ms = 0.0
        persistence_ms = 0.0

        try:
            # 1. Evaluate policies to obtain raw violations
            logger.info("[Correlation-ID: %s] Stage 1: Evaluating policy rules", corr_id)
            start_eval = time.perf_counter()
            try:
                eval_result = self.policy_evaluator.evaluate_request(request)
            except GovernanceError as ge:
                logger.error("[Correlation-ID: %s] Policy evaluation domain failure: %s", corr_id, ge)
                raise
            except Exception as e:
                logger.error("[Correlation-ID: %s] Unexpected policy evaluation failure: %s", corr_id, e)
                raise PolicyEvaluationError(f"Unexpected error during policy evaluation: {e}") from e
            policy_evaluation_ms = (time.perf_counter() - start_eval) * 1000.0

            # Fail-fast checks on evaluation result DTO
            if not isinstance(eval_result, GovernanceResult):
                logger.error("[Correlation-ID: %s] Evaluator returned invalid non-GovernanceResult object.", corr_id)
                raise GovernanceValidationError(
                    "policy_evaluator returned an invalid non-GovernanceResult object."
                )

            # 2. Downstream violation analysis
            # SHORT-CIRCUIT PATH: if there are no violations, bypass violation analyzer execution
            if not eval_result.violations:
                logger.info("[Correlation-ID: %s] Stage 2: No violations detected, skipping violation analyzer execution", corr_id)
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
                logger.info("[Correlation-ID: %s] Stage 2: Enriching %d raw policy violations", corr_id, len(eval_result.violations))
                start_analysis = time.perf_counter()
                try:
                    violation_report = self.violation_analyzer.analyze_violations(
                        project_id=request.project_id,
                        commit_id=request.commit_id,
                        violations=eval_result.violations,
                    )
                except GovernanceError as ge:
                    logger.error("[Correlation-ID: %s] Violation analysis domain failure: %s", corr_id, ge)
                    raise
                except Exception as e:
                    logger.error("[Correlation-ID: %s] Unexpected violation analysis failure: %s", corr_id, e)
                    raise PolicyEvaluationError(f"Unexpected error during violation analysis: {e}") from e
                violation_analysis_ms = (time.perf_counter() - start_analysis) * 1000.0

            # 3. Retrieve historical result context for trend-aware compliance scoring
            logger.info("[Correlation-ID: %s] Stage 3: Loading historical run metrics", corr_id)
            history = None
            if self.persistence is not None:
                start_hist_load = time.perf_counter()
                try:
                    history = self.persistence.list_results(request.project_id)
                except Exception as e:
                    logger.warning("[Correlation-ID: %s] Failed to load historical context: %s. Continuing without history.", corr_id, e)
                    history = None
                persistence_ms += (time.perf_counter() - start_hist_load) * 1000.0

            # 4. Calculate compliance scoring and report
            logger.info("[Correlation-ID: %s] Stage 4: Calculating compliance scoring metrics", corr_id)
            start_score = time.perf_counter()
            try:
                compliance_report = self.compliance_scorer.calculate_compliance(
                    violation_report=violation_report,
                    history=history,
                )
            except GovernanceError as ge:
                logger.error("[Correlation-ID: %s] Compliance scoring domain failure: %s", corr_id, ge)
                raise
            except Exception as e:
                logger.error("[Correlation-ID: %s] Unexpected compliance scoring failure: %s", corr_id, e)
                raise PolicyEvaluationError(f"Unexpected error during compliance scoring calculation: {e}") from e
            compliance_scoring_ms = (time.perf_counter() - start_score) * 1000.0

            # 5. Persist run outputs to the repository/database (if persistence component is injected)
            if self.persistence is not None:
                logger.info("[Correlation-ID: %s] Stage 5: Saving governance analysis outputs to persistence", corr_id)
                start_persist = time.perf_counter()
                try:
                    self.persistence.save_result(eval_result)
                    self.persistence.save_violation_report(violation_report)
                    self.persistence.save_compliance_report(compliance_report)
                except Exception as e:
                    logger.error("[Correlation-ID: %s] Persistence save operation failed: %s", corr_id, e)
                    raise GovernancePersistenceError(f"Persistence layer failed to save governance run data: {e}") from e
                persistence_ms += (time.perf_counter() - start_persist) * 1000.0

            total_ms = (time.perf_counter() - start_total) * 1000.0
            logger.info("[Correlation-ID: %s] Architecture governance verification completed in %.2fms", corr_id, total_ms)

            extra_info = {
                "correlation_id": corr_id,
                "metrics": {
                    "policy_definition_ms": 0.0,  # Measured at creation time, placeholder inside orchestrator
                    "policy_evaluation_ms": policy_evaluation_ms,
                    "violation_analysis_ms": violation_analysis_ms,
                    "compliance_scoring_ms": compliance_scoring_ms,
                    "persistence_ms": persistence_ms,
                    "total_ms": total_ms,
                }
            }

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
                extra_info=extra_info,
            )
        finally:
            execution_cache.reset(token)
            logger.debug("[Correlation-ID: %s] Disposed execution cache context.", corr_id)
