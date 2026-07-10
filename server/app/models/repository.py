import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Enum, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.base import TimestampMixin, UUIDMixin
from app.models.enums import RepositoryProvider, RepositoryStatus

if TYPE_CHECKING:
    from app.models.project import Project

class Repository(Base, UUIDMixin, TimestampMixin):
    """
    SQLAlchemy ORM model representing a Git Repository configuration.
    
    Houses cloning paths, git providers, execution sync states, and
    logical references to target codebase branches.
    """
    __tablename__ = "repositories"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    provider: Mapped[RepositoryProvider] = mapped_column(
        Enum(RepositoryProvider, native_enum=False),
        nullable=False,
    )
    clone_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    default_branch: Mapped[str] = mapped_column(
        String(100),
        default="main",
        nullable=False,
    )
    status: Mapped[RepositoryStatus] = mapped_column(
        Enum(RepositoryStatus, native_enum=False),
        default=RepositoryStatus.PENDING,
        nullable=False,
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    # Many-to-One: A repository belongs to a single project workspace namespace.
    project: Mapped["Project"] = relationship(back_populates="repositories")

    def __repr__(self) -> str:
        return f"<Repository(id={self.id}, project_id={self.project_id}, name='{self.name}', provider='{self.provider}', status='{self.status}')>"

    __table_args__ = (
        UniqueConstraint("project_id", "clone_url", name="uq_repositories_project_clone_url"),
        Index("ix_repositories_project_id_status", "project_id", "status"),
    )
