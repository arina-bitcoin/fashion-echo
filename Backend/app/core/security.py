from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict, Union

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.app.config import settings
from Backend.app.core.database import get_db
from Backend.app.models.user import User

# ---------- Password hashing (твоя конфигурация) ----------
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__time_cost=3,
    argon2__memory_cost=65536,
    argon2__parallelism=1,
    argon2__hash_len=32,
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ---------- Политика сложности пароля ----------
def validate_password_strength(password: str) -> None:
    """
    Минимальная политика: длина >= 8, содержит буквы и цифры.
    При необходимости расширь (спецсимволы, верхний/нижний регистр и т.п.).
    """
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password too short (min 8)")
    if password.isdigit() or password.isalpha():
        raise HTTPException(status_code=400, detail="Password must contain letters and digits")

# ---------- JWT helpers ----------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def _exp_utc_after(delta: timedelta) -> datetime:
    # используем tz-aware datetime, PyJWT его понимает
    return datetime.now(timezone.utc) + delta

def _encode_jwt(payload: Dict[str, Any]) -> str:
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def _decode_jwt(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from e

def create_access_token(
    data_or_subject: Union[Dict[str, Any], str, int],
    expires_delta: Optional[timedelta] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Универсальный helper:
    - если передан dict -> используется как основа payload
    - если передан subject (str|int) -> кладём в payload как "sub"
    В обоих случаях добавляем {"type": "access", "exp": ...}.
    """
    if isinstance(data_or_subject, dict):
        to_encode: Dict[str, Any] = dict(data_or_subject)  # копия
    else:
        to_encode = {"sub": str(data_or_subject)}

    if extra:
        to_encode.update(extra)

    expire = _exp_utc_after(expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return _encode_jwt(to_encode)

def create_refresh_token(
    data_or_subject: Union[Dict[str, Any], str, int],
    expires_delta: Optional[timedelta] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Аналогично create_access_token, но type='refresh' и свой срок.
    """
    if isinstance(data_or_subject, dict):
        to_encode: Dict[str, Any] = dict(data_or_subject)
    else:
        to_encode = {"sub": str(data_or_subject)}

    if extra:
        to_encode.update(extra)

    expire = _exp_utc_after(expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})
    return _encode_jwt(to_encode)

def verify_token(token: str) -> Optional[dict]:
    """
    Возвращает payload либо None (без исключения).
    Удобно там, где не хочется ронять 401.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except InvalidTokenError:
        return None

# Оставляем совместимые алиасы, если где-то в коде вызывалась "вариант-2" сигнатура
def create_access_token_by_subject(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    return create_access_token(subject, expires_delta=expires_delta, extra=extra)

# ---------- FastAPI dependency ----------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = _decode_jwt(token)

    # Можно (опционально) требовать именно access-токен
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token required")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    res = await db.execute(select(User).where(User.id == int(user_id)))
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or not found")

    return user
