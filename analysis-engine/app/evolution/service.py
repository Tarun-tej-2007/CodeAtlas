"""Orchestration service layer for Architecture Evolution."""

import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple

from app.evolution.enums import ArchitecturalChangeType, EvolutionStatus
from app.evolution.exceptions import EvolutionValidationError
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
        """
        if request is None or not isinstance(request, EvolutionRequest):
            raise EvolutionValidationError("request parameter must be a valid EvolutionRequest.")

        from app.evolution.cache import execution_cache
        token = execution_cache.set({})

        try:
            # 1. Build current target snapshot
            try:
                current_snapshot = self.snapshot_calculator.calculate_snapshot(request.target_commit)
            except Exception as e:
                raise EvolutionValidationError(f"Snapshot building failed: {e}") from e

            # 2. Retrieve previous source snapshot from persistence
            try:
                previous_snapshot = self.persistence.get_snapshot(request.source_commit)
            except Exception as e:
                raise EvolutionValidationError(
                    f"Failed to retrieve source snapshot for '{request.source_commit}': {e}"
                ) from e

            # 3. Compare snapshots
            # Support first-time analysis when previous snapshot is not found in database
            if previous_snapshot is None:
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
                    raise EvolutionValidationError(f"Snapshot comparison failed: {e}") from e
            else:
                try:
                    changes = self.difference_engine.diff_snapshots(previous_snapshot, current_snapshot)
                except Exception as e:
                    raise EvolutionValidationError(f"Snapshot comparison failed: {e}") from e

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

            try:
                history = self.persistence.list_results()
            except Exception as e:
                raise EvolutionValidationError(f"Failed to load historical results: {e}") from e

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
                try:
                    trends = self.trend_analyzer.analyze_trends(full_history)
                    risk_report = self.risk_analyzer.analyze_risks(trends)
                except Exception as e:
                    raise EvolutionValidationError(f"Trend/Risk calculation failed: {e}") from e

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
            )
        finally:
            execution_cache.reset(token)
