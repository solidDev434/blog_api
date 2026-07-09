import uuid
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from models.users import Role
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128, nullable=False)
    role: Role = Field(default=Role.READER, nullable=False)


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    role: Role
    is_email_verified: bool

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str


class TokenData(BaseModel):
    username: Optional[str] = None
