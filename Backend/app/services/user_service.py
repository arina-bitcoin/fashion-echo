from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy import func
from app.core.security import verify_password, get_password_hash
from app.models.user import User
from app.schemas.user import UserUpdate, ChangePasswordRequest
from app.services.file_service import file_service

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_profile(self, user_id: int) -> User:
        """Получение профиля пользователя"""
        return self.get_user_by_id(user_id)
    
    def update_user_profile(self, user_id: int, user_data: UserUpdate) -> User:
        """Обновление профиля пользователя"""
        user = self.get_user_by_id(user_id)
        
        # Проверяем email на уникальность если он изменяется
        if user_data.email and user_data.email != user.email:
            existing_user = self.db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise ValueError("Email already registered")
        
        # Обновление данных пользователя
        update_data = user_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = func.now()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def change_password(self, user_id: int, password_data: ChangePasswordRequest) -> None:
        """Смена пароля пользователя"""
        user = self.get_user_by_id(user_id)
        
        # Проверка текущего пароля
        if not verify_password(password_data.current_password, user.hashed_password):
            raise ValueError("Current password is incorrect")
        
        # Установка нового пароля
        user.hashed_password = get_password_hash(password_data.new_password)
        user.updated_at = func.now()
        self.db.commit()
    
    async def upload_avatar(self, user_id: int, file) -> User:
        """Загрузка аватара пользователя"""
        user = self.get_user_by_id(user_id)
        
        # Удаляем старый аватар если есть
        if user.avatar:
            file_service.delete_avatar(user.avatar)
        
        # Сохраняем новый аватар
        avatar_path = await file_service.save_avatar(file, user.id)
        
        # Обновляем пользователя в БД
        user.avatar = avatar_path
        user.updated_at = func.now()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def delete_avatar(self, user_id: int) -> User:
        """Удаление аватара пользователя"""
        user = self.get_user_by_id(user_id)
        
        if not user.avatar:
            raise ValueError("Avatar not found")
        
        # Удаляем файл
        file_service.delete_avatar(user.avatar)
        
        # Обновляем пользователя в БД
        user.avatar = None
        user.updated_at = func.now()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def deactivate_user(self, user_id: int) -> None:
        """Деактивация пользователя"""
        user = self.get_user_by_id(user_id)
        user.is_active = False
        user.updated_at = func.now()
        self.db.commit()
    
    def get_user_by_id(self, user_id: int) -> User:
        """Получение пользователя по ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        return user