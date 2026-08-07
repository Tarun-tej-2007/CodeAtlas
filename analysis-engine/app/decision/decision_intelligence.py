"""Decision intelligence orchestrator orchestrating the complete decision pipeline."""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Tuple

from app.decision.exceptions import DecisionPersistenceError, DecisionTraceabilityError, DecisionValidationError
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


class DecisionIntelligenceService(DecisionIntelligenceOrchestrator):
    """Concrete DecisionIntelligenceOrchestrator implementation coordinating build, trace, drift and health stages."""

    def __init__(
        self,
        builder: DecisionBuilder,
        traceability_provider: DecisionTraceabilityProvider,
        drift_analyzer: DecisionDriftAnalyzer,
        health_analyzer: DecisionHealthAnalyzer,
        persistence: DecisionPersistence,
    ) -> None:
        """Initializes decision intelligence service using constructor dependency injection."""
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
        if project_id is None:
            raise DecisionValidationError("project_id must not be None.")
        if not commit_id or not commit_id.strip():
            raise DecisionValidationError("commit_id must be a non-empty string.")
        if requests is None:
            raise DecisionValidationError("requests collection must not be None.")

        # 1. Load existing decisions from persistence
        try:
            existing_decisions = self.persistence.list_decisions(project_id)
        except Exception as e:
            raise DecisionPersistenceError(f"Infrastructure exception during list_decisions: {str(e)}") from e

        # Ensure we got a tuple
        if existing_decisions is None:
            existing_decisions = ()

        # 2. Build new decisions from request collection
        new_decisions = []
        for req in requests:
            if not isinstance(req, DecisionRequest):
                raise DecisionValidationError("All items in requests must be valid DecisionRequest instances.")
            try:
                dec = self.builder.build_from_request(req)
                new_decisions.append(dec)
            except Exception as e:
                # Pass validation errors directly
                if isinstance(e, DecisionValidationError):
                    raise e
                raise DecisionValidationError(f"Failed to build decision from request: {str(e)}") from e

        # 3. Save newly created decisions to persistence
        for dec in new_decisions:
            try:
                self.persistence.save_decision(project_id, dec)
            except Exception as e:
                raise DecisionPersistenceError(f"Infrastructure exception during save_decision: {str(e)}") from e

        # 4. Merge existing and new decisions, ensuring uniqueness and sorting deterministically
        dec_map = {d.decision_id: d for d in existing_decisions}
        for dec in new_decisions:
            dec_map[dec.decision_id] = dec

        sorted_decisions = tuple(
            sorted(dec_map.values(), key=lambda d: str(d.decision_id))
        )

        # 5. Short-circuit if no decisions exist in repository
        if not sorted_decisions:
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

            return DecisionAnalysisResult(
                project_id=project_id,
                commit_id=commit_id.strip(),
                decisions=(),
                trace_graph=trace_graph,
                drift_report=drift_report,
                health_report=health_report,
                processed_at=datetime.now(timezone.utc),
            )

        # 6. Traceability Graph Analysis
        try:
            trace_graph = self.traceability_provider.trace_decisions(
                project_id, commit_id, sorted_decisions
            )
        except Exception as e:
            if isinstance(e, DecisionTraceabilityError):
                raise e
            raise DecisionTraceabilityError(f"Traceability extraction exception: {str(e)}") from e

        # 7. Drift Mismatch Checks
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
            if isinstance(e, DecisionValidationError):
                raise e
            raise DecisionValidationError(f"Drift analysis exception: {str(e)}") from e

        # 8. Health and Quality Checks
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
            if isinstance(e, DecisionValidationError):
                raise e
            raise DecisionValidationError(f"Health analysis exception: {str(e)}") from e

        return DecisionAnalysisResult(
            project_id=project_id,
            commit_id=commit_id.strip(),
            decisions=sorted_decisions,
            trace_graph=trace_graph,
            drift_report=drift_report,
            health_report=health_report,
            processed_at=datetime.now(timezone.utc),
        )
