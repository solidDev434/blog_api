from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from core.dependency import get_db_session, get_current_user
from schemas.users import UserResponse, UserCreate
from services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login")
async def login_user():
    return "LOGIN USER"


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    if await AuthService.is_username_taken(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    if await AuthService.is_email_taken(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = await AuthService.create_user(db, user)
    return user


@router.post("/logout")
async def logout():
    return "LOGOUT USER"


@router.post("/refresh")
async def refresh():
    return "REFRESH TOKEN"
