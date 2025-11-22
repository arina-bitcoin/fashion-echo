from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from Backend.app.core.database import get_db
from Backend.app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from Backend.app.models.user import User
from Backend.app.schemas.token import Token, RefreshTokenRequest, LoginRequest  # ИМПОРТИРОВАТЬ LoginRequest
from Backend.app.schemas.user import UserCreate, UserResponse, UserWithAvatarResponse
from Backend.app.dependencies import get_current_user
from Backend.app.services.file_service import file_service

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Проверка существования пользователя
    # existing_user = db.query(User).filter(User.email == user_data.email).first()
    result = await db.execute(select(User).where(User.email == user_data.email))
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
        phone=user_data.phone
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# ИСПРАВЛЕННЫЙ эндпоинт login
@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,  # Используем схему вместо query parameters
    db: Session = Depends(get_db)
):
    # Поиск пользователя
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    # user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Создание токенов
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
    # В JWT нет возможности инвалидировать токен на сервере без blacklist,
    # поэтому просто возвращаем успешный ответ
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    payload = verify_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
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

@router.get("/me", response_model=UserWithAvatarResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получение данных текущего пользователя"""
    user_data = UserWithAvatarResponse.from_orm(current_user)
    
    # Добавляем URL аватара
    if current_user.avatar:
        user_data.avatar_url = file_service.get_avatar_url(current_user.avatar)
    
    return user_data