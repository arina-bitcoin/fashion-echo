from pathlib import Path
import uuid
import shutil
from typing import Optional, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    File,
    UploadFile,
)
from sqlalchemy.orm import Session

from Backend.app.core.database import get_db
from Backend.app.dependencies import get_current_user
from Backend.app.models.user import User
from Backend.app.schemas.ad import AdResponse, AdCreate, AdUpdate
from Backend.app.services.ad_service import AdService
from Backend.app.utils.validators import validate_image_file

router = APIRouter()


# ---------- Объявления ----------

@router.get("/", response_model=List[AdResponse])
async def get_ads(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Получить список объявлений с фильтрацией"""
    return AdService.get_ads(
        db,
        skip=skip,
        limit=limit,
        type=type,
        category=category,
    )


@router.post("/", response_model=AdResponse)
async def create_ad(
    ad_data: AdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создать новое объявление"""
    return AdService.create_ad(db, ad_data, current_user.id)


@router.get("/{ad_id}", response_model=AdResponse)
async def get_ad(ad_id: int, db: Session = Depends(get_db)):
    """Получить объявление по ID"""
    ad = AdService.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad


# ---------- Загрузка изображений ----------

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),  # ВАЖНО: имя параметра file
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Загрузка изображения объявления.

    Ожидается multipart/form-data с ключом "file".
    При невалидном типе файла validate_image_file выбросит ValidationException,
    а глобальный обработчик вернёт 400.
    """
    # Валидация типа и размера
    validate_image_file(file)

    # Папка для картинок объявлений
    upload_dir = Path("media") / "ads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Генерируем уникальное имя файла
    ext = Path(file.filename).suffix or ".jpg"
    new_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = upload_dir / new_name

    # Сохраняем файл
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Тесты ожидают наличие ключа "file_path"
    return {
        "file_path": str(dest_path),
        "filename": new_name,
    }


# Дополнительный отладочный эндпоинт (по желанию)
@router.post("/debug/upload-image")
async def debug_upload_image(file: UploadFile = File(...)):
    validate_image_file(file)
    return {"filename": file.filename, "content_type": file.content_type}
