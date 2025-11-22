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