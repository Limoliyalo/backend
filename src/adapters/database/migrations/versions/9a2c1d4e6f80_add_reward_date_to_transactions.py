"""add_reward_date_to_transactions

Revision ID: 9a2c1d4e6f80
Revises: f3g4h5i6j7k8
Create Date: 2026-03-30 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "9a2c1d4e6f80"
down_revision: Union[str, Sequence[str], None] = "f3g4h5i6j7k8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("transactions", sa.Column("reward_date", sa.Date(), nullable=True))

    op.create_index(
        "uq_transactions_user_reward_date",
        "transactions",
        ["user_tg_id", "reward_date"],
        unique=True,
        postgresql_where=sa.text("reward_date IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_transactions_user_reward_date", table_name="transactions")
    op.drop_column("transactions", "reward_date")

