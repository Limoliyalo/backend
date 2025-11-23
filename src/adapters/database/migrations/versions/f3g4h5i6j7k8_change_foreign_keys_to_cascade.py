"""change_foreign_keys_to_cascade

Revision ID: f3g4h5i6j7k8
Revises: e2f3g4h5i6j7
Create Date: 2025-11-23 22:15:00.000000

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "f3g4h5i6j7k8"
down_revision: Union[str, Sequence[str], None] = "7e0246842c09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - change RESTRICT to CASCADE for foreign keys."""

    conn = op.get_bind()
    inspector = inspect(conn)

    # Функция для поиска и изменения foreign key constraint
    def change_fk_constraint(
        table_name: str, column_name: str, ref_table: str, ref_column: str
    ):
        # Находим foreign key constraints для таблицы
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            if column_name in fk["constrained_columns"]:
                constraint_name = fk["name"]
                op.drop_constraint(constraint_name, table_name, type_="foreignkey")
                op.create_foreign_key(
                    constraint_name,
                    table_name,
                    ref_table,
                    [column_name],
                    [ref_column],
                    ondelete="CASCADE",
                )
                break

    # Изменяем foreign key для base_character_activities.activity_type_id
    change_fk_constraint(
        "base_character_activities", "activity_type_id", "activity_types", "id"
    )

    # Изменяем foreign key для character_activity_history.activity_type_id
    change_fk_constraint(
        "character_activity_history", "activity_type_id", "activity_types", "id"
    )

    # Изменяем foreign key для character_items.item_id
    change_fk_constraint("character_items", "item_id", "items", "id")

    # Изменяем foreign key для character_backgrounds.background_id
    change_fk_constraint("character_backgrounds", "background_id", "backgrounds", "id")


def downgrade() -> None:
    """Downgrade schema - change CASCADE back to RESTRICT for foreign keys."""

    conn = op.get_bind()
    inspector = inspect(conn)

    # Функция для поиска и изменения foreign key constraint
    def change_fk_constraint(
        table_name: str, column_name: str, ref_table: str, ref_column: str
    ):
        # Находим foreign key constraints для таблицы
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            if column_name in fk["constrained_columns"]:
                constraint_name = fk["name"]
                op.drop_constraint(constraint_name, table_name, type_="foreignkey")
                op.create_foreign_key(
                    constraint_name,
                    table_name,
                    ref_table,
                    [column_name],
                    [ref_column],
                    ondelete="RESTRICT",
                )
                break

    # Возвращаем RESTRICT для character_backgrounds.background_id
    change_fk_constraint("character_backgrounds", "background_id", "backgrounds", "id")

    # Возвращаем RESTRICT для character_items.item_id
    change_fk_constraint("character_items", "item_id", "items", "id")

    # Возвращаем RESTRICT для character_activity_history.activity_type_id
    change_fk_constraint(
        "character_activity_history", "activity_type_id", "activity_types", "id"
    )

    # Возвращаем RESTRICT для base_character_activities.activity_type_id
    change_fk_constraint(
        "base_character_activities", "activity_type_id", "activity_types", "id"
    )
