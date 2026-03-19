from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_auth_sessions"
down_revision = "0001_identity_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_sessions",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("access_jti", sa.String(length=36), nullable=False),
        sa.Column("refresh_jti", sa.String(length=36), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.user_id"], name="fk_auth_sessions_user_id_users"
        ),
        sa.PrimaryKeyConstraint("session_id", name="pk_auth_sessions"),
        sa.UniqueConstraint("access_jti", name="uq_auth_sessions_access_jti"),
        sa.UniqueConstraint("refresh_jti", name="uq_auth_sessions_refresh_jti"),
    )
    op.create_index(
        "idx_auth_sessions_user_id", "auth_sessions", ["user_id"], unique=False
    )
    op.create_index(
        "idx_auth_sessions_access_jti", "auth_sessions", ["access_jti"], unique=False
    )
    op.create_index(
        "idx_auth_sessions_refresh_jti", "auth_sessions", ["refresh_jti"], unique=False
    )
    op.create_index(
        "idx_auth_sessions_revoked_at", "auth_sessions", ["revoked_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_auth_sessions_revoked_at", table_name="auth_sessions")
    op.drop_index("idx_auth_sessions_refresh_jti", table_name="auth_sessions")
    op.drop_index("idx_auth_sessions_access_jti", table_name="auth_sessions")
    op.drop_index("idx_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
