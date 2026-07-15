import uuid
import logging
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import EmailStr
from typing import Optional
from sqlmodel import select, or_


from core.security import verify_password, get_password_hash
from models.users import User
from schemas.users import UserUpdate, UserPasswordUpdate
from schemas.exceptions import ForbiddenRequest, UnauthorizedRequest, BadRequest

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Get user by username"""
        statement = select(User).where(
            User.id == user_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

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

    @staticmethod
    async def check_if_user_exists(db: AsyncSession, user_id: uuid.UUID) -> User:
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise ForbiddenRequest(
                "You aren't authorized to access this resource")

        return user

    @staticmethod
    async def update_public(db: AsyncSession, user_id: uuid.UUID, payload: UserUpdate):
        """Update user public info"""
        existing_user = await UserService.check_if_user_exists(db, user_id)

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(existing_user, field, value)

        try:
            db.add(existing_user)
            await db.commit()
            await db.refresh()
        except:
            await db.rollback()
            logger.info("Failed to user profile", extra={"user_id", user_id})
            raise

    @staticmethod
    async def update_password(db: AsyncSession, user_id: uuid.UUID, payload: UserPasswordUpdate):
        """Update user password"""
        existing_user = await UserService.check_if_user_exists(db, user_id)

        # Check if old password is correct
        if not verify_password(payload.old_password, existing_user.hashed_password):
            raise UnauthorizedRequest("Incorrect current password")

        # Check if new password is equal to the user old password
        if payload.old_password == payload.new_password:
            raise BadRequest(
                "New password cannot be the same as your old password.")

        hash_new_password = get_password_hash(payload.new_password)

        # Update hashed password
        existing_user.hashed_password = hash_new_password

        try:
            db.add(existing_user)
            await db.commit()
            await db.refresh(existing_user)
        except:
            await db.rollback()
            logger.info("Unexpected error while updating user password", extra={
                        "user_id", user_id})
            raise
