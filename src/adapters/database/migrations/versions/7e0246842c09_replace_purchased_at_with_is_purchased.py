"""replace_purchased_at_with_is_purchased_and_add_picture_url_and_activities_refactor

Revision ID: 7e0246842c09
Revises: e2f3g4h5i6j7
Create Date: 2025-11-23 22:47:35.673288

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "7e0246842c09"
down_revision: Union[str, Sequence[str], None] = "e2f3g4h5i6j7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = inspect(conn)

    # Для character_items
    columns = [col["name"] for col in inspector.get_columns("character_items")]

    # Проверяем наличие purchased_at перед использованием
    has_purchased_at = "purchased_at" in columns

    if "is_purchased" not in columns:
        # Добавляем is_purchased с временным значением
        op.add_column(
            "character_items",
            sa.Column(
                "is_purchased",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )

        # Устанавливаем is_purchased=True для всех записей, где purchased_at не NULL
        # Только если purchased_at существует
        if has_purchased_at:
            op.execute(
                sa.text(
                    "UPDATE character_items SET is_purchased = true WHERE purchased_at IS NOT NULL"
                )
            )

    # Обновляем view v_character_inventory перед удалением колонки
    # Сначала удаляем view, чтобы избежать конфликтов при изменении структуры
    views = inspector.get_view_names()
    if "v_character_inventory" in views:
        op.execute(sa.text("DROP VIEW IF EXISTS v_character_inventory"))

    # Создаем view заново с новой структурой (используя is_purchased вместо purchased_at)
    op.execute(
        sa.text(
            """
            CREATE OR REPLACE VIEW v_character_inventory AS
            SELECT
                ci.character_id,
                i.id AS item_id,
                i.name AS item_name,
                ic.name AS category_name,
                ci.is_active,
                ci.is_favorite,
                ci.is_purchased
            FROM character_items ci
            JOIN items i ON ci.item_id = i.id
            JOIN item_categories ic ON i.category_id = ic.id;
            """
        )
    )

    if has_purchased_at:
        op.drop_column("character_items", "purchased_at")

    # Для character_backgrounds
    columns = [col["name"] for col in inspector.get_columns("character_backgrounds")]

    # Проверяем наличие purchased_at перед использованием
    has_purchased_at = "purchased_at" in columns

    if "is_purchased" not in columns:
        # Добавляем is_purchased с временным значением
        op.add_column(
            "character_backgrounds",
            sa.Column(
                "is_purchased",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )

        # Устанавливаем is_purchased=True для всех записей, где purchased_at не NULL
        # Только если purchased_at существует
        if has_purchased_at:
            op.execute(
                sa.text(
                    "UPDATE character_backgrounds SET is_purchased = true WHERE purchased_at IS NOT NULL"
                )
            )

    # Проверяем, есть ли view, которые используют purchased_at из character_backgrounds
    # (пока не найдено, но на всякий случай оставляем место для будущих view)

    if has_purchased_at:
        op.drop_column("character_backgrounds", "purchased_at")

    # Добавляем picture_url в items
    items_columns = [col["name"] for col in inspector.get_columns("items")]
    if "picture_url" not in items_columns:
        op.add_column(
            "items",
            sa.Column(
                "picture_url",
                sa.String(length=500),
                nullable=True,
            ),
        )

    # Добавляем picture_url в backgrounds
    backgrounds_columns = [col["name"] for col in inspector.get_columns("backgrounds")]
    if "picture_url" not in backgrounds_columns:
        op.add_column(
            "backgrounds",
            sa.Column(
                "picture_url",
                sa.String(length=500),
                nullable=True,
            ),
        )

    # Переименовываем daily_activities в character_activity_history
    if inspector.has_table("daily_activities") and not inspector.has_table(
        "character_activity_history"
    ):
        op.rename_table("daily_activities", "character_activity_history")

        # Переименовываем индексы и constraints
        op.execute(
            sa.text(
                """
            ALTER INDEX IF EXISTS idx_daily_activities_character_date 
            RENAME TO idx_character_activity_history_character_date
        """
            )
        )
        op.execute(
            sa.text(
                """
            ALTER INDEX IF EXISTS idx_daily_activities_type 
            RENAME TO idx_character_activity_history_type
        """
            )
        )
        op.execute(
            sa.text(
                """
            ALTER INDEX IF EXISTS idx_daily_activities_date 
            RENAME TO idx_character_activity_history_date
        """
            )
        )
        op.execute(
            sa.text(
                """
            ALTER TABLE character_activity_history 
            RENAME CONSTRAINT uq_daily_activity TO uq_character_activity_history
        """
            )
        )
        op.execute(
            sa.text(
                """
            ALTER TABLE character_activity_history 
            RENAME CONSTRAINT ck_daily_activities_value_non_negative 
            TO ck_character_activity_history_value_non_negative
        """
            )
        )
        op.execute(
            sa.text(
                """
            ALTER TABLE character_activity_history 
            RENAME CONSTRAINT ck_daily_activities_goal_positive 
            TO ck_character_activity_history_goal_positive
        """
            )
        )

    # Создаем таблицу base_character_activities
    if not inspector.has_table("base_character_activities"):
        op.create_table(
            "base_character_activities",
            sa.Column(
                "id",
                sa.dialects.postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("uuid_generate_v4()"),
            ),
            sa.Column(
                "character_id",
                sa.dialects.postgresql.UUID(as_uuid=True),
                sa.ForeignKey("characters.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "activity_type_id",
                sa.dialects.postgresql.UUID(as_uuid=True),
                sa.ForeignKey("activity_types.id", ondelete="RESTRICT"),
                nullable=False,
            ),
            sa.Column("goal", sa.Integer(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("NOW()"),
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("NOW()"),
            ),
            sa.UniqueConstraint(
                "character_id", "activity_type_id", name="uq_base_character_activity"
            ),
            sa.CheckConstraint(
                "goal > 0", name="ck_base_character_activities_goal_positive"
            ),
        )

        # Создаем индексы
        op.create_index(
            "idx_base_character_activities_character",
            "base_character_activities",
            ["character_id"],
        )
        op.create_index(
            "idx_base_character_activities_type",
            "base_character_activities",
            ["activity_type_id"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspector = inspect(conn)

    # Для character_items
    columns = [col["name"] for col in inspector.get_columns("character_items")]

    if "is_purchased" in columns:
        op.drop_column("character_items", "is_purchased")

    if "purchased_at" not in columns:
        op.add_column(
            "character_items",
            sa.Column(
                "purchased_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )
        # Восстанавливаем view с purchased_at
        views = inspector.get_view_names()
        if "v_character_inventory" in views:
            op.execute(
                sa.text(
                    """
                    CREATE OR REPLACE VIEW v_character_inventory AS
                    SELECT
                        ci.character_id,
                        i.id AS item_id,
                        i.name AS item_name,
                        ic.name AS category_name,
                        ci.is_active,
                        ci.is_favorite,
                        ci.purchased_at
                    FROM character_items ci
                    JOIN items i ON ci.item_id = i.id
                    JOIN item_categories ic ON i.category_id = ic.id;
                    """
                )
            )

    # Для character_backgrounds
    columns = [col["name"] for col in inspector.get_columns("character_backgrounds")]

    if "purchased_at" not in columns:
        op.add_column(
            "character_backgrounds",
            sa.Column(
                "purchased_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )

    if "is_purchased" in columns:
        op.drop_column("character_backgrounds", "is_purchased")

    # Удаляем picture_url из items
    items_columns = [col["name"] for col in inspector.get_columns("items")]
    if "picture_url" in items_columns:
        op.drop_column("items", "picture_url")

    # Удаляем picture_url из backgrounds
    backgrounds_columns = [col["name"] for col in inspector.get_columns("backgrounds")]
    if "picture_url" in backgrounds_columns:
        op.drop_column("backgrounds", "picture_url")

    # Переименовываем character_activity_history обратно в daily_activities
    if inspector.has_table("character_activity_history") and not inspector.has_table(
        "daily_activities"
    ):
        op.rename_table("character_activity_history", "daily_activities")

        # Переименовываем индексы и constraints обратно
        op.execute(
            sa.text(
                """
            ALTER INDEX IF EXISTS idx_character_activity_history_character_date 
            RENAME TO idx_daily_activities_character_date
        """
            )
        )
        op.execute(
            sa.text(
                """
            ALTER INDEX IF EXISTS idx_character_activity_history_type 
            RENAME TO idx_daily_activities_type
        """
            )
        )
        op.execute(
            sa.text(
                """
            ALTER INDEX IF EXISTS idx_character_activity_history_date 
            RENAME TO idx_daily_activities_date
        """
            )
        )
        op.execute(
            sa.text(
                """
            ALTER TABLE daily_activities 
            RENAME CONSTRAINT uq_character_activity_history TO uq_daily_activity
        """
            )
        )
        op.execute(
            sa.text(
                """
            ALTER TABLE daily_activities 
            RENAME CONSTRAINT ck_character_activity_history_value_non_negative 
            TO ck_daily_activities_value_non_negative
        """
            )
        )
        op.execute(
            sa.text(
                """
            ALTER TABLE daily_activities 
            RENAME CONSTRAINT ck_character_activity_history_goal_positive 
            TO ck_daily_activities_goal_positive
        """
            )
        )

    # Удаляем таблицу base_character_activities
    if inspector.has_table("base_character_activities"):
        op.drop_index(
            "idx_base_character_activities_type", table_name="base_character_activities"
        )
        op.drop_index(
            "idx_base_character_activities_character",
            table_name="base_character_activities",
        )
        op.drop_table("base_character_activities")
