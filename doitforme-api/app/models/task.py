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
    DRAFT = "draft"
    PUBLISHED = "published"
    NEGOTIATING = "negotiating"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("initial_offer > 0", name="tasks_initial_offer_positive"),
        Index("idx_tasks_creator", "creator_id"),
        Index("idx_tasks_runner", "runner_id"),
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_location", "location_lat", "location_lng"),
        Index("idx_tasks_category", "category"),
        Index("idx_tasks_created_at", "created_at"),
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Usuario que pide el recado
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False
    )
    
    # Usuario que ejecutará el recado
    runner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True
    )
    
    status: Mapped[TaskStatus] = mapped_column(
        String(20), nullable=False, default=TaskStatus.DRAFT
    )
    
    location_lat: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    location_lng: Mapped[Decimal] = mapped_column(Numeric(11, 8), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    initial_offer: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    accepted_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    proof_image_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
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
