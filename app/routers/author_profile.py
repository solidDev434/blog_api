import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List

from schemas.author_profile import (
    AuthorProfileCreate,
    AuthorProfileUpdate,
    AuthorProfileResponse
)
from schemas.exceptions import NotFoundError
from core.dependency import role_required, User, Role, get_db_session
from services.author_profile import AuthorProfileService

router = APIRouter(
    prefix="/author_profile",
    tags=["Author Profile"]
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=List[AuthorProfileResponse]
)
async def get_all_author_profiles(db: AsyncSession = Depends(get_db_session)):
    try:
        profiles = await AuthorProfileService.get_all_author_profiles(db)
        return profiles
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/{author_id}",
    status_code=status.HTTP_200_OK,
    response_model=AuthorProfileResponse
)
async def get_author_profile_by_id(author_id: uuid.UUID, db: AsyncSession = Depends(get_db_session)):
    try:
        profile = await AuthorProfileService.get_author_profile_by_id(db, author_id)
        return profile
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=AuthorProfileResponse
)
async def get_author_profile(
    user: User = Depends(role_required([Role.AUTHOR])),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        profile = await AuthorProfileService.get_authenticated_user_author_profile(db, user.id)
        return profile
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/me", status_code=status.HTTP_201_CREATED)
async def create_author_profile(
    payload: AuthorProfileCreate,
    user: User = Depends(role_required([Role.AUTHOR])),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        await AuthorProfileService.create_author_profile(db, user.id, payload)
        return {"message": "Author profile created successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch("/me", status_code=status.HTTP_200_OK)
async def update_author_profile(
    payload: AuthorProfileUpdate,
    user: User = Depends(role_required([Role.AUTHOR])),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        await AuthorProfileService.update_author_profile(db, user.id, payload)
        return {"message": "Author profile updated successfully"}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
