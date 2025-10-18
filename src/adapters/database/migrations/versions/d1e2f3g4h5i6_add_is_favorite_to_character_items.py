"""add_is_favorite_to_character_items

Revision ID: d1e2f3g4h5i6
Revises: c09a31934a35
Create Date: 2025-10-18 12:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "d1e2f3g4h5i6"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6g7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    conn = op.get_bind()
    inspector = inspect(conn)

    columns = [col["name"] for col in inspector.get_columns("character_items")]

    if "is_favorite" in columns:

        pass
    elif "is_favourite" in columns:

        op.alter_column(
            "character_items", "is_favourite", new_column_name="is_favorite"
        )
    else:

        op.add_column(
            "character_items",
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

    columns = [col["name"] for col in inspector.get_columns("character_items")]

    if "is_favorite" in columns:
        op.drop_column("character_items", "is_favorite")
