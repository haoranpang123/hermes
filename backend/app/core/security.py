"""JWT 签发与验证 / 密码哈希"""

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from jose import JWTError

from app.config import get_settings

settings = get_settings()

# bcrypt 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---- 密码 ----

def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ---- JWT ----

def create_access_token(
    user_id: int,
    role: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """签发 JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.JWT_EXPIRE_HOURS)

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """解码并验证 JWT token, 返回 payload"""
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")
