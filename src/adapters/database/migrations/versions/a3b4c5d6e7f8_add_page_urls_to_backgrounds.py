"""add_page_urls_to_backgrounds

Revision ID: a3b4c5d6e7f8
Revises: 9a2c1d4e6f80
Create Date: 2026-04-02 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a3b4c5d6e7f8"
down_revision: Union[str, Sequence[str], None] = "9a2c1d4e6f80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("backgrounds", sa.Column("shop_url", sa.String(500), nullable=True))
    op.add_column("backgrounds", sa.Column("profile_url", sa.String(500), nullable=True))
    op.add_column("backgrounds", sa.Column("settings_url", sa.String(500), nullable=True))
    op.add_column("backgrounds", sa.Column("friends_url", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("backgrounds", "friends_url")
    op.drop_column("backgrounds", "settings_url")
    op.drop_column("backgrounds", "profile_url")
    op.drop_column("backgrounds", "shop_url")
