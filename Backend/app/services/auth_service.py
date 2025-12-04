from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Backend.app.models.user import User
from Backend.app.core.security import verify_password

class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str):
        """Аутентификация пользователя"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        
        return user