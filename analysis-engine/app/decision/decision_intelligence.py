"""Decision intelligence orchestrator orchestrating the complete decision pipeline."""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Tuple

from app.decision.exceptions import DecisionPersistenceError, DecisionTraceabilityError, DecisionValidationError, DecisionError
from app.decision.interfaces import (
    DecisionBuilder,
    DecisionDriftAnalyzer,
    DecisionHealthAnalyzer,
    DecisionIntelligenceOrchestrator,
    DecisionPersistence,
    DecisionTraceabilityProvider,
)
from app.decision.models import (
    ArchitectureDecision,
    DecisionAnalysisResult,
    DecisionDriftReport,
    DecisionHealth,
    DecisionHealthReport,
    DecisionRequest,
    DecisionTraceGraph,
)

logger = logging.getLogger("analysis-engine.decision")


class DecisionIntelligenceService(DecisionIntelligenceOrchestrator):
    """Concrete DecisionIntelligenceOrchestrator coordinating decision compiling, tracing and checks."""

    def __init__(
        self,
        builder: DecisionBuilder,
        traceability_provider: DecisionTraceabilityProvider,
        drift_analyzer: DecisionDriftAnalyzer,
        health_analyzer: DecisionHealthAnalyzer,
        persistence: DecisionPersistence,
    ) -> None:
        """Initializes the orchestrator with required dependencies."""
        if builder is None:
            raise DecisionValidationError("builder must not be None.")
        if traceability_provider is None:
            raise DecisionValidationError("traceability_provider must not be None.")
        if drift_analyzer is None:
            raise DecisionValidationError("drift_analyzer must not be None.")
        if health_analyzer is None:
            raise DecisionValidationError("health_analyzer must not be None.")
        if persistence is None:
            raise DecisionValidationError("persistence must not be None.")

        self.builder = builder
        self.traceability_provider = traceability_provider
        self.drift_analyzer = drift_analyzer
        self.health_analyzer = health_analyzer
        self.persistence = persistence

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
        """Runs decision compilation, traceability, drift, and health analysis orchestration."""
        if project_id is None:
            raise DecisionValidationError("project_id must not be None.")
        if not commit_id or not commit_id.strip():
            raise DecisionValidationError("commit_id must be a non-empty string.")
        if requests is None:
            raise DecisionValidationError("requests collection must not be None.")

        corr_id = correlation_id or str(uuid.uuid4())
        logger.info("[Correlation-ID: %s] Starting decision intelligence orchestration", corr_id)

        from app.decision.cache import execution_cache
        token = execution_cache.set({})

        start_total = time.perf_counter()
        decision_build_ms = 0.0
        traceability_analysis_ms = 0.0
        drift_analysis_ms = 0.0
        health_analysis_ms = 0.0
        persistence_ms = 0.0

        try:
            # 1. Load existing decisions from persistence & build new ones
            logger.info("[Correlation-ID: %s] Stage 1: Compiling decisions", corr_id)
            start_build = time.perf_counter()
            try:
                existing_decisions = self.persistence.list_decisions(project_id)
            except Exception as e:
                logger.error("[Correlation-ID: %s] Compiling decisions infrastructure load exception: %s", corr_id, e)
                raise DecisionPersistenceError(f"Infrastructure exception during list_decisions: {str(e)}") from e

            if existing_decisions is None:
                existing_decisions = ()

            new_decisions = []
            for req in requests:
                if not isinstance(req, DecisionRequest):
                    logger.error("[Correlation-ID: %s] Invalid item in requests collection", corr_id)
                    raise DecisionValidationError("All items in requests must be valid DecisionRequest instances.")
                try:
                    dec = self.builder.build_from_request(req)
                    new_decisions.append(dec)
                except Exception as e:
                    logger.error("[Correlation-ID: %s] Failed to build decision from request: %s", corr_id, e)
                    if isinstance(e, DecisionValidationError):
                        raise e
                    raise DecisionValidationError(f"Failed to build decision from request: {str(e)}") from e

            # Save new decisions
            for dec in new_decisions:
                try:
                    self.persistence.save_decision(project_id, dec)
                except Exception as e:
                    logger.error("[Correlation-ID: %s] Infrastructure exception during save_decision: %s", corr_id, e)
                    raise DecisionPersistenceError(f"Infrastructure exception during save_decision: {str(e)}") from e

            dec_map = {d.decision_id: d for d in existing_decisions}
            for dec in new_decisions:
                dec_map[dec.decision_id] = dec

            sorted_decisions = tuple(
                sorted(dec_map.values(), key=lambda d: str(d.decision_id))
            )
            decision_build_ms = (time.perf_counter() - start_build) * 1000.0

            # Short-circuit if no decisions exist in repository
            if not sorted_decisions:
                logger.info("[Correlation-ID: %s] No decisions exist in repository, executing short-circuit output path", corr_id)
                trace_graph = DecisionTraceGraph(
                    project_id=project_id,
                    commit_id=commit_id.strip(),
                    links=(),
                    links_by_target={},
                    links_by_decision={},
                )
                drift_report = DecisionDriftReport(
                    project_id=project_id,
                    commit_id=commit_id.strip(),
                    drifts=(),
                    drifts_by_classification={},
                    extra_info={},
                )
                health = DecisionHealth(
                    overall_score=100.0,
                    category_scores={
                        "alignment": 100.0,
                        "completeness": 100.0,
                        "freshness": 100.0,
                        "traceability": 100.0,
                    },
                    classification="Excellent",
                    recommendations=(),
                    metrics={
                        "total_decisions": 0,
                        "stale_decisions": 0,
                        "orphaned_decisions": 0,
                        "drifted_decisions": 0,
                        "governance_conflicts": 0,
                        "inconsistent_lifecycle": 0,
                        "undocumented_fields": 0,
                    },
                )
                health_report = DecisionHealthReport(
                    project_id=project_id,
                    commit_id=commit_id.strip(),
                    health=health,
                    extra_info={},
                )

                start_persist = time.perf_counter()
                try:
                    self.persistence.save_trace_graph(project_id, trace_graph)
                    self.persistence.save_drift_report(project_id, drift_report)
                    self.persistence.save_health_report(project_id, health_report)
                except Exception as e:
                    logger.error("[Correlation-ID: %s] Persistence save failure during short-circuit: %s", corr_id, e)
                    raise DecisionPersistenceError(f"Infrastructure save failure during short-circuit: {str(e)}") from e
                persistence_ms += (time.perf_counter() - start_persist) * 1000.0

                total_ms = (time.perf_counter() - start_total) * 1000.0
                extra_info = {
                    "correlation_id": corr_id,
                    "metrics": {
                        "decision_build_ms": decision_build_ms,
                        "traceability_analysis_ms": traceability_analysis_ms,
                        "drift_analysis_ms": drift_analysis_ms,
                        "health_analysis_ms": health_analysis_ms,
                        "persistence_ms": persistence_ms,
                        "total_orchestration_ms": total_ms,
                    }
                }

                result = DecisionAnalysisResult(
                    project_id=project_id,
                    commit_id=commit_id.strip(),
                    decisions=(),
                    trace_graph=trace_graph,
                    drift_report=drift_report,
                    health_report=health_report,
                    processed_at=datetime.now(timezone.utc),
                    extra_info=extra_info,
                )

                start_result_persist = time.perf_counter()
                try:
                    self.persistence.save_analysis_result(project_id, result)
                except Exception as e:
                    logger.error("[Correlation-ID: %s] Analysis result save failure during short-circuit: %s", corr_id, e)
                    raise DecisionPersistenceError(f"Infrastructure save failure for analysis result during short-circuit: {str(e)}") from e
                persistence_ms += (time.perf_counter() - start_result_persist) * 1000.0

                extra_info["metrics"]["persistence_ms"] = persistence_ms
                extra_info["metrics"]["total_orchestration_ms"] = (time.perf_counter() - start_total) * 1000.0

                return result

            # 2. Traceability Graph Analysis
            logger.info("[Correlation-ID: %s] Stage 2: Traceability Graph Analysis", corr_id)
            start_trace = time.perf_counter()
            try:
                trace_graph = self.traceability_provider.trace_decisions(
                    project_id, commit_id, sorted_decisions
                )
            except Exception as e:
                logger.error("[Correlation-ID: %s] Traceability extraction exception: %s", corr_id, e)
                if isinstance(e, DecisionTraceabilityError):
                    raise e
                raise DecisionTraceabilityError(f"Traceability extraction exception: {str(e)}") from e
            traceability_analysis_ms = (time.perf_counter() - start_trace) * 1000.0

            # 3. Drift Mismatch Checks
            logger.info("[Correlation-ID: %s] Stage 3: Drift analysis checks", corr_id)
            start_drift = time.perf_counter()
            try:
                drift_report = self.drift_analyzer.analyze_drift(
                    project_id,
                    commit_id,
                    sorted_decisions,
                    trace_graph,
                    dependency_graph,
                    arch_result,
                    governance_result,
                    evolution_result,
                )
            except Exception as e:
                logger.error("[Correlation-ID: %s] Drift analysis exception: %s", corr_id, e)
                if isinstance(e, DecisionValidationError):
                    raise e
                raise DecisionValidationError(f"Drift analysis exception: {str(e)}") from e
            drift_analysis_ms = (time.perf_counter() - start_drift) * 1000.0

            # 4. Health and Quality Checks
            logger.info("[Correlation-ID: %s] Stage 4: Health and quality checks", corr_id)
            start_health = time.perf_counter()
            try:
                health_report = self.health_analyzer.analyze_health(
                    project_id,
                    commit_id,
                    sorted_decisions,
                    drift_report,
                    trace_graph,
                    evolution_result,
                    governance_result,
                )
            except Exception as e:
                logger.error("[Correlation-ID: %s] Health analysis exception: %s", corr_id, e)
                if isinstance(e, DecisionValidationError):
                    raise e
                raise DecisionValidationError(f"Health analysis exception: {str(e)}") from e
            health_analysis_ms = (time.perf_counter() - start_health) * 1000.0

            # 5. Persist reports
            logger.info("[Correlation-ID: %s] Stage 5: Saving reports to persistence", corr_id)
            start_persist = time.perf_counter()
            try:
                self.persistence.save_trace_graph(project_id, trace_graph)
                self.persistence.save_drift_report(project_id, drift_report)
                self.persistence.save_health_report(project_id, health_report)
            except Exception as e:
                logger.error("[Correlation-ID: %s] Infrastructure save failure for reports: %s", corr_id, e)
                raise DecisionPersistenceError(f"Infrastructure save failure for reports: {str(e)}") from e
            persistence_ms += (time.perf_counter() - start_persist) * 1000.0

            total_ms = (time.perf_counter() - start_total) * 1000.0
            extra_info = {
                "correlation_id": corr_id,
                "metrics": {
                    "decision_build_ms": decision_build_ms,
                    "traceability_analysis_ms": traceability_analysis_ms,
                    "drift_analysis_ms": drift_analysis_ms,
                    "health_analysis_ms": health_analysis_ms,
                    "persistence_ms": persistence_ms,
                    "total_orchestration_ms": total_ms,
                }
            }

            result = DecisionAnalysisResult(
                project_id=project_id,
                commit_id=commit_id.strip(),
                decisions=sorted_decisions,
                trace_graph=trace_graph,
                drift_report=drift_report,
                health_report=health_report,
                processed_at=datetime.now(timezone.utc),
                extra_info=extra_info,
            )

            # Persist aggregate analysis result
            start_result_persist = time.perf_counter()
            try:
                self.persistence.save_analysis_result(project_id, result)
            except Exception as e:
                logger.error("[Correlation-ID: %s] Infrastructure save failure for analysis result: %s", corr_id, e)
                raise DecisionPersistenceError(f"Infrastructure save failure for analysis result: {str(e)}") from e
            persistence_ms += (time.perf_counter() - start_result_persist) * 1000.0

            extra_info["metrics"]["persistence_ms"] = persistence_ms
            extra_info["metrics"]["total_orchestration_ms"] = (time.perf_counter() - start_total) * 1000.0

            logger.info("[Correlation-ID: %s] Decision intelligence orchestration successfully completed", corr_id)
            return result
        except (DecisionPersistenceError, DecisionTraceabilityError, DecisionValidationError) as e:
            logger.error("[Correlation-ID: %s] Orchestration execution failure: %s", corr_id, e)
            raise
        except Exception as e:
            logger.error("[Correlation-ID: %s] Orchestration execution unexpected failure: %s", corr_id, e)
            raise DecisionError(f"Unexpected error during decision intelligence orchestration: {e}") from e
        finally:
            execution_cache.reset(token)
            logger.info("[Correlation-ID: %s] Disposed execution cache context", corr_id)
