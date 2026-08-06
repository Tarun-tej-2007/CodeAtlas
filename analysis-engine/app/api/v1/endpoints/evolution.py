"""Architecture Evolution API endpoints module."""

import uuid
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.evolution import (
    ArchitecturalRiskReport,
    ArchitectureEvolutionPersistenceService,
    ArchitectureEvolutionRepository,
    ArchitectureEvolutionResult,
    ArchitectureEvolutionService,
    ArchitectureSnapshot,
    ArchitectureSnapshotService,
    ArchitectureEvolutionDifferenceEngine,
    ArchitecturalTrendAnalyzer,
    CodeAtlasArchitecturalRiskAnalyzer,
    EvolutionMetadata,
    EvolutionRequest,
    EvolutionResult,
    EvolutionStatus,
    EvolutionSummary,
    EvolutionTrendResult,
    RiskSeverity,
)
from app.evolution.interfaces import ArchitectureAnalysisProvider


class EvolutionRequestSchema(BaseModel):
    """Schema for requesting architecture evolution analysis."""

    project_id: uuid.UUID = Field(..., description="Unique project tracking UUID.")
    project_name: str = Field(..., min_length=1, description="Display project name.")
    source_commit: str = Field(..., min_length=1, description="Baseline source commit hash.")
    target_commit: str = Field(..., min_length=1, description="Target commit hash to analyze.")


# Stub class definitions to satisfy snapshot builder dependencies without external calls
class StubGraph:
    nodes = ()
    edges = ()


class StubLayer:
    name = "Domain"


class StubMetric:
    name = "coupling"
    value = 0.5
    unit = "ratio"


class StubArchResult:
    layers = (StubLayer(),)
    metrics = (StubMetric(),)


class StubQualitySummary:
    overall_score = 90.0
    overall_level = "good"
    metrics_by_category = {}


class StubQualityReport:
    summary = StubQualitySummary()
    metrics = ()


class StubTechDebtReport:
    total_items = 5
    total_effort_minutes = 120
    items = ()


class StubArchitectureAnalysisProvider(ArchitectureAnalysisProvider):
    """Deterministic stub provider returning static metrics for pipeline execution."""

    def get_dependency_graph(self, commit_id: str) -> Optional[Any]:
        return StubGraph()

    def get_architecture_result(self, commit_id: str) -> Optional[Any]:
        return StubArchResult()

    def get_quality_report(self, commit_id: str) -> Optional[Any]:
        return StubQualityReport()

    def get_technical_debt_report(self, commit_id: str) -> Optional[Any]:
        return StubTechDebtReport()


# Shared repository getter
def get_persistence_repo(request: Request) -> ArchitectureEvolutionRepository:
    """Retrieves or initializes the Repository wrapper stored on the app state context."""
    if not hasattr(request.app.state, "evolution_repo"):
        from app.tests.test_evolution_persistence import InMemoryArchitectureEvolutionRepository
        request.app.state.evolution_repo = InMemoryArchitectureEvolutionRepository()
    return request.app.state.evolution_repo


def get_persistence_service(
    repo: ArchitectureEvolutionRepository = Depends(get_persistence_repo),
) -> ArchitectureEvolutionPersistenceService:
    """Dependency getter for the ArchitectureEvolutionPersistenceService."""
    return ArchitectureEvolutionPersistenceService(repo)


def get_evolution_service(
    persistence: ArchitectureEvolutionPersistenceService = Depends(get_persistence_service),
) -> ArchitectureEvolutionService:
    """Dependency getter for the ArchitectureEvolutionService."""
    provider = StubArchitectureAnalysisProvider()
    snapshot_calculator = ArchitectureSnapshotService(provider)
    return ArchitectureEvolutionService(
        snapshot_calculator=snapshot_calculator,
        difference_engine=ArchitectureEvolutionDifferenceEngine(),
        trend_analyzer=ArchitecturalTrendAnalyzer(),
        risk_analyzer=CodeAtlasArchitecturalRiskAnalyzer(),
        persistence=persistence,
    )


def verify_token(authorization: Optional[str] = Header(default=None)) -> str:
    """Dependency enforcing security token bearer authorization checks."""
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


router = APIRouter(prefix="/evolution", dependencies=[Depends(verify_token)])


@router.post(
    "/analyze",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Starts an architecture evolution analysis",
)
async def submit_evolution_analysis(
    payload: EvolutionRequestSchema,
    service: ArchitectureEvolutionService = Depends(get_evolution_service),
    persistence: ArchitectureEvolutionPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Runs target snapshot calculations, builds diff changes logging and updates trends."""
    request_dto = EvolutionRequest(
        project_id=payload.project_id,
        project_name=payload.project_name,
        source_commit=payload.source_commit,
        target_commit=payload.target_commit,
    )

    try:
        result = service.evolve_architecture(request_dto)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Persist the output states atomically
    try:
        persistence.save_snapshot(result.current_snapshot)
        # Reconstruct an EvolutionResult to save in history
        meta = EvolutionMetadata(
            project_name=result.request.project_name,
            source_commit=result.request.source_commit,
            target_commit=result.request.target_commit,
            created_at=result.current_snapshot.timestamp,
            status=EvolutionStatus.COMPLETED,
        )
        res = EvolutionResult(
            evolution_id=result.evolution_result_id,
            metadata=meta,
            changes=result.changes,
            summary=result.summary,
        )
        persistence.save_result(res)

        if result.trends is not None:
            persistence.save_trend(result.evolution_result_id, result.trends)
        if result.risk_report is not None:
            persistence.save_risk_report(result.evolution_result_id, result.risk_report)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to persist evolution results: {e}",
        )

    return result.model_dump()


@router.get(
    "/snapshot/{commit_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves an architecture snapshot",
)
async def get_architecture_snapshot(
    commit_id: str,
    persistence: ArchitectureEvolutionPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves snapshot metrics for matching commit hash."""
    snap = persistence.get_snapshot(commit_id)
    if snap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ArchitectureSnapshot for commit {commit_id} not found.",
        )
    return snap.model_dump()


@router.get(
    "/result/{evolution_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves architecture evolution results",
)
async def get_evolution_result(
    evolution_id: uuid.UUID,
    persistence: ArchitectureEvolutionPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves computed analysis results by identifier."""
    result = persistence.get_result(evolution_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"EvolutionResult {evolution_id} not found.",
        )
    return result.model_dump()


@router.get(
    "/trend/{evolution_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves historical trends",
)
async def get_historical_trend(
    evolution_id: uuid.UUID,
    persistence: ArchitectureEvolutionPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves historical trends report by result UUID."""
    trend = persistence.get_trend(evolution_id)
    if trend is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"EvolutionTrendResult {evolution_id} not found.",
        )
    return trend.model_dump()


@router.get(
    "/risks/{evolution_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves architectural risk reports",
)
async def get_risk_report(
    evolution_id: uuid.UUID,
    persistence: ArchitectureEvolutionPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves computed architectural risk report by result UUID."""
    report = persistence.get_risk_report(evolution_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ArchitecturalRiskReport {evolution_id} not found.",
        )
    return report.model_dump()
