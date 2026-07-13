import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.project import Project

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
