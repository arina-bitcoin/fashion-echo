from sqlalchemy.ext.asyncio import AsyncSession  # Изменение: импортируем AsyncSession
from sqlalchemy import select, func  # Изменение: используем select вместо query
from fastapi import HTTPException, status

from Backend.app.core.security import verify_password, get_password_hash
from Backend.app.models.user import User
from Backend.app.schemas.user import UserUpdate, ChangePasswordRequest
from Backend.app.services.file_service import file_service

class UserService:
    # Изменение: убираем __init__, делаем все методы статичными
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
        """Получение пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        return user
    
    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: int) -> User:
        """Получение профиля пользователя"""
        return await UserService.get_user_by_id(db, user_id)
    
    @staticmethod
    async def update_user_profile(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
        """Обновление профиля пользователя"""
        user = await UserService.get_user_by_id(db, user_id)
        
        # Проверяем email на уникальность если он изменяется
        if user_data.email and user_data.email != user.email:
            stmt = select(User).where(User.email == user_data.email)
            result = await db.execute(stmt)
            existing_user = result.scalar_one_or_none()
            if existing_user:
                raise ValueError("Email already registered")
        
        # Обновление данных пользователя
        update_data = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = func.now()
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def change_password(db: AsyncSession, user_id: int, password_data: ChangePasswordRequest) -> None:
        """Смена пароля пользователя"""
        user = await UserService.get_user_by_id(db, user_id)
        
        # Проверка текущего пароля
        if not verify_password(password_data.current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        # Установка нового пароля
        user.hashed_password = get_password_hash(password_data.new_password)
        user.updated_at = func.now()
        await db.commit()
    
    @staticmethod
    async def upload_avatar(db: AsyncSession, user_id: int, file) -> User:
        """Загрузка аватара пользователя"""
        user = await UserService.get_user_by_id(db, user_id)
        
        # Удаляем старый аватар если есть
        if user.avatar:
            file_service.delete_avatar(user.avatar)
        
        # Сохраняем новый аватар
        avatar_path = await file_service.save_avatar(file, user.id)
        
        # Обновляем пользователя в БД
        user.avatar = avatar_path
        user.updated_at = func.now()
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def delete_avatar(db: AsyncSession, user_id: int) -> User:
        """Удаление аватара пользователя"""
        user = await UserService.get_user_by_id(db, user_id)
        
        if not user.avatar:
            raise ValueError("Avatar not found")
        
        # Удаляем файл
        file_service.delete_avatar(user.avatar)
        
        # Обновляем пользователя в БД
        user.avatar = None
        user.updated_at = func.now()
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: int) -> None:
        """Деактивация пользователя"""
        user = await UserService.get_user_by_id(db, user_id)
        user.is_active = False
        user.updated_at = func.now()
        await db.commit()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User:
        """Получение пользователя по email"""
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError("User not found")
        return user