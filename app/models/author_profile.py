import uuid
from sqlmodel import SQLModel, Field, Column, DateTime, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .users import User


class AuthorProfileBase(SQLModel):
    pen_name: Optional[str] = Field(max_length=100, index=True)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    bio: Optional[str] = Field(default=None)

    website: Optional[str] = Field(default=None)
    twitter_handle: Optional[str] = Field(default=None, max_length=50)
    linkedin_url: Optional[str] = Field(default=None)


class AuthorProfile(AuthorProfileBase, table=True):
    __tablename__ = "author_profile"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")

    posts_count: int = Field(default=0, nullable=False)
    is_featured: bool = Field(default=False, nullable=False)

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

    user: "User" = Relationship(back_populates="author_profile")
