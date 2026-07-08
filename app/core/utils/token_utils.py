from datetime import datetime
from fastapi import Response
from core.config import settings
from services.cache import CacheService


async def blacklist_token(
    cache: CacheService,
    jti: str,
    exp: int,
    prefix: str = "bl"
) -> None:
    """Blacklist a token by it's jti until its natural expiry"""
    ttl = exp - int(datetime.utcnow().timestamp())
    if ttl > 0:
        await cache.set(f"{prefix}:{jti}", "1", ttl=ttl)


def ste_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    """Set the refresh token as an httponly cookie with the configuted expiry."""
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key="rft",
        value=refresh_token,
        max_age=max_age,
        httponly=True,
        secure=True,
        samesite="strict",
    )
