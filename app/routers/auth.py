import logging
from fastapi import APIRouter, Depends, status, HTTPException, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from sqlalchemy.ext.asyncio.session import AsyncSession
from datetime import timedelta
from typing import Annotated

from core.dependency import get_db_session, Cache, oauth2_scheme
from schemas.users import (UserResponse, UserCreate, Token)
from schemas.exceptions import TokenError
from services.auth import AuthService
from core.config import settings
from core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    verify_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

logger = logging.getLogger(__name__)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=Token
)
async def login_user(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    user = await AuthService.login_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        data={"sub": user.username, "type": "access"}, expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(
        data={"sub": user.username, "type": "refresh"})

    # Set the refresh token in cookie
    refresh_token_expiry_timestamp = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key="rft",
        value=refresh_token,
        expires=refresh_token_expiry_timestamp,
        httponly=True,
        secure=True,
        samesite="strict"
    )

    return {"access_token": access_token}


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
async def logout(cache: Cache, token: str = Depends(oauth2_scheme)):
    try:
        claims = verify_access_token(token)
    except TokenError:
        return {"message": "Logged out"}
    print(claims, "Logout claims")

    ttl = claims["exp"] - int(datetime.utcnow().timestamp())
    if ttl > 0:
        await cache.set(f"bl:{claims['jti']}", "1", ttl=ttl)

    return {"message": "Logged out successfully"}


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=Token
)
async def refresh(rft: Annotated[str | None, Cookie()] = None):
    username = verify_refresh_token(rft) if rft else None

    access_token = create_access_token(
        data={"sub": username, "type": "access"}, expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    return {"access_token": access_token}
