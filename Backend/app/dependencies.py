# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer
# from sqlalchemy.orm import Session
# from Backend.app.core.database import get_db
# from Backend.app.core.security import verify_token
# from Backend.app.models.user import User

# oauth2_scheme = HTTPBearer()

# async def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_db)
# ) -> User:
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     payload = verify_token(token.credentials)
#     if payload is None or payload.get("type") != "access":
#         raise credentials_exception
    
#     user_id: int = int(payload.get("sub"))
#     if user_id is None:
#         raise credentials_exception
    
#     user = db.query(User).filter(User.id == user_id).first()
#     if user is None or not user.is_active:
#         raise credentials_exception
    
#     return user

# async def get_current_active_user(
#     current_user: User = Depends(get_current_user)
# ) -> User:
#     if not current_user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Backend.app.core.database import get_db
from Backend.app.core.security import verify_token
from Backend.app.models.user import User
from Backend.app.services.user_service import UserService
from typing import Optional
from jose import jwt
from jose.exceptions import JWTError
from Backend.app.config import settings

oauth2_scheme = HTTPBearer()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token.credentials)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception
    
    user_id: int = int(payload.get("sub"))
    if user_id is None:
        raise credentials_exception
    
    # ИСПРАВЛЕНИЕ: используем асинхронный запрос
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Получить текущего пользователя, если он авторизован.
    Возвращает None, если токен отсутствует или невалиден.
    """
    if not token:
        return None
    
    try:
        # Декодируем токен
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    # Получаем пользователя из БД
    user = await UserService.get_user_by_id(db, int(user_id))
    return user


async def is_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Проверить, является ли пользователь администратором.
    Вызывает исключение, если пользователь не администратор.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user