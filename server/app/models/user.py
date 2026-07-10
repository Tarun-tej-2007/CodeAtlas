from typing import TYPE_CHECKING
from sqlalchemy import String, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.base import TimestampMixin, UUIDMixin
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.project import Project

class User(Base, UUIDMixin, TimestampMixin):
    """
    SQLAlchemy ORM model representing a platform User.
    
    Responsible for core authentication identity, roles, and ownership
    of project workspaces.
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.MEMBER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    # One-to-Many: A user can own multiple projects/workspaces.
    # CASCADE: Deleting a User hard-deletes all owned projects and repositories.
    projects: Mapped[list["Project"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}', role='{self.role}')>"
