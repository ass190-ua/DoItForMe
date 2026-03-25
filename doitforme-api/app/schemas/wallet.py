from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DepositRequest(BaseModel):
    amount: Decimal = Field(gt=0, le=10000, description="Amount to deposit")

    model_config = ConfigDict(extra="forbid")


class TransactionPublic(BaseModel):
    id: UUID
    user_id: UUID
    amount: Decimal
    transaction_type: str
    task_id: UUID | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WalletResponse(BaseModel):
    balance: Decimal
    transactions: list[TransactionPublic]
