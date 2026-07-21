"""convert_project_visibility_to_lowercase

Revision ID: a4c92b871234
Revises: 91692e15d625
Create Date: 2026-07-21 09:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4c92b871234'
down_revision: Union[str, None] = '91692e15d625'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert existing stored enum string values to lowercase safely and idempotently
    op.execute("UPDATE projects SET visibility = 'private' WHERE visibility = 'PRIVATE'")
    op.execute("UPDATE projects SET visibility = 'public' WHERE visibility = 'PUBLIC'")


def downgrade() -> None:
    op.execute("UPDATE projects SET visibility = 'PRIVATE' WHERE visibility = 'private'")
    op.execute("UPDATE projects SET visibility = 'PUBLIC' WHERE visibility = 'public'")
