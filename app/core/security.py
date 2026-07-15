import uuid
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext

from schemas.exceptions import InvalidTokenError, TokenError, WrongTokenTypeError
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"])


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())
    })
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_ACCESS_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())
    })
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_access_token(token: str, expected_type="access") -> dict:
    """Verify and extract username from access token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_ACCESS_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except JWTError:
        raise InvalidTokenError("Invalid authentication credentials")

    username: str = payload.get("sub")
    token_type: str = payload.get("type")
    jti: Optional[str] = payload.get("jti")
    exp: Optional[int] = payload.get("exp")

    if not username:
        raise InvalidTokenError("Malformed token: missing required claims")

    if token_type != expected_type:
        raise WrongTokenTypeError(
            f"Expected token type '{expected_type}', got '{token_type}'"
        )

    return {
        "username": username,
        "jti": jti,
        "token_type": token_type,
        "exp": exp,
        "iat": payload.get("iat"),
    }


def verify_refresh_token(token: str, expected_type="refresh") -> dict:
    """Verify and extract username from refresh token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_REFRESH_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except JWTError:
        raise InvalidTokenError("Invalid authentication credentials")

    username: str = payload.get("sub")
    token_type: str = payload.get("type")
    jti: Optional[str] = payload.get("jti")
    exp: Optional[int] = payload.get("exp")

    if not username:
        raise InvalidTokenError("Malformed token: missing required claims")

    if token_type != expected_type:
        raise WrongTokenTypeError(
            f"Expected token type '{expected_type}', got '{token_type}'"
        )

    return {
        "username": username,
        "jti": jti,
        "exp": exp,
        "token_type": token_type,
    }
