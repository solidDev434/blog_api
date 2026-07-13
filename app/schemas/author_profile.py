import uuid
from pydantic import Field
from models.author_profile import AuthorProfileBase


class AuthorProfileCreate(AuthorProfileBase):
    pass


class AuthorProfileUpdate(AuthorProfileBase):
    pass


class AuthorProfileResponse(AuthorProfileBase):
    id: uuid.UUID

    posts_count: int = Field(default=0, nullable=False)
    is_featured: bool = Field(default=False, nullable=False)
