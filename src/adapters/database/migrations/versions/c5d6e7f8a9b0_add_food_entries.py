"""add_food_entries

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
Create Date: 2026-06-05 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "c5d6e7f8a9b0"
down_revision: Union[str, Sequence[str], None] = "b4c5d6e7f8a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "food_entries",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "character_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("characters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("consumed_at", sa.DateTime(), nullable=False),
        sa.Column("meal_type", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=True),
        sa.Column("calories", sa.Integer(), nullable=False),
        sa.Column("protein_g", sa.Integer(), nullable=True),
        sa.Column("fat_g", sa.Integer(), nullable=True),
        sa.Column("carbs_g", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("calories > 0", name="ck_food_entries_calories_positive"),
        sa.CheckConstraint(
            "protein_g >= 0 OR protein_g IS NULL",
            name="ck_food_entries_protein_non_negative",
        ),
        sa.CheckConstraint(
            "fat_g >= 0 OR fat_g IS NULL",
            name="ck_food_entries_fat_non_negative",
        ),
        sa.CheckConstraint(
            "carbs_g >= 0 OR carbs_g IS NULL",
            name="ck_food_entries_carbs_non_negative",
        ),
    )
    op.create_index(
        "idx_food_entries_character_consumed_at",
        "food_entries",
        ["character_id", "consumed_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_food_entries_character_consumed_at", table_name="food_entries")
    op.drop_table("food_entries")
