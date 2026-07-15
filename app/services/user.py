from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import EmailStr
from typing import Optional
from sqlmodel import select, or_

from models.users import User


class UserService:
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username"""
        statement = select(User).where(
            User.username == username)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: EmailStr) -> Optional[User]:
        """Get user by email"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email_or_username(db: AsyncSession, username: str | EmailStr) -> Optional[User]:
        """Get user by username or email"""
        statement = select(User).where(
            or_(User.email == username, User.username == username))
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def is_username_taken(db: AsyncSession, username: str) -> bool:
        """Check if username already exists"""
        user = await UserService.get_user_by_username(db, username)
        return user is not None

    @staticmethod
    async def is_email_taken(db: AsyncSession, email: EmailStr) -> bool:
        """Check if username already exists"""
        user = await UserService.get_user_by_email(db, email)
        return user is not None
