"""Analysis Engine endpoints module."""

import uuid
import logging
from fastapi import APIRouter, Response, Header, status
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisStatus

router = APIRouter()
logger = logging.getLogger("analysis-engine")


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
) -> AnalysisResponse:
    """Accepts a repository URL and project ID, registering an analysis job."""
    req_id = x_request_id or str(uuid.uuid4())
    response.headers["X-Request-ID"] = req_id
    
    logger.info("Received analysis request for project %s [Request-ID: %s]", request.project_id, req_id)
    
    return AnalysisResponse(
        job_id=uuid.uuid4(),
        status=AnalysisStatus.ACCEPTED,
        message="Analysis request received",
        project_id=request.project_id,
        repository_url=request.repository_url,
    )
