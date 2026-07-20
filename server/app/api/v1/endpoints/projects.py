import uuid
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.enums import ProjectVisibility
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    PaginatedProjectResponse,
)
from app.services.project import ProjectService
from app.core.exceptions import ProjectNotFoundError


router = APIRouter()



@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project workspace",
    description="Creates a new project entity for the current authenticated user and automatically generates a URL-safe slug.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Project created successfully.",
            "headers": {
                "Location": {
                    "description": "Canonical URI of created project",
                    "schema": {"type": "string"},
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Malformed JSON payload or invalid request format."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid access token credentials."
        },
        status.HTTP_409_CONFLICT: {
            "description": "A project with this name or slug already exists for the owner."
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Field-level schema validation error."
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Unexpected server error."
        },
    },
)
def create_project(
    data: ProjectCreate,
    response: Response,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    HTTP endpoint to create a new project workspace for the current authenticated user.
    Translates domain and database exceptions into standardized HTTP responses.
    """
    project_service = ProjectService(db)
    try:
        project = project_service.create_project(owner_id=current_user_id, data=data)
        response.headers["Location"] = f"/api/v1/projects/{project.id}"
        return project
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A project with this name or slug already exists for the owner.",
        )



@router.get(

    "",
    response_model=PaginatedProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="List projects",
    description="Retrieve a paginated list of projects visible to the authenticated requesting user.",
    responses={
        status.HTTP_200_OK: {
            "description": "Paginated list of projects retrieved successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid access token credentials."
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation error for query parameter format or allowed values."
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Unexpected server error."
        },
    },
)
def list_projects(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)."),
    size: int = Query(default=20, ge=1, le=100, description="Number of items per page."),
    sort_by: Literal["created_at", "updated_at", "name"] = Query(
        default="created_at", description="Attribute to sort by."
    ),
    order: Literal["asc", "desc"] = Query(
        default="desc", description="Sort ordering direction."
    ),
    search: str | None = Query(
        default=None, max_length=100, description="Case-insensitive search on name or description."
    ),
    visibility: ProjectVisibility | None = Query(
        default=None, description="Filter results by project visibility."
    ),
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    HTTP endpoint to retrieve a paginated list of projects visible to the requesting user.
    """
    project_service = ProjectService(db)
    return project_service.list_projects_paginated(
        owner_id=current_user_id,
        page=page,
        size=size,
        sort_by=sort_by,
        order=order,
        search=search,
        visibility=visibility,
    )



@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project details",
    description="Fetch complete details for a specific project by UUID.",
    responses={
        status.HTTP_200_OK: {
            "description": "Project details retrieved successfully."
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing or invalid access token credentials."
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Project not found or requester lacks read permission."
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Malformed project_id UUID parameter."
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Unexpected server error."
        },
    },
)
def get_project(
    project_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    HTTP endpoint to fetch complete details of a project by UUID.
    Returns 404 if project does not exist or if private project is owned by another user.
    """
    project_service = ProjectService(db)
    try:
        return project_service.get_project_with_access(
            project_id=project_id, requesting_user_id=current_user_id
        )
    except ProjectNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e) or "Project not found",
        )



@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update project",
    description="Partially update an existing project's metadata (name, description, visibility).",
)
def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    HTTP endpoint placeholder to partially update a project.
    CRUD business logic will be implemented in subsequent steps.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint logic not implemented yet.",
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete a project workspace.",
)
def delete_project(
    project_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    HTTP endpoint placeholder to delete a project.
    CRUD business logic will be implemented in subsequent steps.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint logic not implemented yet.",
    )
