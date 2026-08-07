"""Architecture Decision Intelligence API endpoints module."""

import uuid
from typing import Any, Dict, Optional, Tuple
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.decision import (
    ArchitectureDecision,
    DecisionAnalysisResult,
    DecisionDriftReport,
    DecisionHealthReport,
    DecisionRequest,
    DecisionTraceGraph,
    DecisionBuilderService,
    DecisionTraceabilityService,
    DecisionDriftAnalyzerService,
    DecisionHealthAnalyzerService,
    DecisionIntelligenceService,
    DecisionPersistenceService,
    DecisionRepository,
)
from app.decision.exceptions import DecisionPersistenceError, DecisionTraceabilityError, DecisionValidationError


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


router = APIRouter(prefix="/decision", dependencies=[Depends(verify_token)])


def get_decision_repo(request: Request) -> DecisionRepository:
    """Retrieves or initializes the thread-safe in-memory DecisionRepository on the app state."""
    if not hasattr(request.app.state, "decision_repo"):
        from app.tests.test_decision_persistence import InMemoryDecisionRepository
        request.app.state.decision_repo = InMemoryDecisionRepository()
    return request.app.state.decision_repo


def get_persistence_service(
    repo: DecisionRepository = Depends(get_decision_repo),
) -> DecisionPersistenceService:
    """Dependency getter for the DecisionPersistenceService."""
    return DecisionPersistenceService(repo)


def get_decision_service(
    persistence: DecisionPersistenceService = Depends(get_persistence_service),
) -> DecisionIntelligenceService:
    """Dependency getter for the DecisionIntelligenceService orchestrator."""
    builder = DecisionBuilderService()
    traceability = DecisionTraceabilityService()
    drift = DecisionDriftAnalyzerService()
    health = DecisionHealthAnalyzerService()

    return DecisionIntelligenceService(
        builder=builder,
        traceability_provider=traceability,
        drift_analyzer=drift,
        health_analyzer=health,
        persistence=persistence,
    )


class DecisionAnalyzeRequestPayload(BaseModel):
    """Payload schema requesting full decision pipeline analysis execution."""

    project_id: uuid.UUID = Field(..., description="Unique project tracking UUID.")
    commit_id: str = Field(..., min_length=1, description="Target Git commit hash.")
    requests: Tuple[DecisionRequest, ...] = Field(
        default_factory=tuple, description="Decisions registration requests."
    )


def resolve_decision_context(
    decision_id: uuid.UUID, persistence: DecisionPersistenceService
) -> Tuple[uuid.UUID, str]:
    """Helper to resolve the project and commit ID context from the saved decision record key metadata."""
    dec = persistence.get_decision(decision_id)
    if not dec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision with ID '{decision_id}' not found.",
        )

    repo = persistence.repository
    keys = repo.list_keys_starting_with("decision:")
    project_id = None
    for k in keys:
        if k.endswith(f":{decision_id}"):
            parts = k.split(":")
            project_id = uuid.UUID(parts[1])
            break

    if not project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project scope context for decision '{decision_id}' not found.",
        )

    # Resolve commit ID by checking trace, drift, health or result keys
    commit_id = "default-commit"
    for prefix in (f"result:{project_id}:", f"trace:{project_id}:", f"drift:{project_id}:", f"health:{project_id}:"):
        matching_keys = repo.list_keys_starting_with(prefix)
        if matching_keys:
            commit_id = matching_keys[0].split(":")[-1]
            break
    return project_id, commit_id


@router.post(
    "/analyze",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Executes complete architecture decision intelligence analysis orchestration",
)
async def analyze_decisions(
    payload: DecisionAnalyzeRequestPayload,
    service: DecisionIntelligenceService = Depends(get_decision_service),
) -> Dict[str, Any]:
    """Runs decision compilation, traceability, drift, and health evaluation."""
    try:
        result = service.analyze_project_decisions(
            project_id=payload.project_id,
            commit_id=payload.commit_id,
            requests=payload.requests,
        )
        return result.model_dump(mode="json")
    except DecisionValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except (DecisionPersistenceError, DecisionTraceabilityError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{decision_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a persisted architecture decision by identifier",
)
async def get_decision(
    decision_id: uuid.UUID,
    persistence: DecisionPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Query stored decisions table."""
    dec = persistence.get_decision(decision_id)
    if not dec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision with ID '{decision_id}' not found.",
        )
    return dec.model_dump(mode="json")


@router.get(
    "/trace/{decision_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a persisted decision trace graph matching decision",
)
async def get_trace_graph(
    decision_id: uuid.UUID,
    persistence: DecisionPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Query stored trace graphs."""
    project_id, commit_id = resolve_decision_context(decision_id, persistence)
    graph = persistence.get_trace_graph(project_id, commit_id)
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace graph not found for decision '{decision_id}'.",
        )
    return graph.model_dump(mode="json")


@router.get(
    "/drift/{decision_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a persisted decision drift report matching decision",
)
async def get_drift_report(
    decision_id: uuid.UUID,
    persistence: DecisionPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Query stored drift reports."""
    project_id, commit_id = resolve_decision_context(decision_id, persistence)
    report = persistence.get_drift_report(project_id, commit_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drift report not found for decision '{decision_id}'.",
        )
    return report.model_dump(mode="json")


@router.get(
    "/health/{decision_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a persisted decision health report matching decision",
)
async def get_health_report(
    decision_id: uuid.UUID,
    persistence: DecisionPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Query stored health reports."""
    project_id, commit_id = resolve_decision_context(decision_id, persistence)
    report = persistence.get_health_report(project_id, commit_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Health report not found for decision '{decision_id}'.",
        )
    return report.model_dump(mode="json")


@router.get(
    "/analysis/{decision_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a complete persisted decision analysis result matching decision",
)
async def get_analysis_result(
    decision_id: uuid.UUID,
    persistence: DecisionPersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Query stored aggregate analysis results."""
    project_id, commit_id = resolve_decision_context(decision_id, persistence)
    result = persistence.get_analysis_result(project_id, commit_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis result not found for decision '{decision_id}'.",
        )
    return result.model_dump(mode="json")
