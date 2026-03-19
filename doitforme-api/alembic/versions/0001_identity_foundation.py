from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_identity_foundation"
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum("poster", "performer", "admin", name="user_role")


def upgrade() -> None:
    user_role.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("rating", sa.Numeric(3, 2), nullable=False, server_default="5.00"),
        sa.Column(
            "completed_tasks_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("rating_count", sa.Integer(), nullable=False, server_default="0"),
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
        sa.CheckConstraint("rating >= 0 AND rating <= 5", name="users_rating_range"),
        sa.PrimaryKeyConstraint("user_id", name="pk_users"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("idx_users_email", "users", ["email"], unique=False)
    op.create_index("idx_users_role", "users", ["role"], unique=False)
    op.create_index(
        "idx_users_location", "users", ["latitude", "longitude"], unique=False
    )
    op.create_index("idx_users_rating", "users", ["rating"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_users_rating", table_name="users")
    op.drop_index("idx_users_location", table_name="users")
    op.drop_index("idx_users_role", table_name="users")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_table("users")
    user_role.drop(op.get_bind(), checkfirst=True)
