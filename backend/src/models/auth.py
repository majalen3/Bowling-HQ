from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


def _validate_email(value: str) -> str:
    value = value.strip()
    if "@" not in value or "." not in value.split("@")[-1]:
        raise ValueError("Invalid email address")
    return value.lower()


class UserCreate(BaseModel):
    email: str
    display_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        return _validate_email(value)


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str) -> str:
        return _validate_email(value)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: UUID
    email: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    display_name: str
    created_at: datetime
