import uuid
from enum import Enum
from sqlmodel import Field, SQLModel, AutoString
from pydantic import EmailStr
from datetime import datetime, timezone
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

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: EmailStr = Field(sa_type=AutoString, nullable=False, unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.READER)
    is_active: bool = Field(default=True)
    is_email_verified: bool = Field(default=False)
    email_verified_at: Optional[datetime] = Field(default=None, nullable=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": datetime.now(timezone.utc)},
        nullable=False
    )
    last_login_at: datetime = Field(default=None, nullable=True)
