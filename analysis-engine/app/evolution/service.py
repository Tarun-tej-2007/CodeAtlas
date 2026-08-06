"""Orchestration service layer for Architecture Evolution."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple

import logging
import time
from app.evolution.enums import ArchitecturalChangeType, EvolutionStatus
from app.evolution.exceptions import (
    EvolutionValidationError,
    EvolutionPersistenceError,
    EvolutionFileSystemError,
)

logger = logging.getLogger("analysis-engine.evolution")
from app.evolution.interfaces import (
    ArchitectureSnapshotCalculator,
    EvolutionDifferenceEngine,
    EvolutionPersistence,
    RiskAnalyzer,
    TrendAnalyzer,
)
from app.evolution.models import (
    ArchitecturalChange,
    ArchitectureEvolutionResult,
    ArchitectureSnapshot,
    EvolutionMetadata,
    EvolutionRequest,
    EvolutionResult,
    EvolutionSummary,
)


class ArchitectureEvolutionService:
    """Stateless service coordinating architecture snapshot compilation, diff comparisons, trends, and risk analysis."""

    def __init__(
        self,
        snapshot_calculator: ArchitectureSnapshotCalculator,
        difference_engine: EvolutionDifferenceEngine,
        trend_analyzer: TrendAnalyzer,
        risk_analyzer: RiskAnalyzer,
        persistence: EvolutionPersistence,
    ) -> None:
        """Initializes orchestrator service using constructor dependency injection.

        Args:
            snapshot_calculator: Injected snapshot calculator.
            difference_engine: Injected difference comparisons engine.
            trend_analyzer: Injected historical trends calculator.
            risk_analyzer: Injected structural risk calculator.
            persistence: Injected evolution repository manager.
        """
        if any(
            arg is None
            for arg in (snapshot_calculator, difference_engine, trend_analyzer, risk_analyzer, persistence)
        ):
            raise ValueError("All orchestrator dependencies must not be None.")

        if not isinstance(snapshot_calculator, ArchitectureSnapshotCalculator):
            raise TypeError("snapshot_calculator must inherit from ArchitectureSnapshotCalculator.")
        if not isinstance(difference_engine, EvolutionDifferenceEngine):
            raise TypeError("difference_engine must inherit from EvolutionDifferenceEngine.")
        if not isinstance(trend_analyzer, TrendAnalyzer):
            raise TypeError("trend_analyzer must inherit from TrendAnalyzer.")
        if not isinstance(risk_analyzer, RiskAnalyzer):
            raise TypeError("risk_analyzer must inherit from RiskAnalyzer.")
        if not isinstance(persistence, EvolutionPersistence):
            raise TypeError("persistence must inherit from EvolutionPersistence.")

        self.snapshot_calculator = snapshot_calculator
        self.difference_engine = difference_engine
        self.trend_analyzer = trend_analyzer
        self.risk_analyzer = risk_analyzer
        self.persistence = persistence

    def evolve_architecture(self, request: EvolutionRequest) -> ArchitectureEvolutionResult:
        """Runs the complete evolution analysis orchestration.

        Args:
            request: EvolutionRequest parameters context.

        Returns:
            The compiled ArchitectureEvolutionResult DTO.

        Raises:
            EvolutionValidationError: If any validation checks or engine operations fail.
            EvolutionPersistenceError: If database operations fail.
            EvolutionFileSystemError: If filesystem/builder operations fail.
        """
        if request is None or not isinstance(request, EvolutionRequest):
            raise EvolutionValidationError("request parameter must be a valid EvolutionRequest.")

        corr_id = request.correlation_id or str(uuid.uuid4())
        logger.info("[Correlation-ID: %s] Starting architecture evolution analysis for project: %s", corr_id, request.project_name)

        from app.evolution.cache import execution_cache
        token = execution_cache.set({})

        start_total = time.perf_counter()
        snapshot_generation_ms = 0.0
        architecture_comparison_ms = 0.0
        trend_analysis_ms = 0.0
        risk_analysis_ms = 0.0
        persistence_ms = 0.0

        try:
            # 1. Build current target snapshot
            logger.info("[Correlation-ID: %s] Stage 1: Building snapshot for target commit: %s", corr_id, request.target_commit)
            start_snap = time.perf_counter()
            try:
                current_snapshot = self.snapshot_calculator.calculate_snapshot(request.target_commit)
            except Exception as e:
                logger.error("[Correlation-ID: %s] Snapshot building failed: %s", corr_id, e)
                raise EvolutionFileSystemError(f"Snapshot building failed: {e}") from e
            snapshot_generation_ms = (time.perf_counter() - start_snap) * 1000.0

            # 2. Retrieve previous source snapshot from persistence
            logger.info("[Correlation-ID: %s] Stage 2: Retrieving snapshot for source commit: %s", corr_id, request.source_commit)
            start_persist = time.perf_counter()
            try:
                previous_snapshot = self.persistence.get_snapshot(request.source_commit)
            except Exception as e:
                logger.error("[Correlation-ID: %s] Database retrieval failed for snapshot: %s", corr_id, e)
                raise EvolutionPersistenceError(
                    f"Failed to retrieve source snapshot for '{request.source_commit}': {e}"
                ) from e
            persistence_ms += (time.perf_counter() - start_persist) * 1000.0

            # 3. Compare snapshots
            logger.info("[Correlation-ID: %s] Stage 3: Comparing snapshots", corr_id)
            start_compare = time.perf_counter()
            if previous_snapshot is None:
                logger.info("[Correlation-ID: %s] Baseline snapshot not found in database. Performing first-time evolution.", corr_id)
                empty_snapshot = ArchitectureSnapshot(
                    snapshot_id=uuid.uuid4(),
                    commit_id=request.source_commit,
                    timestamp=datetime.now(timezone.utc),
                    layers=(),
                    components={},
                )
                try:
                    changes = self.difference_engine.diff_snapshots(empty_snapshot, current_snapshot)
                except Exception as e:
                    logger.error("[Correlation-ID: %s] Snapshot comparison failed: %s", corr_id, e)
                    raise EvolutionValidationError(f"Snapshot comparison failed: {e}") from e
            else:
                try:
                    changes = self.difference_engine.diff_snapshots(previous_snapshot, current_snapshot)
                except Exception as e:
                    logger.error("[Correlation-ID: %s] Snapshot comparison failed: %s", corr_id, e)
                    raise EvolutionValidationError(f"Snapshot comparison failed: {e}") from e
            architecture_comparison_ms = (time.perf_counter() - start_compare) * 1000.0

            # 4. Count change categories
            added_count = 0
            removed_count = 0
            modified_count = 0
            unchanged_count = 0

            for cf in changes:
                if cf.change_type == ArchitecturalChangeType.ADDED:
                    added_count += 1
                elif cf.change_type == ArchitecturalChangeType.REMOVED:
                    removed_count += 1
                elif cf.change_type == ArchitecturalChangeType.MODIFIED:
                    modified_count += 1
                elif cf.change_type == ArchitecturalChangeType.UNCHANGED:
                    unchanged_count += 1

            summary = EvolutionSummary(
                added_count=added_count,
                removed_count=removed_count,
                modified_count=modified_count,
                unchanged_count=unchanged_count,
            )

            # 5. Trend and risk analysis (Short-circuit if insufficient history)
            trends = None
            risk_report = None

            logger.info("[Correlation-ID: %s] Stage 4: Listing historical results", corr_id)
            start_persist = time.perf_counter()
            try:
                history = self.persistence.list_results()
            except Exception as e:
                logger.error("[Correlation-ID: %s] Failed to load historical results: %s", corr_id, e)
                raise EvolutionPersistenceError(f"Failed to load historical results: {e}") from e
            persistence_ms += (time.perf_counter() - start_persist) * 1000.0

            # Build current temporary EvolutionResult wrapper for trends
            meta = EvolutionMetadata(
                project_name=request.project_name,
                source_commit=request.source_commit,
                target_commit=request.target_commit,
                created_at=datetime.now(timezone.utc),
                status=EvolutionStatus.COMPLETED,
            )
            current_res = EvolutionResult(
                evolution_id=uuid.uuid4(),
                metadata=meta,
                changes=changes,
                summary=summary,
            )

            full_history = tuple(list(history) + [current_res])

            if previous_snapshot is not None and len(full_history) >= 2:
                logger.info("[Correlation-ID: %s] Stage 5: Analyzing trends and risks", corr_id)
                start_trend = time.perf_counter()
                try:
                    trends = self.trend_analyzer.analyze_trends(full_history)
                except Exception as e:
                    logger.error("[Correlation-ID: %s] Trend calculation failed: %s", corr_id, e)
                    raise EvolutionValidationError(f"Trend calculation failed: {e}") from e
                trend_analysis_ms = (time.perf_counter() - start_trend) * 1000.0

                start_risk = time.perf_counter()
                try:
                    risk_report = self.risk_analyzer.analyze_risks(trends)
                except Exception as e:
                    logger.error("[Correlation-ID: %s] Risk analysis failed: %s", corr_id, e)
                    raise EvolutionValidationError(f"Risk analysis failed: {e}") from e
                risk_analysis_ms = (time.perf_counter() - start_risk) * 1000.0
            else:
                logger.info("[Correlation-ID: %s] Skipping trends/risks: insufficient history.", corr_id)

            total_orchestration_ms = (time.perf_counter() - start_total) * 1000.0
            logger.info("[Correlation-ID: %s] Completed architecture evolution analysis in %0.2fms", corr_id, total_orchestration_ms)

            extra_info = {
                "correlation_id": corr_id,
                "metrics": {
                    "snapshot_generation_ms": snapshot_generation_ms,
                    "architecture_comparison_ms": architecture_comparison_ms,
                    "trend_analysis_ms": trend_analysis_ms,
                    "risk_analysis_ms": risk_analysis_ms,
                    "persistence_ms": persistence_ms,
                    "total_orchestration_ms": total_orchestration_ms,
                }
            }

            # 6. Package final result DTO
            return ArchitectureEvolutionResult(
                evolution_result_id=uuid.uuid4(),
                request=request,
                current_snapshot=current_snapshot,
                previous_snapshot=previous_snapshot,
                changes=changes,
                summary=summary,
                trends=trends,
                risk_report=risk_report,
                extra_info=extra_info,
            )
        finally:
            execution_cache.reset(token)
