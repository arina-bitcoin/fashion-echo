from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from Backend.app.core.database import get_db
from Backend.app.core.security import verify_password, get_password_hash
from Backend.app.dependencies import get_current_active_user
from Backend.app.models.user import User
from Backend.app.schemas.user import UserResponse, UserUpdate, ChangePasswordRequest

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Обновление данных пользователя
    update_data = user_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Проверка текущего пароля
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Установка нового пароля
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.post("/me/deactivate")
async def deactivate_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    current_user.is_active = False
    db.commit()
    
    return {"message": "Account deactivated successfully"}