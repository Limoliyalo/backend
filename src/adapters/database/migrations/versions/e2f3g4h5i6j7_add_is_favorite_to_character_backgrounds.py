"""add_is_favorite_to_character_backgrounds

Revision ID: e2f3g4h5i6j7
Revises: d1e2f3g4h5i6
Create Date: 2025-10-18 12:25:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "e2f3g4h5i6j7"
down_revision: Union[str, Sequence[str], None] = "d1e2f3g4h5i6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    conn = op.get_bind()
    inspector = inspect(conn)

    columns = [col["name"] for col in inspector.get_columns("character_backgrounds")]

    if "is_favorite" in columns:

        pass
    elif "is_favourite" in columns:

        op.alter_column(
            "character_backgrounds", "is_favourite", new_column_name="is_favorite"
        )
    else:

        op.add_column(
            "character_backgrounds",
            sa.Column(
                "is_favorite",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )


def downgrade() -> None:
    """Downgrade schema."""

    conn = op.get_bind()
    inspector = inspect(conn)

    columns = [col["name"] for col in inspector.get_columns("character_backgrounds")]

    if "is_favorite" in columns:
        op.drop_column("character_backgrounds", "is_favorite")
