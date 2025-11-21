from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from Backend.app.core.database import get_db
from Backend.app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token
)
from Backend.app.models.user import User
from Backend.app.schemas.token import Token, RefreshTokenRequest
from Backend.app.schemas.user import UserCreate, UserResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
# async def register(
#     user_data: UserCreate,
#     db: Session = Depends(get_db)
# ):
#     # Проверка существования пользователя
#     existing_user = db.query(User).filter(User.email == user_data.email).first()
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email already registered"
#         )
    
#     # Создание пользователя
#     hashed_password = get_password_hash(user_data.password)
#     db_user = User(
#         email=user_data.email,
#         hashed_password=hashed_password,
#         full_name=user_data.full_name
#     )
    
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
    
#     return db_user

# Вместо этого
# existing_user = db.query(User).filter(User.email == user_data.email).first()

# Используйте это:
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем существующего пользователя
    result = await db.execute(select(User).filter(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Проверяем телефон
    result = await db.execute(select(User).filter(User.phone == user_data.phone))
    existing_phone_user = result.scalar_one_or_none()
    
    if existing_phone_user:
        raise HTTPException(
            status_code=400,
            detail="Phone number already registered"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False
        # settings={'notifications': True, 'theme': 'light'}
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # return {"message": "User created successfully", "user_id": new_user.id}
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        phone=new_user.phone,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
        created_at=new_user.created_at
    )

# @router.post("/login", response_model=Token)
# async def login(
#     email: str,
#     password: str,
#     db: Session = Depends(get_db)
# ):
#     # Поиск пользователя
#     user = db.query(User).filter(User.email == email).first()
#     if not user or not verify_password(password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password"
#         )
    
#     if not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Inactive user"
#         )
    
#     # Создание токенов
#     access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
#     refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
#     return Token(
#         access_token=access_token,
#         refresh_token=refresh_token
#     )

# @router.post("/refresh", response_model=Token)
# async def refresh_token(
#     refresh_data: RefreshTokenRequest,
#     db: Session = Depends(get_db)
# ):
#     payload = verify_token(refresh_data.refresh_token)
#     if not payload or payload.get("type") != "refresh":
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token"
#         )
    
#     user_id = int(payload.get("sub"))
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user or not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found or inactive"
#         )
    
#     # Создание новых токенов
#     access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
#     refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
#     return Token(
#         access_token=access_token,
#         refresh_token=refresh_token
#     )
@router.post("/login", response_model=Token)
async def login(
    email: str,
    password: str,
    db: AsyncSession = Depends(get_db)
):
    # Поиск пользователя
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Обновляем last_login
    # user.last_login = datetime.now()
    # await db.commit()
    # await db.refresh(user)

    # Обновляем last_login (используем прямой подход без refresh)
    user.last_login = datetime.now()
    await db.commit()
    
    # Получаем обновленные данные пользователя
    result = await db.execute(select(User).where(User.id == user.id))
    updated_user = result.scalar_one_or_none()
    
    # Создание токенов
    access_token = create_access_token(data={"sub": str(updated_user.id), "email": updated_user.email})
    refresh_token = create_refresh_token(data={"sub": str(updated_user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
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
    result = await db.execute(select(User).where(User.id == user_id))
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

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(security)
):
    payload = verify_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = int(payload.get("sub"))
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at
    )