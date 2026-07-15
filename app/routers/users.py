from fastapi import APIRouter, status, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from core.dependency import CurrentUser, get_db_session
from services.user import UserService
from schemas.users import UserResponse, UserUpdate, UserPasswordUpdate
from schemas.exceptions import ForbiddenRequest, UnauthorizedRequest, BadRequest

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
async def read_users(user: CurrentUser):
    return user


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK
)
async def update_user_info(
    payload: UserUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        await UserService.update_public(db, user.id, payload)
    except ForbiddenRequest as fe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(fe)
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch(
    "/me/password",
    status_code=status.HTTP_200_OK
)
async def update_user_password(
    payload: UserPasswordUpdate,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        await UserService.update_password(db, user.id, payload)
        return {"message": "User password updated"}
    except BadRequest as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except UnauthorizedRequest as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
