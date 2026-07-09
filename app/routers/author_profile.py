from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas.author_profile import AuthorProfileCreate
from core.dependency import role_required, User, Role, get_db_session
from services.author_profile import AuthorProfileService

router = APIRouter(
    prefix="/author_profile",
    tags=["Author Profile"]
)


@router.post("/me", status_code=status.HTTP_201_CREATED)
async def create_author_profile(
    payload: AuthorProfileCreate,
    user: User = Depends(role_required([Role.AUTHOR, Role.EDITOR])),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        await AuthorProfileService.create_author_profile(db, user.id, payload)
        return {"message": "Author profile created successfully"}
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occured. Try again"
        )
