"""add_blacklisted_tokens_table

Revision ID: a1b2c3d4e5f6
Revises: 60f31b6f3f71
Create Date: 2025-10-12 18:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "60f31b6f3f71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "blacklisted_tokens",
        sa.Column("jti", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "reason",
            sa.String(length=50),
            nullable=False,
            server_default="logout",
            comment="Reason for blacklisting (logout, revoke_all, etc.)",
        ),
        sa.Column(
            "blacklisted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment="When the token was blacklisted",
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="When the token would have expired (for cleanup)",
        ),
    )
    op.create_index(
        "ix_blacklisted_tokens_user_tg_id",
        "blacklisted_tokens",
        ["user_tg_id"],
        unique=False,
    )
    op.create_index(
        "ix_blacklisted_tokens_expires_at",
        "blacklisted_tokens",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_blacklisted_tokens_expires_at", table_name="blacklisted_tokens")
    op.drop_index("ix_blacklisted_tokens_user_tg_id", table_name="blacklisted_tokens")
    op.drop_table("blacklisted_tokens")
