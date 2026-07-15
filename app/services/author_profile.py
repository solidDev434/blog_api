import uuid
import logging
from typing import Optional, List
from sqlmodel import select, and_, or_
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.author_profile import AuthorProfileCreate
from models.author_profile import AuthorProfile
from schemas.exceptions import NotFoundError, ConflictError

logger = logging.getLogger(__name__)


class AuthorProfileService:
    @staticmethod
    async def get_all_author_profiles(
        db: AsyncSession
    ) -> List[AuthorProfile]:
        logger.info("Fetching all author profiles")
        try:
            statement = select(AuthorProfile)
            profiles = await db.execute(statement)
            return profiles.scalars().all()
        except Exception:
            logger.exception("Failed to fetch all author profiles")
            raise

    @staticmethod
    async def get_author_profile_by_id(
        db: AsyncSession,
        author_id: uuid.UUID
    ) -> AuthorProfile:
        logger.info(
            "Fetching author profiles by author id",
            extra={"author_id": str(author_id)}
        )
        try:
            statement = select(AuthorProfile).where(
                AuthorProfile.id == author_id)
            result = await db.execute(statement)
            profile = result.scalar_one_or_none()

            if not profile:
                logger.info("Author profile not found", extra={
                    "author_id": str(author_id)})
                raise NotFoundError(f"Author profile not found")

            return profile
        except Exception:
            logger.exception("Failed to fetch all author profiles")
            raise

    @staticmethod
    async def get_authenticated_user_author_profile(
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> Optional[AuthorProfile]:
        logger.info("Fetching authenticated author profile", extra={
            "user_id": str(user_id)})
        try:
            statement = select(AuthorProfile).where(
                AuthorProfile.user_id == user_id)
            result = await db.execute(statement)
            return result.scalar_one_or_none()
        except:
            logger.exception("Failed to fetch author profile", extra={
                             "user_id": str(user_id)})
            raise

    @staticmethod
    async def create_author_profile(
        db: AsyncSession,
        user_id: uuid.UUID,
        payload: AuthorProfileCreate
    ) -> None:
        logger.info("Creating author profile", extra={
            "user_id": str(user_id)})

        try:
            # Check if profile already exists, throw a conflict error if profile exists else proceed to creating profile
            statement = select(AuthorProfile).where(
                and_(AuthorProfile.user_id == user_id, or_(AuthorProfile.pen_name is not None, AuthorProfile.pen_name == payload.pen_name)))
            existing_profile = await db.execute(statement)

            if existing_profile.scalar_one_or_none():
                raise ConflictError("Author profile already exists")

            data = payload.model_dump(exclude_unset=True)
            profile = AuthorProfile(user_id=user_id, **data)

            db.add(profile)
            await db.commit()
            await db.refresh(profile)
        except:
            logger.exception(
                "Failed to create author profile",
                extra={"user_id": str(user_id)}
            )
            raise

    @staticmethod
    async def update_author_profile(
        db: AsyncSession,
        user_id: uuid.UUID,
        payload: AuthorProfileCreate
    ) -> None:
        profile = await AuthorProfileService.get_authenticated_user_author_profile(db, user_id)
        if not profile:
            logger.info("Author profile update attempted but not found", extra={
                        "user_id": str(user_id)})
            raise NotFoundError(f"Author profile not found for user {user_id}")

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(profile, field, value)

        try:
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
        except:
            logger.exception("Failed to persist author profile update", extra={
                             "user_id": str(user_id)})
            raise
