import re

from pydantic import BaseModel, Field, field_validator

from app.models.enums import Role

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_email(value: str) -> str:
    email = value.strip().lower()
    if not _EMAIL.match(email):
        raise ValueError("Invalid email")
    return email


class RegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=2, max_length=160)
    phone: str | None = Field(default=None, max_length=40)

    @field_validator("email")
    @classmethod
    def email_ok(cls, value: str) -> str:
        return _normalize_email(value)


class LoginIn(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_ok(cls, value: str) -> str:
        return _normalize_email(value)


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    phone: str | None
    role: Role
    is_active: bool

    model_config = {"from_attributes": True}


class TokenUser(BaseModel):
    token: str
    user_id: int
    email: str
    role: Role
    full_name: str
