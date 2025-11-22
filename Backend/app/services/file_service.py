import os
import shutil
from fastapi import UploadFile, HTTPException, status
from typing import Optional
import uuid
from pathlib import Path

class FileService:
    def __init__(self):
        self.base_storage_path = "file_storage"
        self.avatar_path = os.path.join(self.base_storage_path, "images", "avatars")
        self.allowed_image_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        
        # Создаем директории если их нет
        os.makedirs(self.avatar_path, exist_ok=True)
    
    def _generate_unique_filename(self, original_filename: str) -> str:
        """Генерирует уникальное имя файла"""
        ext = Path(original_filename).suffix
        return f"{uuid.uuid4()}{ext}"
    
    def validate_image_file(self, file: UploadFile) -> None:
        """Валидация загружаемого изображения"""
        if file.content_type not in self.allowed_image_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Allowed types: JPEG, PNG, GIF, WEBP"
            )
        
        # Проверяем размер файла
        file.file.seek(0, 2)  # Перемещаемся в конец файла
        file_size = file.file.tell()
        file.file.seek(0)  # Возвращаемся в начало
        
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {self.max_file_size // 1024 // 1024}MB"
            )
    
    async def save_avatar(self, file: UploadFile, user_id: int) -> str:
        """Сохраняет аватар пользователя и возвращает путь к файлу"""
        self.validate_image_file(file)
        
        # Генерируем уникальное имя файла
        filename = self._generate_unique_filename(file.filename)
        file_path = os.path.join(self.avatar_path, filename)
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return f"images/avatars/{filename}"
    
    def delete_avatar(self, avatar_path: str) -> bool:
        """Удаляет аватар пользователя"""
        if not avatar_path:
            return False
            
        full_path = os.path.join(self.base_storage_path, avatar_path)
        
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    
    def get_avatar_url(self, avatar_path: str) -> Optional[str]:
        """Возвращает URL для доступа к аватару"""
        if not avatar_path:
            return None
        return f"/static/{avatar_path}"

# Создаем экземпляр сервиса
file_service = FileService()