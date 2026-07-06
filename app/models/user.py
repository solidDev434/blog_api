from enum import Enum
from sqlmodel import Field, SQLModel, AutoString
from pydantic import EmailStr
from datetime import datetime


class UserRole(str, Enum):
    READER = "reader"
    AUTHOR = "author"
    EDITOR = "editor"
    ADMIN = "admin"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: EmailStr = Field(sa_type=AutoString, nullable=False)
    hashed_password: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.READER, nullable=False)
    name: str | None = Field(default=None)
    avatar_url: str | None = Field(default=None)
    bio: str | None = Field(default=None)

    is_email_verified: bool = Field(nullable=False, default=False)
    email_verified_at: datetime = Field(default_factory=lambda: datetime.now())

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    last_login_at: datetime = Field(default_factory=lambda: datetime.now())
