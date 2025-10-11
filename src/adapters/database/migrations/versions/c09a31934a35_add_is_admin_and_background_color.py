"""add_is_admin_and_background_color

Revision ID: c09a31934a35
Revises: 1c86fc7ff822
Create Date: 2025-10-11 16:59:33.110071

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c09a31934a35"
down_revision: Union[str, Sequence[str], None] = "1c86fc7ff822"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавить поле is_admin в таблицу users
    op.add_column(
        "users",
        sa.Column(
            "is_admin", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
    )

    # Добавить поле color в таблицу backgrounds
    op.add_column(
        "backgrounds", sa.Column("color", sa.String(length=30), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удалить поле color из таблицы backgrounds
    op.drop_column("backgrounds", "color")

    # Удалить поле is_admin из таблицы users
    op.drop_column("users", "is_admin")
