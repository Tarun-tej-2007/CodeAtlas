"""Analysis Engine endpoints module."""

import uuid
import logging
from fastapi import APIRouter, Response, Header, status, Depends
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisStatus
from app.services.analysis import AnalysisService

router = APIRouter()
logger = logging.getLogger("analysis-engine")


def get_analysis_service() -> AnalysisService:
    """Dependency getter for the AnalysisService."""
    return AnalysisService()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit codebase repository for parsing and semantic analysis",
)
async def submit_analysis(
    request: AnalysisRequest,
    response: Response,
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
    run_sync: bool = False,
    analysis_service: AnalysisService = Depends(get_analysis_service),
) -> AnalysisResponse:
    """Accepts a repository URL and project ID, registering an analysis job. Integrates with reporting & persistence."""
    req_id = x_request_id or str(uuid.uuid4())
    response.headers["X-Request-ID"] = req_id
    
    logger.info("Received analysis request for project %s [Request-ID: %s]", request.project_id, req_id)
    
    unified_res = None
    report_res = None
    if run_sync:
        res = analysis_service.analyze_repository(
            repository_url=request.repository_url,
            project_id=request.project_id,
        )
        unified_res = getattr(res, "unified_result", None)
        report_res = getattr(res, "report_result", None)
        msg = "Analysis completed synchronously"
        status_code = AnalysisStatus.COMPLETED
    else:
        msg = "Analysis request received"
        status_code = AnalysisStatus.ACCEPTED

    return AnalysisResponse(
        job_id=uuid.uuid4(),
        status=status_code,
        message=msg,
        project_id=request.project_id,
        repository_url=request.repository_url,
        unified_result=unified_res,
        report_result=report_res,
    )
