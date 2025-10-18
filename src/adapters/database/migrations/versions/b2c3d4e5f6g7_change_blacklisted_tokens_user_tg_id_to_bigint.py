"""change_blacklisted_tokens_user_tg_id_to_bigint

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-10-12 18:55:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - change user_tg_id to BIGINT."""

    op.execute(
        """
        ALTER TABLE blacklisted_tokens 
        ALTER COLUMN user_tg_id TYPE BIGINT 
        USING user_tg_id::BIGINT
        """
    )


def downgrade() -> None:
    """Downgrade schema - change user_tg_id back to INTEGER."""

    op.execute(
        """
        ALTER TABLE blacklisted_tokens 
        ALTER COLUMN user_tg_id TYPE INTEGER 
        USING user_tg_id::INTEGER
        """
    )
