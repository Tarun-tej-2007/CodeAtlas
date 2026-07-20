import uuid
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.enums import ProjectVisibility

class ProjectRepository:
    """
    SQLAlchemy 2.0 repository mapping database queries for the Project model.
    Encapsulates all SQL statements to isolate the service layer from direct database queries.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        """
        Retrieves a Project by its unique UUID primary key.
        """
        return self.db.get(Project, project_id)

    def get_by_slug(self, owner_id: uuid.UUID, slug: str) -> Project | None:
        """
        Retrieves a Project owned by the user with the specified slug.
        """
        statement = select(Project).where(
            Project.owner_id == owner_id,
            Project.slug == slug
        )
        return self.db.scalar(statement)

    def list_by_owner(self, owner_id: uuid.UUID) -> list[Project]:
        """
        Lists all projects owned by the specified user.
        """
        statement = select(Project).where(Project.owner_id == owner_id).order_by(Project.created_at.desc())
        return list(self.db.scalars(statement).all())

    def list_projects_paginated(
        self,
        owner_id: uuid.UUID,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        order: str = "desc",
        search: str | None = None,
        visibility: ProjectVisibility | None = None,
    ) -> tuple[list[Project], int]:
        """
        Lists projects visible to the owner with database-level pagination,
        sorting, search, and visibility filtering.
        Returns a tuple of (items, total_count).
        """
        access_condition = or_(
            Project.owner_id == owner_id,
            Project.visibility == ProjectVisibility.PUBLIC
        )

        conditions = [access_condition]

        if search and search.strip():
            term = f"%{search.strip()}%"
            conditions.append(
                or_(
                    Project.name.ilike(term),
                    Project.description.ilike(term)
                )
            )

        if visibility is not None:
            conditions.append(Project.visibility == visibility)

        count_statement = select(func.count()).select_from(Project).where(*conditions)
        total = self.db.scalar(count_statement) or 0

        sort_attr = getattr(Project, sort_by, Project.created_at)
        order_clause = sort_attr.asc() if order == "asc" else sort_attr.desc()

        offset_val = (page - 1) * size
        items_statement = (
            select(Project)
            .where(*conditions)
            .order_by(order_clause)
            .offset(offset_val)
            .limit(size)
        )
        items = list(self.db.scalars(items_statement).all())

        return items, total


    def create(self, project: Project) -> Project:
        """
        Adds a new Project entity to the database session and flushes it.
        """
        self.db.add(project)
        self.db.flush()
        return project

    def update(self, project: Project) -> Project:
        """
        Flushes modifications to the Project model in the database session.
        """
        self.db.flush()
        return project

    def delete(self, project: Project) -> None:
        """
        Deletes a Project entity from the database session.
        """
        self.db.delete(project)
        self.db.flush()

    def slug_exists(self, owner_id: uuid.UUID, slug: str) -> bool:
        """
        Checks if a project slug is already taken by the given owner.
        """
        statement = select(Project.id).where(
            Project.owner_id == owner_id,
            Project.slug == slug
        )
        return self.db.scalar(statement) is not None
