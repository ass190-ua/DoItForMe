from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_proposals_and_task_pivot"
down_revision = "0003_tasks"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Rename columns in tasks
    op.alter_column('tasks', 'created_by', new_column_name='creator_id')
    op.alter_column('tasks', 'accepted_by', new_column_name='runner_id')
    op.alter_column('tasks', 'latitude', new_column_name='location_lat')
    op.alter_column('tasks', 'longitude', new_column_name='location_lng')
    op.alter_column('tasks', 'initial_price', new_column_name='initial_offer')

    # 2. Add 'address' column to tasks
    op.add_column('tasks', sa.Column('address', sa.String(length=255), nullable=True))
    op.execute("UPDATE tasks SET address = 'Sin dirección' WHERE address IS NULL")
    op.alter_column('tasks', 'address', nullable=False)

    # 3. Change status column type from Enum to VARCHAR(20)
    op.alter_column(
        'tasks', 'status',
        type_=sa.String(length=20),
        existing_type=postgresql.ENUM('open', 'accepted', 'in_progress', 'completed', 'cancelled', name='task_status'),
        server_default='draft',
        existing_nullable=False
    )
    op.execute("UPDATE tasks SET status = 'published' WHERE status = 'open'")
    op.execute("DROP TYPE IF EXISTS task_status")

    # 4. Update constraints for tasks
    op.drop_constraint('tasks_initial_price_positive', 'tasks', type_='check')
    op.create_check_constraint('tasks_initial_offer_positive', 'tasks', 'initial_offer > 0')

    # 5. Fix Foreign Keys in tasks
    op.drop_constraint('fk_tasks_created_by_users', 'tasks', type_='foreignkey')
    op.drop_constraint('fk_tasks_accepted_by_users', 'tasks', type_='foreignkey')
    op.create_foreign_key('fk_tasks_creator_id_users', 'tasks', 'users', ['creator_id'], ['user_id'])
    op.create_foreign_key('fk_tasks_runner_id_users', 'tasks', 'users', ['runner_id'], ['user_id'])

    # 6. Update Indexes in tasks
    op.drop_index('idx_tasks_created_by', table_name='tasks')
    op.drop_index('idx_tasks_accepted_by', table_name='tasks')
    op.drop_index('idx_tasks_location', table_name='tasks')
    
    op.create_index('idx_tasks_creator', 'tasks', ['creator_id'], unique=False)
    op.create_index('idx_tasks_runner', 'tasks', ['runner_id'], unique=False)
    op.create_index('idx_tasks_location', 'tasks', ['location_lat', 'location_lng'], unique=False)

    # 7. Create proposals table
    op.create_table(
        'proposals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('runner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('proposed_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('proposed_price > 0', name='proposals_price_positive'),
        sa.ForeignKeyConstraint(['runner_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.task_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_proposals_runner', 'proposals', ['runner_id'], unique=False)
    op.create_index('idx_proposals_status', 'proposals', ['status'], unique=False)
    op.create_index('idx_proposals_task', 'proposals', ['task_id'], unique=False)

def downgrade() -> None:
    pass
