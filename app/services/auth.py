from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import EmailStr
from typing import Optional
from sqlmodel import select, or_

from models.users import User
from schemas.users import UserCreate
from core.security import verify_password, get_password_hash


class AuthService:
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
    async def login_user(db: AsyncSession, username: str | EmailStr, password: str) -> Optional[User]:
        user = await AuthService.get_user_by_email_or_username(db, username)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        """Create new user"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            role=user.role,
            hashed_password=hashed_password
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def is_username_taken(db: AsyncSession, username: str) -> bool:
        """Check if username already exists"""
        user = await AuthService.get_user_by_username(db, username)
        return user is not None

    @staticmethod
    async def is_email_taken(db: AsyncSession, email: EmailStr) -> bool:
        """Check if username already exists"""
        user = await AuthService.get_user_by_email(db, email)
        return user is not None
