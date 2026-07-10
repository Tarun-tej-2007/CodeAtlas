# Import SQLAlchemy Declarative Base
from app.db.database import Base

# Import all models here so that they are registered on Base.metadata
# prior to Alembic running autogenerate migrations.
from app.models.user import User  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.repository import Repository  # noqa: F401

# Export Base so Alembic env.py can reference it
__all__ = ["Base"]
