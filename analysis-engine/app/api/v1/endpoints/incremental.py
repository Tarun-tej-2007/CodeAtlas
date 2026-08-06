"""Incremental Analysis API endpoints module."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.graph.dependency_graph import DependencyGraph
from app.graph.dependency_models import GraphEdge, GraphNode
from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.incremental import (
    ChangedFile,
    DependencyImpactAnalyzer,
    IncrementalAnalysisPersistenceService,
    IncrementalAnalysisRepository,
    IncrementalAnalysisResult,
    IncrementalAnalysisService,
    RepositorySnapshot,
    RepositorySnapshotService,
    SHA256FingerprintGenerator,
    SHA256SnapshotDifferenceEngine,
)


class IncrementalAnalysisRequestSchema(BaseModel):
    """Schema for requesting incremental codebase analysis."""

    project_id: uuid.UUID = Field(..., description="Unique project tracking UUID.")
    project_name: str = Field(..., min_length=1, description="Display project name.")
    repository_root: str = Field(..., min_length=1, description="Absolute path to the repository directory.")
    source_commit: str = Field(..., min_length=1, description="Baseline source commit hash.")
    target_commit: str = Field(..., min_length=1, description="Target commit hash to analyze.")
    nodes: List[Dict[str, Any]] = Field(default_factory=list, description="Graph nodes list description.")
    edges: List[Dict[str, Any]] = Field(default_factory=list, description="Graph edges list description.")


# Shared mock repository using app state to avoid globals
def get_persistence_repo(request: Request) -> IncrementalAnalysisRepository:
    """Retrieves or initializes the Repository wrapper stored on the app state context."""
    if not hasattr(request.app.state, "incremental_repo"):
        from app.tests.test_incremental_persistence import InMemoryIncrementalAnalysisRepository
        request.app.state.incremental_repo = InMemoryIncrementalAnalysisRepository()
    return request.app.state.incremental_repo


def get_persistence_service(repo: IncrementalAnalysisRepository = Depends(get_persistence_repo)) -> IncrementalAnalysisPersistenceService:
    """Dependency getter for the IncrementalAnalysisPersistenceService."""
    return IncrementalAnalysisPersistenceService(repo)


def get_incremental_service(
    persistence: IncrementalAnalysisPersistenceService = Depends(get_persistence_service),
) -> IncrementalAnalysisService:
    """Dependency getter for the IncrementalAnalysisService."""
    from app.scanner.pipeline import ScannerPipeline
    # Instantiate collaborators
    scanner = ScannerPipeline()
    snapshot_service = RepositorySnapshotService(
        scanner=scanner,
        fingerprint_generator=SHA256FingerprintGenerator(),
    )
    return IncrementalAnalysisService(
        snapshot_service=snapshot_service,
        diff_engine=SHA256SnapshotDifferenceEngine(),
        impact_analyzer=DependencyImpactAnalyzer(),
        persistence=persistence,
    )


def verify_token(authorization: Optional[str] = Header(default=None)) -> str:
    """FastAPI dependency enforcing security token authentication and authorization."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Only Bearer token is supported.",
        )
    token = authorization.split(" ")[1]
    if token != "supersecretjwtkey123!":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid security token.",
        )
    return token


router = APIRouter(prefix="/incremental", dependencies=[Depends(verify_token)])


@router.post(
    "/analyze",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Starts an incremental codebase analysis",
)
async def submit_incremental_analysis(
    payload: IncrementalAnalysisRequestSchema,
    x_request_id: Optional[str] = Header(default=None, alias="X-Request-ID"),
    service: IncrementalAnalysisService = Depends(get_incremental_service),
) -> Dict[str, Any]:
    """Resolves changed files difference metrics and calculates downstream impact sets."""
    # Reconstruct DependencyGraph from request nodes and edges lists
    try:
        nodes = [
            GraphNode(
                id=n["id"],
                name=n["name"],
                type=DependencyNodeType(n["type"]),
            )
            for n in payload.nodes
        ]
        edges = [
            GraphEdge(
                source_id=e["source_id"],
                target_id=e["target_id"],
                type=DependencyEdgeType(e["type"]),
            )
            for e in payload.edges
        ]
        dependency_graph = DependencyGraph(nodes=nodes, edges=edges)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid graph node/edge format: {e}",
        )

    try:
        result = service.analyze_incrementally(
            project_id=payload.project_id,
            project_name=payload.project_name,
            repository_root=payload.repository_root,
            source_commit=payload.source_commit,
            target_commit=payload.target_commit,
            dependency_graph=dependency_graph,
            correlation_id=x_request_id,
        )
        return result.model_dump()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/snapshot/{commit_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a repository snapshot",
)
async def get_repository_snapshot(
    commit_id: str,
    persistence: IncrementalAnalysisPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves snapshot mappings for matching commit hash."""
    snap = persistence.get_snapshot(commit_id)
    if snap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RepositorySnapshot for commit {commit_id} not found.",
        )
    return snap.model_dump()


@router.get(
    "/result/{analysis_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves incremental analysis metadata results",
)
async def get_incremental_result(
    analysis_id: uuid.UUID,
    persistence: IncrementalAnalysisPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves computed analysis results by identifier."""
    result = persistence.get_result(analysis_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IncrementalAnalysisResult {analysis_id} not found.",
        )
    return result.model_dump()


@router.get(
    "/changes/{analysis_id}",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Retrieves file changes lists",
)
async def get_incremental_changes(
    analysis_id: uuid.UUID,
    persistence: IncrementalAnalysisPersistenceService = Depends(get_persistence_service),
) -> List[Dict[str, Any]]:
    """Retrieves the list of changed files from computed analysis result."""
    result = persistence.get_result(analysis_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IncrementalAnalysisResult {analysis_id} not found.",
        )
    # Ensure deterministic response ordering by sorting changed files alphabetically
    sorted_files = sorted(result.changed_files, key=lambda f: f.path)
    return [cf.model_dump() for cf in sorted_files]
