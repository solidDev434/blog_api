from pydantic import BaseModel, Field, EmailStr, ConfigDict
from models.users import User, UserRole
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, nullable=False)
    role: UserRole = Field(default=UserRole.READER, nullable=False)


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_email_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str
