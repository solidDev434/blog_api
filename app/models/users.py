from enum import Enum
from sqlmodel import Field, SQLModel, AutoString
from pydantic import EmailStr
from datetime import datetime
from extendableenum import inheritable_enum
from typing import Optional


@inheritable_enum
class UserRole(str, Enum):
    READER = "reader"
    AUTHOR = "author"
    EDITOR = "editor"


class Role(UserRole):
    ADMIN = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: EmailStr = Field(sa_type=AutoString, nullable=False)
    hashed_password: str
    role: UserRole = Field(default=UserRole.READER)
    is_disabled: bool = Field(default=False)
    is_email_verified: bool = Field(default=False)
    email_verified_at: Optional[datetime] = Field(default=None, nullable=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    last_login_at: datetime = Field(default_factory=lambda: datetime.now())
