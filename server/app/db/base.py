# Import SQLAlchemy Declarative Base
from app.db.database import Base

# Import all models here so that they are registered on Base.metadata
# prior to Alembic running autogenerate migrations.
# Example:
# from app.models.user import User  # noqa
# from app.models.project import Project  # noqa
# from app.models.repository import Repository  # noqa

# Export Base so Alembic env.py can reference it
__all__ = ["Base"]
