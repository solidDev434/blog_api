import logging
from fastapi import APIRouter, Depends, status, HTTPException, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio.session import AsyncSession
from datetime import timedelta
from typing import Annotated

from core.dependency import get_db_session, Cache, oauth2_scheme
from schemas.users import (UserResponse, UserCreate, Token)
from schemas.exceptions import TokenError
from services.auth import AuthService
from services.user import UserService
from core.utils.token_utils import blacklist_token, ste_refresh_token_cookie
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
    ste_refresh_token_cookie(response, refresh_token)

    return {"access_token": access_token}


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db_session)):
    if await UserService.is_username_taken(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    if await UserService.is_email_taken(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = await AuthService.create_user(db, user)
    return user


@router.post("/logout")
async def logout(
    response: Response,
    cache: Cache,
    token: str = Depends(oauth2_scheme),
    rft: Annotated[str | None, Cookie()] = None,
):
    try:
        claims = verify_access_token(token)
        await blacklist_token(cache, claims['jti'], claims["exp"])
    except TokenError:
        pass

    # Blacklist the refresh token too
    if rft:
        try:
            refresh_claims = verify_refresh_token(rft)
            await blacklist_token(cache, refresh_claims['jti'], refresh_claims["exp"], "bl_ref")
        except TokenError:
            pass

    # Clear cookie
    response.delete_cookie(
        key="rft",
        httponly=True,
        secure=True,
        samesite="strict"
    )

    return {"message": "Logged out successfully"}


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=Token
)
async def refresh(
    response: Response,
    cache: Cache,
    rft: Annotated[str | None, Cookie()] = None
):
    if not rft:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    try:
        claims = verify_refresh_token(rft)
    except TokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

    if await cache.get(f"bl_ref:{claims['jti']}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Refresh token has been revoked")

    await blacklist_token(cache, claims['jti'], claims["exp"], "bl_ref")

    access_token = create_access_token(
        data={"sub": claims["username"], "type": "access"}, expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(
        data={"sub": claims["username"], "type": "refresh"})

    ste_refresh_token_cookie(response, refresh_token)

    return {"access_token": access_token}
