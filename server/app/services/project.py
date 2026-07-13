import uuid
import re
from sqlalchemy.orm import Session
from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.exceptions import ProjectNotFoundError

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

    def list_projects(self, owner_id: uuid.UUID) -> list[Project]:
        """
        Retrieves all project workspaces owned by the specified user.
        """
        return self.project_repo.list_by_owner(owner_id)

    def update_project(self, project_id: uuid.UUID, data: ProjectUpdate) -> Project:
        """
        Updates project attributes. If project name is updated, regenerates and
        updates the project's unique slug.
        """
        project = self.get_project(project_id)
        
        if data.name is not None:
            project.name = data.name
            project.slug = self._generate_unique_slug(project.owner_id, data.name, current_project_id=project_id)
            
        if data.description is not None:
            project.description = data.description
            
        if data.visibility is not None:
            project.visibility = data.visibility
            
        self.project_repo.update(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project_id: uuid.UUID) -> None:
        """
        Hard-deletes a project workspace.
        """
        project = self.get_project(project_id)
        self.project_repo.delete(project)
        self.db.commit()
