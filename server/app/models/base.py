import uuid
from datetime import datetime
from sqlalchemy import func, DateTime
from sqlalchemy.orm import Mapped, mapped_column

class TimestampMixin:
    """
    Mixin class to inherit timezone-aware created_at and updated_at datetime properties.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

class UUIDMixin:
    """
    Mixin class to inherit auto-generated UUID primary keys.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
        nullable=False,
    )
