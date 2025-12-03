# # from fastapi import APIRouter, Depends, HTTPException, status
# from Backend.app.schemas.user import UserCreate, UserResponse, UserWithAvatarResponse
# from fastapi import APIRouter, Depends, HTTPException, status, Response

# from fastapi.security import HTTPBearer
# from sqlalchemy.orm import Session
# from Backend.app.core.database import get_db
# from Backend.app.core.security import (
#     verify_password, 
#     get_password_hash, 
#     create_access_token, 
#     create_refresh_token,
#     verify_token
# )
# from Backend.app.models.user import User
# from Backend.app.schemas.token import Token, RefreshTokenRequest, LoginRequest
# from Backend.app.schemas.user import UserCreate, UserResponse
# from Backend.app.services.file_service import file_service
# from Backend.app.dependencies import get_current_user


# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from datetime import datetime

# router = APIRouter()
# security = HTTPBearer()

# @router.post("/register", response_model=UserResponse)

# # Используйте это:
# async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
#     # Проверяем существующего пользователя
#     result = await db.execute(select(User).filter(User.email == user_data.email))
#     existing_user = result.scalar_one_or_none()
    
#     if existing_user:
#         raise HTTPException(
#             status_code=400,
#             detail="Email already registered"
#         )
    
#     # Проверяем телефон
#     result = await db.execute(select(User).filter(User.phone == user_data.phone))
#     existing_phone_user = result.scalar_one_or_none()
    
#     if existing_phone_user:
#         raise HTTPException(
#             status_code=400,
#             detail="Phone number already registered"
#         )
    
#     # Создаем нового пользователя
#     hashed_password = get_password_hash(user_data.password)
#     new_user = User(
#         name=user_data.name,
#         email=user_data.email,
#         phone=user_data.phone,
#         hashed_password=hashed_password,
#         is_active=True,
#         is_verified=False
#         # settings={'notifications': True, 'theme': 'light'}
#     )
    
#     db.add(new_user)
#     await db.commit()
#     await db.refresh(new_user)
    
#     # return {"message": "User created successfully", "user_id": new_user.id}
#     return UserResponse(
#         id=new_user.id,
#         email=new_user.email,
#         name=new_user.name,
#         phone=new_user.phone,
#         is_active=new_user.is_active,
#         is_verified=new_user.is_verified,
#         created_at=new_user.created_at
#     )

# # @router.post("/login", response_model=Token)
# # async def login(
# #     email: str,
# #     password: str,
# #     db: Session = Depends(get_db)
# # ):
# #     # Поиск пользователя
# #     user = db.query(User).filter(User.email == email).first()
# #     if not user or not verify_password(password, user.hashed_password):
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Incorrect email or password"
# #         )
    
# #     if not user.is_active:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Inactive user"
# #         )
    
# #     # Создание токенов
# #     access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
# #     refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
# #     return Token(
# #         access_token=access_token,
# #         refresh_token=refresh_token
# #     )

# # @router.post("/refresh", response_model=Token)
# # async def refresh_token(
# #     refresh_data: RefreshTokenRequest,
# #     db: Session = Depends(get_db)
# # ):
# #     payload = verify_token(refresh_data.refresh_token)
# #     if not payload or payload.get("type") != "refresh":
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="Invalid refresh token"
# #         )
    
# #     user_id = int(payload.get("sub"))
# #     user = db.query(User).filter(User.id == user_id).first()
# #     if not user or not user.is_active:
# #         raise HTTPException(
# #             status_code=status.HTTP_401_UNAUTHORIZED,
# #             detail="User not found or inactive"
# #         )
    
# #     # Создание новых токенов
# #     access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
# #     refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
# #     return Token(
# #         access_token=access_token,
# #         refresh_token=refresh_token
# #     )
# @router.post("/login", response_model=Token)
# async def login(
#     # email: str,
#     # password: str,
#     login_data: LoginRequest,
#     db: AsyncSession = Depends(get_db)
# ):
#     # Поиск пользователя
#     result = await db.execute(select(User).where(User.email == login_data.email))
#     user = result.scalar_one_or_none()
    
#     if not user or not verify_password(login_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect email or password"
#         )
    
#     if not user.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Inactive user"
#         )
    
#     # Обновляем last_login
#     user.last_login = datetime.now()
#     await db.commit()
#     # await db.refresh(user)
    
#     # Получаем обновленные данные пользователя
#     result = await db.execute(select(User).where(User.id == user.id))
#     updated_user = result.scalar_one_or_none()
    
#     # Создание токенов
#     access_token = create_access_token(data={"sub": str(updated_user.id), "email": updated_user.email})
#     refresh_token = create_refresh_token(data={"sub": str(updated_user.id)})
    
#     return Token(
#         access_token=access_token,
#         refresh_token=refresh_token,
#         token_type="bearer"
#     )

# @router.post("/refresh", response_model=Token)
# async def refresh_token(
#     refresh_data: RefreshTokenRequest,
#     db: AsyncSession = Depends(get_db)
# ):
#     payload = verify_token(refresh_data.refresh_token)
#     if not payload or payload.get("type") != "refresh":
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token"
#         )
    
#     user_id = int(payload.get("sub"))
#     result = await db.execute(select(User).where(User.id == user_id))
#     user = result.scalar_one_or_none()
    
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
#         refresh_token=refresh_token,
#         token_type="bearer"
#     )

# @router.get("/me", response_model=UserWithAvatarResponse)
# async def get_current_user(
#     db: AsyncSession = Depends(get_db),
#     token: str = Depends(security)
# ):
#     payload = verify_token(token.credentials)
#     if not payload:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token"
#         )
    
#     user_id = int(payload.get("sub"))
#     result = await db.execute(select(User).where(User.id == user_id))
#     user = result.scalar_one_or_none()
    
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
    
#     return UserResponse(
#         id=user.id,
#         email=user.email,
#         name=user.name,
#         phone=user.phone,
#         is_active=user.is_active,
#         is_verified=user.is_verified,
#         created_at=user.created_at
#     )

# # @router.get("/me", response_model=UserWithAvatarResponse)
# # async def get_current_user_info(
# #     current_user: User = Depends(get_current_user)
# # ):
# #     """Получение данных текущего пользователя"""
# #     user_data = UserWithAvatarResponse.from_orm(current_user)
    
# #     # Добавляем URL аватара
# #     if current_user.avatar:
# #         user_data.avatar_url = file_service.get_avatar_url(current_user.avatar)
    
# #     return user_data

# @router.post("/logout")
# async def logout(
#     response: Response,
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Выход пользователя.
#     На клиенте нужно удалить токены из localStorage/sessionStorage.
#     """
#     # В JWT нет возможности инвалидировать токен на сервере без blacklist,
#     # поэтому просто возвращаем успешный ответ
#     return {"message": "Successfully logged out"}

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
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
        phone=user_data.phone
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    # Поиск пользователя
    result = await db.execute(select(User).filter(User.email == login_data.email))
    user = result.scalar_one_or_none()
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
    
    # Обновляем время последнего входа
    stmt = (
        update(User)
        .where(User.id == user.id)
        .values(last_login=func.now())
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()
    
    # Создание токенов
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
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