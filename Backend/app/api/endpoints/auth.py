from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    Query,
    Body,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.app.core.database import get_db
from Backend.app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    validate_password_strength,
)
from Backend.app.models.user import User
from Backend.app.schemas.token import Token, RefreshTokenRequest, LoginRequest
from Backend.app.schemas.user import UserCreate, UserResponse, UserWithAvatarResponse
from Backend.app.dependencies import get_current_user
from Backend.app.services.file_service import file_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Поддержка как user_data.name, так и user_data.full_name
    name = getattr(user_data, "name", None) or getattr(user_data, "full_name", None)

    res = await db.execute(select(User).where(User.email == user_data.email))
    existing = res.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    validate_password_strength(user_data.password)

    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        name=name,
        phone=user_data.phone,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(
    # Основной путь — форм-логин (OAuth2PasswordRequestForm)
    form_data: Optional[OAuth2PasswordRequestForm] = Depends(None),
    # Доп. пути на случай клиентов/тестов: JSON и query
    login_data: Optional[LoginRequest] = Body(None),
    email_q: Optional[EmailStr] = Query(None),
    password_q: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Поддерживаем 3 способа передать логин/пароль (в порядке приоритета):
    1) form-data (OAuth2PasswordRequestForm)
    2) JSON body (LoginRequest)
    3) Query-параметры ?email=&password=
    """
    email: Optional[str] = None
    password: Optional[str] = None

    if form_data is not None:
        email = form_data.username
        password = form_data.password
    elif login_data is not None:
        email = login_data.email
        password = login_data.password
    else:
        email = email_q
        password = password_q

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="email and password are required",
        )

    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Обновляем отметку входа (не критично, если не удастся)
    try:
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
    except Exception:
        pass

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    payload = verify_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user_id = int(payload.get("sub"))
    res = await db.execute(select(User).where(User.id == user_id))
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token, refresh_token=new_refresh_token, token_type="bearer"
    )

@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    # Клиент должен удалить токены у себя (localStorage/sessionStorage)
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserWithAvatarResponse)
async def get_current_user_info(
    request: Request, current_user: User = Depends(get_current_user)
):
    user_data = UserWithAvatarResponse.model_validate(current_user)
    if current_user.avatar:
        user_data.avatar_url = file_service.get_avatar_url(current_user.avatar, request)
    return user_data

@router.get("/me/basic")
async def me_basic(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}
