from fastapi import APIRouter, Depends, HTTPException, status, Response, Query, Body, Request
from pydantic import EmailStr
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from datetime import datetime, timezone
from Backend.app.core.database import get_db
from Backend.app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from Backend.app.models.user import User
from Backend.app.schemas.token import Token, RefreshTokenRequest, LoginRequest
from Backend.app.schemas.user import UserCreate, UserResponse, UserWithAvatarResponse
from Backend.app.dependencies import get_current_user
from Backend.app.services.file_service import file_service

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # Проверка существования пользователя
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создание пользователя
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name,
        phone=user_data.phone,
        is_active = True,
        is_verified = False,
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(
    # Вариант 1 – как в тестах: query-параметры
    email: Optional[EmailStr] = Query(None),
    password: Optional[str] = Query(None),
    # Вариант 2 – как в основном приложении: JSON body
    login_data: Optional[LoginRequest] = Body(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Логин: поддерживает и JSON body (LoginRequest),
    и query-параметры (email/password), как в интеграционном тесте.
    """

    # Определяем откуда брать данные
    if login_data is not None:
        email_value = login_data.email
        password_value = login_data.password
    else:
        email_value = email
        password_value = password

    # Если каких-то данных нет – 422, как и раньше
    if not email_value or not password_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="email and password are required",
        )

    # Поиск пользователя
    result = await db.execute(select(User).filter(User.email == email_value))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password_value, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    # Обновляем время последнего входа (не блокируем создание токенов)
    # ОПТИМИЗАЦИЯ: делаем обновление last_login необязательным, чтобы не замедлять логин
    try:
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
    except Exception as e:
        # Если обновление не удалось - не критично, продолжаем логин
        print(f"⚠️ Failed to update last_login: {e}")
    
    # Убрали db.refresh - он не нужен и вызывает дополнительный запрос к БД
    
    # Создание токенов

    # # Обновляем время последнего входа
    # stmt = (
    #     update(User)
    #     .where(User.id == user.id)
    #     .values(last_login=func.now())
    #     .execution_options(synchronize_session="fetch")
    # )
    # await db.execute(stmt)
    # await db.commit()

    # # Создание токенов – как было
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    payload = verify_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = int(payload.get("sub"))
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Создание новых токенов
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user)
):
    """
    Выход пользователя.
    На клиенте нужно удалить токены из localStorage/sessionStorage.
    """
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserWithAvatarResponse)
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Получение данных текущего пользователя"""
    user_data = UserWithAvatarResponse.model_validate(current_user)
    
    # Добавляем URL аватара
    if current_user.avatar:
        user_data.avatar_url = file_service.get_avatar_url(current_user.avatar, request)
    
    return user_data