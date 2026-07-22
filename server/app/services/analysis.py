"""Analysis service module coordinating project analysis workflows."""

import uuid
from typing import Any
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ProjectNotFoundError,
    AnalysisEngineRequestError,
)
from app.services.project import ProjectService
from app.services.analysis_engine import AnalysisEngineClient
from app.schemas.analysis import AnalysisRequest, AnalysisResponse


class AnalysisService:
    """Service layer orchestrating static repository analysis jobs."""

    def __init__(self, db: Session) -> None:
        """Initializes AnalysisService.

        Args:
            db: Database session.
        """
        self.db = db
        self.project_service = ProjectService(db)

    async def submit_project_analysis(
        self,
        project_id: uuid.UUID,
        requesting_user_id: uuid.UUID,
        request_id: str | None = None,
    ) -> AnalysisResponse:
        """Coordinates and submits a project codebase for analysis.

        1. Verifies the project workspace exists and requester has access.
        2. Retrieves the repository clone URL.
        3. Invokes the Analysis Engine client, forwarding the correlation request ID.

        Args:
            project_id: Unique project workspace ID.
            requesting_user_id: ID of the authenticated user requesting analysis.
            request_id: Optional existing X-Request-ID to preserve.

        Returns:
            AnalysisResponse payload.
        """
        # 1. Resolve project and access
        project = self.project_service.get_project_with_access(
            project_id=project_id, requesting_user_id=requesting_user_id
        )
        if not project:
            raise ProjectNotFoundError(f"Project '{project_id}' not found.")

        # 2. Extract repository clone URL
        if not project.repositories:
            raise AnalysisEngineRequestError("Project has no registered repository configuration.")

        repo = project.repositories[0]
        if not repo.clone_url:
            raise AnalysisEngineRequestError("Project repository has an invalid or empty clone URL.")

        # Ensure we have a request correlation ID
        correlation_id = request_id or str(uuid.uuid4())

        # 3. Call client
        client = AnalysisEngineClient()
        request_payload = AnalysisRequest(
            repository_url=repo.clone_url,
            project_id=project.id,
        )

        return await client.submit_analysis(request_payload, request_id=correlation_id)
