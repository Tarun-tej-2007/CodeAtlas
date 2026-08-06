"""Architecture Governance API endpoints module."""

import uuid
from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from app.governance import (
    ComplianceReport,
    GovernanceAnalysisResult,
    GovernancePolicy,
    GovernanceRequest,
    GovernanceResult,
    GovernanceViolationReport,
)
from app.governance.exceptions import GovernanceError, GovernanceValidationError
from app.governance.persistence import GovernancePersistenceService, GovernanceRepository
from app.governance.service import GovernanceService


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


router = APIRouter(prefix="/governance", dependencies=[Depends(verify_token)])


# Shared repository context getter
def get_governance_repo(request: Request) -> GovernanceRepository:
    """Retrieves or initializes the thread-safe in-memory GovernanceRepository on the app state."""
    if not hasattr(request.app.state, "governance_repo"):
        from app.tests.test_governance_persistence import InMemoryGovernanceRepository
        request.app.state.governance_repo = InMemoryGovernanceRepository()
    return request.app.state.governance_repo


def get_persistence_service(
    repo: GovernanceRepository = Depends(get_governance_repo),
) -> GovernancePersistenceService:
    """Dependency getter for the GovernancePersistenceService."""
    return GovernancePersistenceService(repo)


def get_governance_service(
    persistence: GovernancePersistenceService = Depends(get_persistence_service),
) -> GovernanceService:
    """Dependency getter for the GovernanceService."""
    from app.api.v1.endpoints.evolution import StubArchitectureAnalysisProvider
    from app.governance.policy_evaluation import PolicyEvaluationService
    from app.governance.violation_analyzer import GovernanceViolationAnalyzer
    from app.governance.compliance_scoring import ComplianceScoringService

    provider = StubArchitectureAnalysisProvider()
    evaluator = PolicyEvaluationService(provider)
    analyzer = GovernanceViolationAnalyzer()
    scorer = ComplianceScoringService()

    return GovernanceService(
        policy_evaluator=evaluator,
        violation_analyzer=analyzer,
        compliance_scorer=scorer,
        persistence=persistence,
    )


@router.post(
    "/verify",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Executes the complete architecture governance evaluation and scoring workflow",
)
async def verify_governance(
    payload: GovernanceRequest,
    service: GovernanceService = Depends(get_governance_service),
) -> Dict[str, Any]:
    """Orchestrates policy evaluations, violation enrichment, scoring and persistence."""
    try:
        result = service.verify_governance(payload)
        return result.model_dump()
    except GovernanceValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except GovernanceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/policy",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Persists a new architecture governance policy",
)
async def create_policy(
    payload: GovernancePolicy,
    persistence: GovernancePersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Validates and persists a governance policy."""
    try:
        persistence.save_policy(payload)
        return {"status": "created", "policy_id": str(payload.policy_id)}
    except GovernanceValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except GovernanceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/policy/{policy_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a persisted governance policy",
)
async def get_policy(
    policy_id: uuid.UUID,
    persistence: GovernancePersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves policy object metadata and rules by identifier."""
    try:
        policy = persistence.get_policy(policy_id)
        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GovernancePolicy {policy_id} not found.",
            )
        return policy.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/policy",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Updates an existing governance policy",
)
async def update_policy(
    payload: GovernancePolicy,
    persistence: GovernancePersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Updates mapped policy payload details in database."""
    try:
        persistence.update_policy(payload)
        return {"status": "updated", "policy_id": str(payload.policy_id)}
    except GovernanceValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except GovernanceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/policies",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Lists all registered governance policies",
)
async def list_policies(
    persistence: GovernancePersistenceService = Depends(get_persistence_service),
) -> List[Dict[str, Any]]:
    """Retrieves all registered governance policies in database."""
    try:
        policies = persistence.list_policies()
        return [p.model_dump() for p in policies]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/result/{result_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a persisted governance evaluation run result",
)
async def get_result(
    result_id: uuid.UUID,
    persistence: GovernancePersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves raw run results by identifier."""
    try:
        res = persistence.get_result(result_id)
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GovernanceResult {result_id} not found.",
            )
        return res.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/results/{project_id}",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="Lists all historical governance results for a project scope",
)
async def list_results(
    project_id: uuid.UUID,
    persistence: GovernancePersistenceService = Depends(get_persistence_service),
) -> List[Dict[str, Any]]:
    """Retrieves all historical run results for matching project scope UUID."""
    try:
        results = persistence.list_results(project_id)
        return [r.model_dump() for r in results]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/violation-report/{report_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves an enriched governance violation report",
)
async def get_violation_report(
    report_id: uuid.UUID,
    persistence: GovernancePersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves enriched violation diagnostics by identifier."""
    try:
        report = persistence.get_violation_report(report_id)
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GovernanceViolationReport {report_id} not found.",
            )
        return report.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/compliance-report/{report_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a compliance score report",
)
async def get_compliance_report(
    report_id: uuid.UUID,
    persistence: GovernancePersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves computed compliance reports by identifier."""
    try:
        report = persistence.get_compliance_report(report_id)
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ComplianceReport {report_id} not found.",
            )
        return report.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/analysis-result/{result_id}",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Retrieves a complete governance analysis result DTO",
)
async def get_analysis_result(
    result_id: uuid.UUID,
    persistence: GovernancePersistenceService = Depends(get_persistence_service),
) -> Dict[str, Any]:
    """Retrieves full governance analysis results DTO by identifier."""
    try:
        result = persistence.get_analysis_result(result_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GovernanceAnalysisResult {result_id} not found.",
            )
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
