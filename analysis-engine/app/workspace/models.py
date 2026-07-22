"""Workspace data models module."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import uuid


@dataclass(frozen=True)
class Workspace:
    """Immutable runtime representation of an isolated analysis workspace."""

    id: uuid.UUID
    analysis_id: uuid.UUID
    path: Path
    created_at: datetime
