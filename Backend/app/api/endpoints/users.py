from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status, 
    UploadFile, 
    File, 
    Request, 
    Query
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete

from Backend.app.core.database import get_db
from Backend.app.core.security import verify_password, get_password_hash
from Backend.app.dependencies import get_current_user
from Backend.app.models.user import User
from Backend.app.schemas.user import UserResponse, UserUpdate, ChangePasswordRequest, UserWithAvatarResponse, UserPublicInfo
from Backend.app.services.file_service import file_service
from Backend.app.schemas.ad import AdResponse, AdStatus
from Backend.app.models.ad import Ad

router = APIRouter()

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
    else:
        user_data.avatar_url = None
    
    return user_data

@router.put("/me", response_model=UserWithAvatarResponse)
async def update_current_user(
    user_data: UserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление профиля пользователя"""

    # Собираем только реально переданные поля
    update_data = user_data.model_dump(exclude_unset=True)

    # Если среди них есть email — проверяем на уникальность
    new_email = update_data.get("email")
    if new_email and new_email != current_user.email:
        result = await db.execute(select(User).filter(User.email == new_email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    # Обновление данных пользователя (асинхронно)
    stmt = (
        update(User)
        .where(User.id == current_user.id)
        .values(**update_data, updated_at=func.now())
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()

    # Читаем обновлённого пользователя из БД
    result = await db.execute(select(User).filter(User.id == current_user.id))
    updated_user = result.scalar_one()

    # Формируем ответ с URL аватара
    response_data = UserWithAvatarResponse.model_validate(updated_user)
    if updated_user.avatar:
        response_data.avatar_url = file_service.get_avatar_url(updated_user.avatar, request)
    else:
        response_data.avatar_url = None
    
    return response_data


@router.post("/me/avatar", response_model=UserWithAvatarResponse)
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Загрузка аватара пользователя"""
    try:
        # Удаляем старый аватар если есть
        if current_user.avatar:
            file_service.delete_avatar(current_user.avatar)
        
        # Сохраняем новый аватар
        avatar_path = await file_service.save_avatar(file, current_user.id)
        
        # Обновляем пользователя в БД
        stmt = (
            update(User)
            .where(User.id == current_user.id)
            .values(avatar=avatar_path, updated_at=func.now())
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(stmt)
        await db.commit()
        
        # Получаем обновленного пользователя
        result = await db.execute(select(User).filter(User.id == current_user.id))
        updated_user = result.scalar_one()
        
        # Формируем ответ
        response_data = UserWithAvatarResponse.model_validate(updated_user)
        response_data.avatar_url = file_service.get_avatar_url(avatar_path, request)
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading avatar: {str(e)}"
        )

@router.delete("/me/avatar", response_model=UserWithAvatarResponse)
async def delete_avatar(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление аватара пользователя"""
    if not current_user.avatar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avatar not found"
        )
    
    # Удаляем файл
    file_service.delete_avatar(current_user.avatar)
    
    # Обновляем пользователя в БД
    stmt = (
        update(User)
        .where(User.id == current_user.id)
        .values(avatar=None, updated_at=func.now())
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()
    
    # Получаем обновленного пользователя
    result = await db.execute(select(User).filter(User.id == current_user.id))
    updated_user = result.scalar_one()
    
    # Формируем ответ
    response_data = UserWithAvatarResponse.model_validate(updated_user)
    response_data.avatar_url = None
    return response_data


@router.get("/me/ads", response_model=list[AdResponse])
async def get_user_ads(
    status: str = Query("all", description="Статус объявлений: active, inactive, all"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Вернуть список объявлений текущего пользователя.
    Используется в интеграционном тесте TestUsersIntegration.test_get_user_ads.
    """
    from sqlalchemy.orm import selectinload
    
    stmt = (
        select(Ad)
        .options(selectinload(Ad.images))  # ← ДОБАВЬТЕ ЭТО
        .filter(Ad.user_id == current_user.id)
        .order_by(Ad.created_at.desc())
    )

    # Фильтр по статусу
    if status == "active":
        stmt = stmt.filter(Ad.status == AdStatus.ACTIVE)
    elif status == "inactive":
        stmt = stmt.filter(Ad.status == AdStatus.INACTIVE)
    # Если status == "all" или что-то другое, показываем все
    
    result = await db.execute(stmt)
    ads = list(result.scalars().all())

    # Pydantic будет обрабатывать преобразование images через model_validator
    # Не трогаем SQLAlchemy объекты напрямую
    return ads


@router.get("/{user_id}/public", response_model=UserPublicInfo)
async def get_user_public_info(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить публичную информацию о пользователе (имя, телефон, email)"""
    stmt = select(User).filter(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserPublicInfo(
        id=user.id,
        name=user.name,
        phone=user.phone,
        email=user.email
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка текущего пароля
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Установка нового пароля
    new_hashed_password = get_password_hash(password_data.new_password)
    stmt = (
        update(User)
        .where(User.id == current_user.id)
        .values(hashed_password=new_hashed_password, updated_at=func.now())
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Password updated successfully"}

@router.post("/me/deactivate")
async def deactivate_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        update(User)
        .where(User.id == current_user.id)
        .values(is_active=False, updated_at=func.now())
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Account deactivated successfully"}

@router.delete("/me/delete")
async def delete_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Полное удаление аккаунта пользователя"""
    user_id = current_user.id
    
    # Удаляем аватар если есть
    if current_user.avatar:
        file_service.delete_avatar(current_user.avatar)
    
    # Удаляем пользователя из базы данных
    stmt = delete(User).where(User.id == user_id)
    await db.execute(stmt)
    await db.commit()
    
    return {"message": "Account deleted successfully"}