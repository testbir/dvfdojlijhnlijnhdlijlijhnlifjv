# admin_service/api/homepage.py


from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from utils.auth import get_current_user
from services.s3_client import S3Client
from services.catalog_api import (
    get_banners, create_banner, delete_banner,
    get_promos, create_promo, delete_promo
)
from schemas import PromoCreate
from core.config import settings
import uuid
import os
from fastapi import Form
from services.catalog_api import update_banner


router = APIRouter(prefix="/admin", tags=["Homepage"])


async def save_temp_file(file: UploadFile) -> tuple[str, str]:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    temp_path = f"/tmp/{filename}"
    contents = await file.read()
    with open(temp_path, "wb") as tmp:
        tmp.write(contents)
    return temp_path, filename


async def upload_image(file: UploadFile) -> str:
    temp_path, raw_filename = await save_temp_file(file)
    try:
        s3 = S3Client(bucket_name=settings.S3_PUBLIC_BUCKET)
        folder = s3.get_folder(raw_filename)
        object_name = f"{folder}/{raw_filename}"
        return await s3.upload_file(temp_path, object_name)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# === БАННЕРЫ ===

@router.get("/banners/", summary="Список баннеров")
async def list_banners(user_id: str = Depends(get_current_user)):
    return await get_banners()

@router.post("/banners/", summary="Загрузить баннер")
async def add_banner(
    file: UploadFile = File(...),
    order: int = 0,
    user_id: str = Depends(get_current_user)
):
    image_url = await upload_image(file)
    return await create_banner({"image": image_url, "order": order})

@router.delete("/banners/{banner_id}", summary="Удалить баннер")
async def remove_banner(banner_id: int, user_id: str = Depends(get_current_user)):
    return await delete_banner(banner_id)


# === ПРОМО-ИЗОБРАЖЕНИЯ ===

@router.get("/promos/", summary="Список промо-изображений")
async def list_promos(user_id: str = Depends(get_current_user)):
    return await get_promos()

@router.post("/promos/", summary="Добавить промо-изображение")
async def add_promo(
    course_id: int,
    order: int = 0,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    image_url = await upload_image(file)
    return await create_promo({
        "image": image_url,
        "course_id": course_id,
        "order": order
    })

@router.delete("/promos/{promo_id}", summary="Удалить промо")
async def remove_promo(promo_id: int, user_id: str = Depends(get_current_user)):
    return await delete_promo(promo_id)


@router.put("/banners/{banner_id}", summary="Обновить баннер")
async def edit_banner(
    banner_id: int,
    order: int = Form(...),
    link: str = Form(""),
    file: UploadFile = File(None),
    user_id: str = Depends(get_current_user)
):
    image_url = None
    if file:
        image_url = await upload_image(file)

    data = {"order": order, "link": link}
    if image_url:
        data["image"] = image_url

    return await update_banner(banner_id, data)
