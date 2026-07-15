from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import AsyncGenerator, Annotated, List
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession
from redis.asyncio import Redis

from .redis import redis_client
from .security import verify_access_token
from .db import async_engine
from models.users import User, Role
from services.auth import AuthService
from services.cache import CacheService
from schemas.exceptions import WrongTokenTypeError, InvalidTokenError

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )

    async with async_session() as session:
        yield session


async def get_redis() -> Redis:
    return redis_client.get_client()


async def get_cache(redis: Annotated[Redis, Depends(get_redis)]) -> CacheService:
    return CacheService(redis)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db_session),
    cache: CacheService = Depends(get_cache)
) -> User:
    try:
        claims = verify_access_token(token)
    except WrongTokenTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    cached_token = await cache.get(f"bl:{claims['jti']}")
    if cached_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalidated"
        )

    # Get user form DB
    user = await AuthService.get_user_by_username(db, claims["username"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate credentials")

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def role_required(required_roles: List[Role]):
    def wrapper(user: User = Depends(get_current_active_user)):
        if user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for role: {user.role.value.capitalize()}"
            )
        return user
    return wrapper


CurrentUser = Annotated[User, Depends(get_current_active_user)]
Cache = Annotated[CacheService, Depends(get_cache)]
