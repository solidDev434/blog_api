from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import EmailStr
from typing import Optional

from services.user import UserService
from models.users import User
from schemas.users import UserCreate
from core.security import verify_password, get_password_hash


class AuthService:
    @staticmethod
    async def login_user(db: AsyncSession, username: str | EmailStr, password: str) -> Optional[User]:
        user = await UserService.get_user_by_email_or_username(db, username)
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
