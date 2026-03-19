import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TaskStatus(StrEnum):
    OPEN = "open"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("initial_price > 0", name="tasks_initial_price_positive"),
        Index("idx_tasks_created_by", "created_by"),
        Index("idx_tasks_accepted_by", "accepted_by"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_location", "latitude", "longitude"),
        Index("idx_tasks_category", "category"),
        Index("idx_tasks_created_at", "created_at"),
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False
    )
    accepted_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        String(20), nullable=False, default=TaskStatus.OPEN
    )
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    initial_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    accepted_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    completion_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
