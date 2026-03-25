from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0003_tasks"
down_revision = "0002_auth_sessions"
branch_labels = None
depends_on = None


task_status = postgresql.ENUM(
    "open",
    "accepted",
    "in_progress",
    "completed",
    "cancelled",
    name="task_status",
    create_type=False,
)


def upgrade() -> None:
    task_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "tasks",
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("accepted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", task_status, nullable=False, server_default="open"),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=False),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("initial_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("accepted_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("completion_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint("initial_price > 0", name="tasks_initial_price_positive"),
        sa.ForeignKeyConstraint(
            ["accepted_by"], ["users.user_id"], name="fk_tasks_accepted_by_users"
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.user_id"], name="fk_tasks_created_by_users"
        ),
        sa.PrimaryKeyConstraint("task_id", name="pk_tasks"),
    )
    op.create_index("idx_tasks_created_by", "tasks", ["created_by"], unique=False)
    op.create_index("idx_tasks_accepted_by", "tasks", ["accepted_by"], unique=False)
    op.create_index("idx_tasks_status", "tasks", ["status"], unique=False)
    op.create_index(
        "idx_tasks_location", "tasks", ["latitude", "longitude"], unique=False
    )
    op.create_index("idx_tasks_category", "tasks", ["category"], unique=False)
    op.create_index("idx_tasks_created_at", "tasks", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_tasks_created_at", table_name="tasks")
    op.drop_index("idx_tasks_category", table_name="tasks")
    op.drop_index("idx_tasks_location", table_name="tasks")
    op.drop_index("idx_tasks_status", table_name="tasks")
    op.drop_index("idx_tasks_accepted_by", table_name="tasks")
    op.drop_index("idx_tasks_created_by", table_name="tasks")
    op.drop_table("tasks")
    task_status.drop(op.get_bind(), checkfirst=True)
