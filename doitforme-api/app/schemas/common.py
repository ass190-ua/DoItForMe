from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorDetails(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    error: None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now().astimezone())


class ErrorResponse(BaseModel):
    success: bool = False
    data: None = None
    error: ErrorDetails
    timestamp: datetime = Field(default_factory=lambda: datetime.now().astimezone())
