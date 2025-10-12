"""add_refresh_tokens_table

Revision ID: 60f31b6f3f71
Revises: c09a31934a35
Create Date: 2025-10-12 16:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "60f31b6f3f71"
down_revision: Union[str, Sequence[str], None] = "c09a31934a35"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("jti", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["user_tg_id"], ["users.tg_id"], ondelete="CASCADE"),
        sa.UniqueConstraint("jti", name="uq_refresh_tokens_jti"),
    )
    op.create_index(
        "ix_refresh_tokens_user_tg_id", "refresh_tokens", ["user_tg_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_refresh_tokens_user_tg_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
