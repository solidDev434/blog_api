from pydantic import BaseModel, Field, EmailStr
from models.users import User, UserRole


class CreateUser(BaseModel):
    username: str = Field(nullable=False)
    email: EmailStr = Field(nullable=False)
    password: str = Field(..., min_length=8, max_length=128, nullable=False)
    role: UserRole = Field(default=UserRole.READER, nullable=False)
