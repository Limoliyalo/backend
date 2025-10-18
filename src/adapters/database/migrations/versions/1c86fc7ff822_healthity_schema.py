"""Add Healthity schema objects

Revision ID: 1c86fc7ff822
Revises: 5b0e3c0b1b8f
Create Date: 2025-10-11 03:10:20.206946

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "1c86fc7ff822"
down_revision: Union[str, Sequence[str], None] = "5b0e3c0b1b8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_index_if_exists(
    inspector: sa.engine.reflection.Inspector, table: str, name: str
) -> None:
    if table not in inspector.get_table_names():
        return
    indexes = {index["name"] for index in inspector.get_indexes(table)}
    if name in indexes:
        op.drop_index(name, table_name=table)


def upgrade() -> None:
    connection = op.get_bind()
    inspector = inspect(connection)

    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    _drop_index_if_exists(inspector, "pictures", "ix_pictures_telegram_id")
    if "pictures" in inspector.get_table_names():
        op.drop_table("pictures")

    _drop_index_if_exists(inspector, "users", "ix_users_telegram_id")
    if "users" in inspector.get_table_names():
        op.rename_table("users", "users_old")

    op.create_table(
        "users",
        sa.Column("tg_id", sa.BigInteger(), primary_key=True),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column("balance", sa.Integer(), nullable=False, server_default=sa.text("0")),
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
        sa.CheckConstraint("balance >= 0", name="ck_users_balance_non_negative"),
    )

    if "users_old" in inspector.get_table_names():
        op.execute(
            """
            INSERT INTO users (tg_id, password_hash, is_active, balance, created_at, updated_at)
            SELECT telegram_id, NULL, true, COALESCE(coins, 0), created_at, updated_at
            FROM users_old
            """
        )
        op.drop_table("users_old")

    op.create_table(
        "user_settings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_tg_id",
            sa.BigInteger(),
            sa.ForeignKey("users.tg_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("quiet_start_time", sa.Time(), nullable=True),
        sa.Column("quiet_end_time", sa.Time(), nullable=True),
        sa.Column(
            "muted_days",
            postgresql.ARRAY(sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::text[]"),
        ),
        sa.Column(
            "do_not_disturb",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
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
    )

    op.create_table(
        "user_friends",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "owner_tg_id",
            sa.BigInteger(),
            sa.ForeignKey("users.tg_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "friend_tg_id",
            sa.BigInteger(),
            sa.ForeignKey("users.tg_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint("owner_tg_id", "friend_tg_id", name="uq_user_friend_pair"),
        sa.CheckConstraint("owner_tg_id <> friend_tg_id", name="ck_user_friend_self"),
    )

    op.create_table(
        "item_categories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    op.create_table(
        "backgrounds",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cost", sa.Integer(), nullable=False),
        sa.Column(
            "required_level", sa.Integer(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column(
            "is_available", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint("cost >= 0", name="ck_backgrounds_cost_non_negative"),
        sa.CheckConstraint(
            "required_level >= 1", name="ck_backgrounds_required_level_positive"
        ),
    )

    op.create_table(
        "items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("item_categories.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cost", sa.Integer(), nullable=False),
        sa.Column(
            "required_level", sa.Integer(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column(
            "is_available", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
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
        sa.CheckConstraint("cost >= 0", name="ck_items_cost_non_negative"),
        sa.CheckConstraint(
            "required_level >= 1", name="ck_items_required_level_positive"
        ),
    )

    op.create_table(
        "characters",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_tg_id",
            sa.BigInteger(),
            sa.ForeignKey("users.tg_id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("name", sa.String(length=100), nullable=True),
        sa.Column("sex", sa.String(length=20), nullable=True),
        sa.Column(
            "current_mood",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'neutral'"),
        ),
        sa.Column("level", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "total_experience",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
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
        sa.CheckConstraint("level >= 1", name="ck_characters_level_positive"),
        sa.CheckConstraint(
            "total_experience >= 0", name="ck_characters_experience_non_negative"
        ),
        sa.CheckConstraint(
            "sex IN ('male','female','other') OR sex IS NULL",
            name="ck_characters_sex_enum",
        ),
    )

    op.create_table(
        "character_items",
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
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "is_favorite",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "purchased_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint("character_id", "item_id", name="uq_character_item"),
    )

    op.create_table(
        "character_backgrounds",
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
        sa.Column(
            "background_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("backgrounds.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "is_favorite",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "purchased_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.UniqueConstraint(
            "character_id", "background_id", name="uq_character_background"
        ),
    )

    op.create_table(
        "item_background_positions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "background_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("backgrounds.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position_x", sa.Numeric(10, 2), nullable=False),
        sa.Column("position_y", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "position_z", sa.Numeric(10, 2), nullable=False, server_default=sa.text("0")
        ),
        sa.UniqueConstraint(
            "item_id", "background_id", name="uq_item_background_position"
        ),
    )

    op.create_table(
        "activity_types",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
        sa.Column("unit", sa.String(length=20), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("daily_goal_default", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    op.create_table(
        "daily_progress",
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
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column(
            "experience_gained",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("level_at_end", sa.Integer(), nullable=False),
        sa.Column("mood_average", sa.String(length=50), nullable=True),
        sa.Column("behavior_index", sa.Integer(), nullable=True),
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
        sa.UniqueConstraint("character_id", "date", name="uq_daily_progress"),
        sa.CheckConstraint(
            "experience_gained >= 0", name="ck_daily_progress_experience_non_negative"
        ),
        sa.CheckConstraint(
            "level_at_end >= 1", name="ck_daily_progress_level_positive"
        ),
        sa.CheckConstraint(
            "behavior_index BETWEEN 0 AND 100 OR behavior_index IS NULL",
            name="ck_daily_progress_behavior_index_range",
        ),
    )

    op.create_table(
        "daily_activities",
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
        sa.Column(
            "activity_type_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("activity_types.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("value", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("goal", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
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
            "character_id", "activity_type_id", "date", name="uq_daily_activity"
        ),
        sa.CheckConstraint("value >= 0", name="ck_daily_activities_value_non_negative"),
        sa.CheckConstraint("goal > 0", name="ck_daily_activities_goal_positive"),
    )

    op.create_table(
        "mood_history",
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
        sa.Column("mood", sa.String(length=50), nullable=False),
        sa.Column("trigger", sa.Text(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    op.create_table(
        "transactions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "user_tg_id",
            sa.BigInteger(),
            sa.ForeignKey("users.tg_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column(
            "related_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "related_background_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("backgrounds.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.CheckConstraint(
            "balance_after >= 0", name="ck_transactions_balance_non_negative"
        ),
    )

    op.create_index("idx_users_is_active", "users", ["is_active"])
    op.create_index("idx_users_created_at", "users", ["created_at"])
    op.create_index("idx_user_settings_user", "user_settings", ["user_tg_id"])
    op.create_index("idx_user_friends_owner", "user_friends", ["owner_tg_id"])
    op.create_index("idx_user_friends_friend", "user_friends", ["friend_tg_id"])
    op.create_index("idx_backgrounds_required_level", "backgrounds", ["required_level"])
    op.create_index("idx_backgrounds_available", "backgrounds", ["is_available"])
    op.create_index("idx_items_category", "items", ["category_id"])
    op.create_index("idx_items_required_level", "items", ["required_level"])
    op.create_index("idx_items_available", "items", ["is_available"])
    op.create_index("idx_characters_user", "characters", ["user_tg_id"])
    op.create_index("idx_characters_level", "characters", ["level"])
    op.create_index(
        "idx_character_items_character", "character_items", ["character_id"]
    )
    op.create_index(
        "idx_character_items_active",
        "character_items",
        ["character_id", "is_active"],
        postgresql_where=sa.text("is_active = true"),
    )
    op.create_index(
        "idx_character_items_favourite",
        "character_items",
        ["character_id", "is_favorite"],
        postgresql_where=sa.text("is_favorite = true"),
    )
    op.create_index(
        "idx_character_backgrounds_character", "character_backgrounds", ["character_id"]
    )
    op.create_index(
        "idx_character_backgrounds_active",
        "character_backgrounds",
        ["character_id", "is_active"],
        postgresql_where=sa.text("is_active = true"),
    )
    op.create_index(
        "idx_item_bg_positions_item", "item_background_positions", ["item_id"]
    )
    op.create_index(
        "idx_item_bg_positions_bg", "item_background_positions", ["background_id"]
    )
    op.create_index(
        "idx_daily_activities_type", "daily_activities", ["activity_type_id"]
    )
    op.create_index(
        "idx_transactions_user_time", "transactions", ["user_tg_id", "timestamp"]
    )
    op.create_index("idx_transactions_type", "transactions", ["type"])
    op.create_index("idx_transactions_timestamp", "transactions", ["timestamp"])

    op.execute(
        "CREATE INDEX idx_daily_progress_character_date ON daily_progress (character_id, date DESC)"
    )
    op.execute("CREATE INDEX idx_daily_progress_date ON daily_progress (date DESC)")
    op.execute(
        "CREATE INDEX idx_daily_activities_character_date ON daily_activities (character_id, date DESC)"
    )
    op.execute("CREATE INDEX idx_daily_activities_date ON daily_activities (date DESC)")
    op.execute(
        "CREATE INDEX idx_mood_history_character_time ON mood_history (character_id, timestamp DESC)"
    )
    op.execute(
        "CREATE INDEX idx_mood_history_timestamp ON mood_history (timestamp DESC)"
    )
    op.execute(
        "CREATE INDEX idx_transactions_timestamp_desc ON transactions (timestamp DESC)"
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    for table_name in (
        "users",
        "user_settings",
        "characters",
        "items",
        "daily_progress",
        "daily_activities",
    ):
        op.execute(
            sa.text(
                "CREATE TRIGGER update_{0}_updated_at BEFORE UPDATE ON {0} "
                "FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()".format(
                    table_name
                )
            )
        )

    op.execute(
        """
        INSERT INTO activity_types (name, unit, color, daily_goal_default)
        VALUES
            ('water', 'ml', '#2196F3', 2000),
            ('food', 'kcal', '#4CAF50', 2000),
            ('exercise', 'minutes', '#FF9800', 30),
            ('sleep', 'hours', '#9C27B0', 8),
            ('meditation', 'minutes', '#00BCD4', 15),
            ('steps', 'steps', '#8BC34A', 10000),
            ('reading', 'minutes', '#795548', 30)
        ON CONFLICT (name) DO NOTHING;
        """
    )

    op.execute(
        """
        INSERT INTO item_categories (name, description)
        VALUES
            ('clothing', 'Одежда для персонажа'),
            ('accessories', 'Аксессуары и украшения'),
            ('hairstyles', 'Прически'),
            ('pets', 'Питомцы'),
            ('furniture', 'Мебель для комнаты'),
            ('effects', 'Визуальные эффекты')
        ON CONFLICT (name) DO NOTHING;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW v_character_stats AS
        SELECT
            c.id AS character_id,
            c.name AS character_name,
            c.level,
            c.total_experience,
            c.current_mood,
            u.tg_id,
            u.balance,
            u.is_active AS user_active
        FROM characters c
        JOIN users u ON c.user_tg_id = u.tg_id;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE VIEW v_daily_activity_summary AS
        SELECT
            da.character_id,
            da.date,
            COUNT(DISTINCT da.activity_type_id) AS activities_tracked,
            SUM(CASE WHEN da.value >= da.goal THEN 1 ELSE 0 END) AS goals_achieved,
            AVG(CASE WHEN da.goal > 0 THEN (da.value::float / da.goal) * 100 ELSE 0 END) AS average_completion_percent
        FROM daily_activities da
        GROUP BY da.character_id, da.date;
        """
    )

    op.execute(
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

    op.execute("COMMENT ON TABLE users IS 'Реальные пользователи Telegram'")
    op.execute("COMMENT ON TABLE characters IS 'Виртуальные персонажи пользователей'")
    op.execute(
        "COMMENT ON TABLE daily_activities IS 'Ежедневные активности персонажа (вода, еда, упражнения и т.д.)'"
    )
    op.execute(
        "COMMENT ON TABLE daily_progress IS 'Исторический прогресс персонажа по дням'"
    )
    op.execute(
        "COMMENT ON TABLE transactions IS 'История финансовых операций (покупки, награды и т.д.)'"
    )


def downgrade() -> None:
    for view in (
        "v_character_inventory",
        "v_daily_activity_summary",
        "v_character_stats",
    ):
        op.execute(f"DROP VIEW IF EXISTS {view}")

    for table_name in (
        "users",
        "user_settings",
        "characters",
        "items",
        "daily_progress",
        "daily_activities",
    ):
        op.execute(
            sa.text(
                "DROP TRIGGER IF EXISTS update_{0}_updated_at ON {0}".format(table_name)
            )
        )

    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column")

    op.execute("DROP INDEX IF EXISTS idx_transactions_timestamp_desc")
    op.execute("DROP INDEX IF EXISTS idx_mood_history_timestamp")
    op.execute("DROP INDEX IF EXISTS idx_mood_history_character_time")
    op.execute("DROP INDEX IF EXISTS idx_daily_activities_date")
    op.execute("DROP INDEX IF EXISTS idx_daily_activities_character_date")
    op.execute("DROP INDEX IF EXISTS idx_daily_progress_date")
    op.execute("DROP INDEX IF EXISTS idx_daily_progress_character_date")

    op.drop_index("idx_transactions_timestamp", table_name="transactions")
    op.drop_index("idx_transactions_type", table_name="transactions")
    op.drop_index("idx_transactions_user_time", table_name="transactions")
    op.drop_table("transactions")

    op.drop_table("mood_history")

    op.drop_index("idx_daily_activities_type", table_name="daily_activities")
    op.drop_table("daily_activities")

    op.drop_table("daily_progress")

    op.drop_index("idx_item_bg_positions_bg", table_name="item_background_positions")
    op.drop_index("idx_item_bg_positions_item", table_name="item_background_positions")
    op.drop_table("item_background_positions")

    op.drop_index(
        "idx_character_backgrounds_active", table_name="character_backgrounds"
    )
    op.drop_index(
        "idx_character_backgrounds_character", table_name="character_backgrounds"
    )
    op.drop_table("character_backgrounds")

    op.drop_index("idx_character_items_favourite", table_name="character_items")
    op.drop_index("idx_character_items_active", table_name="character_items")
    op.drop_index("idx_character_items_character", table_name="character_items")
    op.drop_table("character_items")

    op.drop_index("idx_characters_level", table_name="characters")
    op.drop_index("idx_characters_user", table_name="characters")
    op.drop_table("characters")

    op.drop_index("idx_items_available", table_name="items")
    op.drop_index("idx_items_required_level", table_name="items")
    op.drop_index("idx_items_category", table_name="items")
    op.drop_table("items")

    op.drop_index("idx_backgrounds_available", table_name="backgrounds")
    op.drop_index("idx_backgrounds_required_level", table_name="backgrounds")
    op.drop_table("backgrounds")

    op.drop_table("item_categories")

    op.drop_index("idx_user_friends_friend", table_name="user_friends")
    op.drop_index("idx_user_friends_owner", table_name="user_friends")
    op.drop_table("user_friends")

    op.drop_index("idx_user_settings_user", table_name="user_settings")
    op.drop_table("user_settings")

    op.drop_index("idx_users_created_at", table_name="users")
    op.drop_index("idx_users_is_active", table_name="users")
    op.drop_table("users")

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("message_interval", sa.Integer(), nullable=False),
        sa.Column(
            "experience", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column("coins", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("level", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "messages_count", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )

    op.create_table(
        "pictures",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("picture_id", sa.Integer(), nullable=False),
        sa.Column(
            "telegram_id",
            sa.BigInteger(),
            sa.ForeignKey("users.telegram_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("level_to_open", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column(
            "is_opened", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("opened_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("picture_id", "telegram_id", name="uq_picture_owner"),
    )

    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)
    op.create_index("ix_pictures_telegram_id", "pictures", ["telegram_id"])
