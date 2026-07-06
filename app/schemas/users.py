from pydantic import BaseModel, Field, EmailStr
from models.users import User, UserRole


class CreateUser(BaseModel):
    username: str = Field(index=True, unique=True, nullable=False)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = Field(default=UserRole.READER, nullable=False)
    name: str | None = Field(default=None)
    avatar_url: str | None = Field(default=None)
    bio: str | None = Field(default=None)
