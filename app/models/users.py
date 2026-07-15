import uuid
from enum import Enum
from sqlmodel import Field, SQLModel, AutoString, Column, DateTime, Relationship
from pydantic import EmailStr
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

# import for type checking to avoid runtime import cycles / undefined name warnings
if TYPE_CHECKING:
    from .author_profile import AuthorProfile


class Role(Enum):
    READER = "reader"
    AUTHOR = "author"
    EDITOR = "editor"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    email: EmailStr = Field(sa_type=AutoString, nullable=False, unique=True)
    hashed_password: str
    role: Role = Field(default=Role.READER)
    is_active: bool = Field(default=True)
    is_email_verified: bool = Field(default=False)
    author_profile: Optional["AuthorProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False}
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=lambda: datetime.now(timezone.utc),
        ),
    )
    last_login_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
