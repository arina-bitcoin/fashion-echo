# backend/app/api/v1/endpoints/files.py
@router.post("/upload/ad-image")
async def upload_ad_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Сохранение в file_storage/images/ads/
    # Валидация: размер, тип файла
    # Возврат пути к файлу
    pass