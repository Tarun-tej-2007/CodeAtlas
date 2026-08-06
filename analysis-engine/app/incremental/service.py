"""Incremental Analysis Service Module."""

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Union

from app.graph.dependency_graph import DependencyGraph
from app.incremental.enums import ChangeType, IncrementalStatus
from app.incremental.exceptions import IncrementalAnalysisValidationError
from app.incremental.models import (
    ChangedFile,
    IncrementalAnalysisMetadata,
    IncrementalAnalysisResult,
    RepositorySnapshot,
)
from app.incremental.snapshot_service import RepositorySnapshotService
from app.incremental.diff import SHA256SnapshotDifferenceEngine
from app.incremental.impact import DependencyImpactAnalyzer
from app.incremental.interfaces import IncrementalAnalysisPersistence


class IncrementalAnalysisService:
    """Service orchestrating the complete incremental analysis pipeline."""

    def __init__(
        self,
        snapshot_service: RepositorySnapshotService,
        diff_engine: SHA256SnapshotDifferenceEngine,
        impact_analyzer: DependencyImpactAnalyzer,
        persistence: IncrementalAnalysisPersistence,
    ) -> None:
        """Initializes the orchestrator with constructor-injected dependencies."""
        if any(
            arg is None
            for arg in (snapshot_service, diff_engine, impact_analyzer, persistence)
        ):
            raise ValueError("All IncrementalAnalysisService dependencies must not be None.")

        self.snapshot_service = snapshot_service
        self.diff_engine = diff_engine
        self.impact_analyzer = impact_analyzer
        self.persistence = persistence

    def analyze_incrementally(
        self,
        *,
        project_id: uuid.UUID,
        project_name: str,
        repository_root: Union[Path, str],
        source_commit: str,
        target_commit: str,
        dependency_graph: DependencyGraph,
    ) -> IncrementalAnalysisResult:
        """Runs snapshot creation, change difference calculation, impact tracing, and persistence sequence.

        Args:
            project_id: Unique project identifier.
            project_name: Display project name.
            repository_root: Filesystem path to repository codebase root.
            source_commit: Source baseline commit identifier hash.
            target_commit: Target/current commit identifier hash.
            dependency_graph: Baseline DependencyGraph used for impact resolution.

        Returns:
            The finalized IncrementalAnalysisResult DTO.
        """
        if project_id is None or not isinstance(project_id, uuid.UUID):
            raise IncrementalAnalysisValidationError("project_id must be a valid UUID.")
        if project_name is None or not project_name.strip():
            raise IncrementalAnalysisValidationError("project_name must be a non-empty string.")
        if repository_root is None:
            raise IncrementalAnalysisValidationError("repository_root must not be None.")
        if source_commit is None or not source_commit.strip():
            raise IncrementalAnalysisValidationError("source_commit must be a non-empty string.")
        if target_commit is None or not target_commit.strip():
            raise IncrementalAnalysisValidationError("target_commit must be a non-empty string.")
        if dependency_graph is None or not isinstance(dependency_graph, DependencyGraph):
            raise IncrementalAnalysisValidationError("dependency_graph must be an instance of DependencyGraph.")

        from app.incremental.cache import execution_cache

        # Set up a clean execution-scoped cache context
        token = execution_cache.set({})
        try:
            # 1. Retrieve previous repository snapshot first to populate cache with baseline snapshots
            previous_snapshot = self.persistence.get_snapshot(source_commit)
            if previous_snapshot is None:
                previous_snapshot = RepositorySnapshot(commit_id=source_commit, fingerprints={})

            # Save the previous snapshot in cache context for downstream fingerprint generators
            cache = execution_cache.get()
            if cache is not None:
                cache["previous_snapshot"] = previous_snapshot

            # 2. Compile current repository snapshot
            current_snapshot = self.snapshot_service.create_snapshot(repository_root, target_commit)

        # 3. Compute changes
            changed_files = self.diff_engine.diff_snapshots(previous_snapshot, current_snapshot)

            # 4. Count change categories
            added_count = 0
            modified_count = 0
            deleted_count = 0
            unchanged_count = 0

            for cf in changed_files:
                if cf.change_type == ChangeType.ADDED:
                    added_count += 1
                elif cf.change_type == ChangeType.MODIFIED:
                    modified_count += 1
                elif cf.change_type == ChangeType.DELETED:
                    deleted_count += 1
                elif cf.change_type == ChangeType.UNCHANGED:
                    unchanged_count += 1

            reanalysis_required = (added_count + modified_count + deleted_count) > 0

            # 5. Determine impact set (Short-circuit if unchanged)
            impacted_nodes: Tuple[str, ...] = ()
            if reanalysis_required:
                impacted_nodes = self.impact_analyzer.analyze_impact(dependency_graph, changed_files)

            # 6. Build Result DTO
            metadata = IncrementalAnalysisMetadata(
                project_name=project_name,
                source_commit=source_commit,
                target_commit=target_commit,
                created_at=datetime.now(timezone.utc),
                status=IncrementalStatus.COMPLETED,
                extra_info={"impacted_nodes": list(impacted_nodes)},
            )

            result = IncrementalAnalysisResult(
                analysis_id=uuid.uuid4(),
                metadata=metadata,
                added_count=added_count,
                modified_count=modified_count,
                deleted_count=deleted_count,
                unchanged_count=unchanged_count,
                changed_files=changed_files,
            )

            # 7. Persist result and target snapshot exactly once
            self.persistence.save_result(result)
            self.persistence.save_snapshot(current_snapshot)

            return result
        finally:
            execution_cache.reset(token)
