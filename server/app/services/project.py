import uuid
import re
import math
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.enums import ProjectVisibility
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, PaginatedProjectResponse
from app.core.exceptions import ProjectNotFoundError, ProjectForbiddenError


class ProjectService:
    """
    Business service orchestrating Project workspace entities lifecycle.
    """

    def __init__(self, db: Session, project_repo: ProjectRepository | None = None) -> None:
        self.db = db
        self.project_repo = project_repo or ProjectRepository(db)

    def _generate_unique_slug(self, owner_id: uuid.UUID, name: str, current_project_id: uuid.UUID | None = None) -> str:
        """
        Generates a URL-safe slug from a project name, converting to lowercase,
        substituting whitespace with hyphens, and removing special characters.
        Enforces uniqueness by appending sequential counters if conflicts exist.
        """
        slug = name.lower()
        # Convert spaces and whitespace blocks to single hyphens
        slug = re.sub(r"\s+", "-", slug)
        # Strip all characters other than lowercase letters, digits, and hyphens
        slug = re.sub(r"[^a-z0-9\-]", "", slug)
        # Collapse multiple hyphens
        slug = re.sub(r"-+", "-", slug)
        # Trim leading/trailing hyphens
        slug = slug.strip("-")
        
        if not slug:
            slug = "project"

        base_slug = slug
        counter = 2
        
        while True:
            existing = self.project_repo.get_by_slug(owner_id, slug)
            if not existing or (current_project_id is not None and existing.id == current_project_id):
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug

    def create_project(self, owner_id: uuid.UUID, data: ProjectCreate) -> Project:
        """
        Executes database registration for a new Project workspace.
        """
        slug = self._generate_unique_slug(owner_id, data.name)
        
        project = Project(
            owner_id=owner_id,
            name=data.name,
            slug=slug,
            description=data.description,
            visibility=data.visibility,
        )
        
        self.project_repo.create(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project(self, project_id: uuid.UUID) -> Project:
        """
        Retrieves a project workspace by its unique primary key.
        Raises ProjectNotFoundError if no workspace matches.
        """
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ProjectNotFoundError("Project not found")
        return project

    def get_project_with_access(self, project_id: uuid.UUID, requesting_user_id: uuid.UUID) -> Project:
        """
        Retrieves a project by UUID if accessible to the requesting user.
        Raises ProjectNotFoundError if project does not exist or user lacks read permission.
        """
        project = self.project_repo.get_by_id_and_access(project_id, requesting_user_id)
        if not project:
            raise ProjectNotFoundError("Project not found")
        return project


    def list_projects(self, owner_id: uuid.UUID) -> list[Project]:
        """
        Retrieves all project workspaces owned by the specified user.
        """
        return self.project_repo.list_by_owner(owner_id)

    def list_projects_paginated(
        self,
        owner_id: uuid.UUID,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        order: str = "desc",
        search: str | None = None,
        visibility: ProjectVisibility | None = None,
    ) -> PaginatedProjectResponse:
        """
        Orchestrates paginated listing of projects visible to the given user,
        calculating pagination metadata and wrapping results in PaginatedProjectResponse.
        """
        items, total = self.project_repo.list_projects_paginated(
            owner_id=owner_id,
            page=page,
            size=size,
            sort_by=sort_by,
            order=order,
            search=search,
            visibility=visibility,
        )

        pages = math.ceil(total / size) if total > 0 else 0
        count = len(items)
        has_next = page < pages
        has_previous = page > 1 and page <= (pages + 1)

        return PaginatedProjectResponse(
            items=[ProjectResponse.model_validate(item) for item in items],
            count=count,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=has_next,
            has_previous=has_previous,
        )


    def update_project(

        self,
        project_id: uuid.UUID,
        data: ProjectUpdate,
        requesting_user_id: uuid.UUID | None = None,
    ) -> Project:
        """
        Updates project attributes. If requesting_user_id is supplied, validates ownership.
        Regenerates slug if project name changes.
        Raises ProjectNotFoundError if project does not exist (or is private to another user).
        Raises ProjectForbiddenError if public project is owned by another user.
        """
        project = self.get_project(project_id)

        if requesting_user_id is not None and project.owner_id != requesting_user_id:
            if project.visibility == ProjectVisibility.PRIVATE:
                raise ProjectNotFoundError("Project not found")
            raise ProjectForbiddenError("You do not have permission to update this project")

        if data.name is not None:
            project.name = data.name
            project.slug = self._generate_unique_slug(
                project.owner_id, data.name, current_project_id=project_id
            )

        if data.description is not None:
            project.description = data.description

        if data.visibility is not None:
            project.visibility = data.visibility

        self.project_repo.update(project)
        self.db.commit()
        self.db.refresh(project)
        return project


    def delete_project(
        self,
        project_id: uuid.UUID,
        requesting_user_id: uuid.UUID | None = None,
    ) -> None:
        """
        Deletes a project workspace. If requesting_user_id is supplied, validates ownership.
        Raises ProjectNotFoundError if project does not exist (or is private to another user).
        Raises ProjectForbiddenError if public project is owned by another user.
        """
        project = self.get_project(project_id)

        if requesting_user_id is not None and project.owner_id != requesting_user_id:
            if project.visibility == ProjectVisibility.PRIVATE:
                raise ProjectNotFoundError("Project not found")
            raise ProjectForbiddenError("You do not have permission to delete this project")

        self.project_repo.delete(project)
        self.db.commit()

