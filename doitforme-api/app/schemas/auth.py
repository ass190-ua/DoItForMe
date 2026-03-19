from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=100)
    role: UserRole

    @field_validator("role")
    @classmethod
    def restrict_admin(cls, v: UserRole) -> UserRole:
        if v == UserRole.ADMIN:
            raise ValueError("Admin role cannot be self-assigned")
        return v


class UserPublic(BaseModel):
    user_id: UUID
    email: str
    name: str
    role: str

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    user: UserPublic
