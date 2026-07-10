import uuid
from typing import TYPE_CHECKING
from sqlalchemy import String, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.base import TimestampMixin, UUIDMixin
from app.models.enums import Visibility

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.repository import Repository

class Project(Base, UUIDMixin, TimestampMixin):
    """
    SQLAlchemy ORM model representing a Project workspace.
    
    Acts as a logical boundary and isolation namespace for grouping 
    multiple repositories under a single tenant workspace.
    """
    __tablename__ = "projects"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    visibility: Mapped[Visibility] = mapped_column(
        Enum(Visibility, native_enum=False),
        default=Visibility.PRIVATE,
        nullable=False,
    )

    # Relationships
    # Many-to-One: A project is owned by a single user.
    owner: Mapped["User"] = relationship(back_populates="projects")
    
    # One-to-Many: A project workspace can contain multiple repositories.
    # CASCADE: Deleting a project hard-deletes all its mapped repository configs.
    repositories: Mapped[list["Repository"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, owner_id={self.owner_id}, name='{self.name}', visibility='{self.visibility}')>"

    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_projects_owner_name"),
    )
