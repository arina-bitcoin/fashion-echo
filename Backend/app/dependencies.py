# from typing import Optional, Annotated
# from datetime import datetime, timedelta
# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from jose import JWTError, jwt
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select
# from Backend.app.core.database import get_db
# from Backend.app.models.user import User
# from Backend.app.config import settings

# security = HTTPBearer(auto_error=False)

# async def get_current_user(
#     token: Annotated[HTTPAuthorizationCredentials, Depends(security)],
#     db: AsyncSession = Depends(get_db)
# ) -> User:
#     """Получить текущего пользователя по токену"""
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Неверные учетные данные",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         # Исправление: получаем строковый токен из объекта credentials
#         token_str = token.credentials  # <-- ВАЖНОЕ ИСПРАВЛЕНИЕ
        
#         payload = jwt.decode(
#             token_str,
#             settings.SECRET_KEY,
#             algorithms=[settings.ALGORITHM]
#         )
#         user_id: int = payload.get("user_id")
#         if user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
    
#     stmt = select(User).where(User.id == user_id)
#     result = await db.execute(stmt)
#     user = result.scalar_one_or_none()
    
#     if user is None:
#         raise credentials_exception
    
#     return user


# async def get_current_user_optional(
#     credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)] = None,
#     db: AsyncSession = Depends(get_db)
# ) -> Optional[User]:
#     """Получить текущего пользователя (опционально)"""
#     if credentials is None:
#         return None
    
#     try:
#         # Исправление: получаем строковый токен из объекта credentials
#         token_str = credentials.credentials  # <-- ВАЖНОЕ ИСПРАВЛЕНИЕ
        
#         payload = jwt.decode(
#             token_str,
#             settings.SECRET_KEY,
#             algorithms=[settings.ALGORITHM]
#         )
#         user_id: int = payload.get("user_id")
#         if user_id is None:
#             return None
#     except JWTError:
#         return None
    
#     stmt = select(User).where(User.id == user_id)
#     result = await db.execute(stmt)
#     user = result.scalar_one_or_none()
    
#     return user


# async def is_admin_user(
#     current_user: Annotated[User, Depends(get_current_user)]
# ) -> bool:
#     """Проверить, является ли пользователь администратором"""
#     return getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_superuser', False)

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from Backend.app.core.database import get_db
from Backend.app.models.user import User
from Backend.app.services.user_service import UserService
from Backend.app.config import settings

security = HTTPBearer(auto_error=False)  # auto_error=False - не выбрасывать ошибку если нет токена

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Получить текущего пользователя (обязательная аутентификация)"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
        )
    
    user = await UserService.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    
    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Получить текущего пользователя (опциональная аутентификация)"""
    if credentials is None:
        return None
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    user = await UserService.get_user_by_id(db, user_id)
    return user

async def is_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Проверка, что пользователь является администратором"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )
    return current_user