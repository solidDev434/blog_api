import uuid
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.author_profile import AuthorProfileCreate
from models.author_profile import AuthorProfile


class AuthorProfileService:
    @staticmethod
    async def create_author_profile(
        db: AsyncSession,
        user_id: uuid.UUID,
        payload: AuthorProfileCreate
    ) -> AuthorProfile:
        data = payload.model_dump(exclude_unset=True)
        profile = AuthorProfile(user_id=user_id, **data)

        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return profile
