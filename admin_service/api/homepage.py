# admin_service/api/homepage.py

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from services.s3_client import S3Client
from services.catalog_api import (
    get_banners, create_banner, delete_banner, update_banner,
    get_promos, create_promo, delete_promo
)
from schemas import PromoCreate
from core.config import settings
import uuid
import os
from utils.auth import get_current_admin_user
from models.admin import AdminUser
import logging
import httpx

router = APIRouter(prefix="/admin", tags=["Homepage"])
logger = logging.getLogger(__name__)

def _hdr():
    return {"Authorization": f"Bearer {settings.INTERNAL_TOKEN}"}

async def save_temp_file(file: UploadFile) -> tuple[str, str]:
    """
    Сохраняет файл во временное хранилище
    
    Returns:
        Кортеж (путь_к_файлу, имя_файла)
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Имя файла не указано")
    
    ext = os.path.splitext(file.filename)[1]
    if not ext:
        raise HTTPException(status_code=400, detail="Файл должен иметь расширение")
    
    filename = f"{uuid.uuid4()}{ext}"
    temp_path = f"/tmp/{filename}"
    
    try:
        contents = await file.read()
        with open(temp_path, "wb") as tmp:
            tmp.write(contents)
        return temp_path, filename
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {str(e)}")


async def upload_image(file: UploadFile) -> str:
    """
    Загружает изображение в S3 и возвращает URL
    
    Args:
        file: Загружаемый файл
        
    Returns:
        URL загруженного изображения
    """
    # Проверяем тип файла
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")
    
    # Проверяем расширение
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый формат изображения. Разрешены: {', '.join(allowed_extensions)}"
        )
    
    temp_path, raw_filename = await save_temp_file(file)
    
    try:
        s3 = S3Client(bucket_name=settings.S3_PUBLIC_BUCKET)
        folder = s3.get_folder(raw_filename)
        object_name = f"{folder}/{raw_filename}"
        
        url = await s3.upload_file(temp_path, object_name)
        
        logger.info(f"Изображение {file.filename} успешно загружено: {url}")
        return url
        
    except Exception as e:
        logger.error(f"Ошибка загрузки изображения {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки изображения: {str(e)}")
    finally:
        # Всегда удаляем временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)


# === БАННЕРЫ ===

@router.get("/banners/", summary="Список баннеров")
async def list_banners(current_admin: AdminUser = Depends(get_current_admin_user)):
    """Получает список всех баннеров"""
    logger.info(f"Админ {current_admin.username} запрашивает список баннеров")
    
    try:
        return await get_banners()
    except Exception as e:
        logger.error(f"Ошибка получения списка баннеров: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения баннеров: {str(e)}")


@router.post("/banners/", summary="Загрузить баннер")
async def add_banner(
    file: UploadFile = File(...),
    order: int = Form(0),
    title: str = Form(""),
    description: str = Form(""),
    link: str = Form(""),
    is_active: bool = Form(True),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создает новый баннер с изображением"""
    logger.info(f"Админ {current_admin.username} создает баннер: {file.filename}")
    
    try:
        # Загружаем изображение в S3
        image_url = await upload_image(file)
        
        # Создаем баннер
        banner_data = {
            "image": image_url,
            "order": order,
            "title": title,
            "description": description,
            "link": link,
            "is_active": is_active,
            "created_by": current_admin.username
        }
        
        result = await create_banner(banner_data)
        
        logger.info(f"Баннер успешно создан: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания баннера: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания баннера: {str(e)}")


@router.put("/banners/{banner_id}", summary="Обновить баннер")
async def edit_banner(
    banner_id: int,
    file: UploadFile = File(None),
    order: int = Form(None),
    title: str = Form(None),
    description: str = Form(None),
    link: str = Form(None),
    is_active: bool = Form(None),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Обновляет существующий баннер"""
    logger.info(f"Админ {current_admin.username} обновляет баннер {banner_id}")
    
    try:
        update_data = {}
        
        # Если загружено новое изображение
        if file and file.filename:
            image_url = await upload_image(file)
            update_data["image"] = image_url
        
        # Обновляем остальные поля (только если они переданы)
        if order is not None:
            update_data["order"] = order
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if link is not None:
            update_data["link"] = link
        if is_active is not None:
            update_data["is_active"] = is_active
            
        update_data["updated_by"] = current_admin.username
        
        result = await update_banner(banner_id, update_data)
        
        logger.info(f"Баннер {banner_id} успешно обновлен")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления баннера {banner_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления баннера: {str(e)}")


@router.delete("/banners/{banner_id}", summary="Удалить баннер")
async def remove_banner(
    banner_id: int, 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удаляет баннер"""
    logger.warning(f"Админ {current_admin.username} удаляет баннер {banner_id}")
    
    try:
        result = await delete_banner(banner_id)
        
        logger.info(f"Баннер {banner_id} успешно удален")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка удаления баннера {banner_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления баннера: {str(e)}")


# === ПРОМО-ИЗОБРАЖЕНИЯ ===

@router.get("/promos/", summary="Список промо-изображений")
async def list_promos(current_admin: AdminUser = Depends(get_current_admin_user)):
    """Получает список всех промо-изображений"""
    logger.info(f"Админ {current_admin.username} запрашивает список промо-изображений")
    
    try:
        return await get_promos()
    except Exception as e:
        logger.error(f"Ошибка получения списка промо-изображений: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения промо-изображений: {str(e)}")


@router.post("/promos/", summary="Загрузить промо-изображение")
async def add_promo(
    file: UploadFile = File(...),
    title: str = Form(""),
    description: str = Form(""),
    course_id: int = Form(None),
    order: int = Form(0),
    is_active: bool = Form(True),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Создает новое промо-изображение"""
    logger.info(f"Админ {current_admin.username} создает промо-изображение: {file.filename}")
    
    try:
        # Загружаем изображение в S3
        image_url = await upload_image(file)
        
        # Создаем промо
        promo_data = PromoCreate(
            image=image_url,
            title=title,
            description=description,
            course_id=course_id,
            order=order,
            is_active=is_active
        )
        
        result = await create_promo(promo_data)
        
        logger.info(f"Промо-изображение успешно создано: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания промо-изображения: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания промо-изображения: {str(e)}")


@router.put("/promos/{promo_id}", summary="Обновить промо-изображение")
async def edit_promo(
    promo_id: int,
    file: UploadFile = File(None),
    title: str = Form(None),
    description: str = Form(None),
    course_id: int = Form(None),
    order: int = Form(None),
    is_active: bool = Form(None),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Обновляет существующее промо-изображение"""
    logger.info(f"Админ {current_admin.username} обновляет промо-изображение {promo_id}")
    try:
        update_data = {}
        if file and file.filename:
            image_url = await upload_image(file)
            update_data["image"] = image_url
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if course_id is not None:
            update_data["course_id"] = course_id
        if order is not None:
            update_data["order"] = order
        if is_active is not None:
            update_data["is_active"] = is_active

        async with httpx.AsyncClient(base_url=settings.CATALOG_SERVICE_URL, timeout=15.0) as client:
            response = await client.put(
                f"/v1/admin/promos/{promo_id}",
                headers=_hdr(),
                json=update_data
            )
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Промо не найдено")
            response.raise_for_status()
            return response.json()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления промо-изображения {promo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления промо-изображения: {str(e)}")


@router.delete("/promos/{promo_id}", summary="Удалить промо-изображение")
async def remove_promo(
    promo_id: int, 
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удаляет промо-изображение"""
    logger.warning(f"Админ {current_admin.username} удаляет промо-изображение {promo_id}")
    
    try:
        result = await delete_promo(promo_id)
        
        logger.info(f"Промо-изображение {promo_id} успешно удалено")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка удаления промо-изображения {promo_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления промо-изображения: {str(e)}")


# === ДОПОЛНИТЕЛЬНЫЕ УТИЛИТЫ ===

@router.get("/upload-status/", summary="Статус загрузок")
async def get_upload_status(current_admin: AdminUser = Depends(get_current_admin_user)):
    """Возвращает статистику по загруженным файлам"""
    logger.info(f"Админ {current_admin.username} запрашивает статус загрузок")
    
    try:
        # Здесь можно добавить логику для получения статистики из S3
        return {
            "total_uploads": "unknown",
            "storage_used": "unknown", 
            "recent_uploads": [],
            "status": "ok"
        }
    except Exception as e:
        logger.error(f"Ошибка получения статуса загрузок: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса: {str(e)}")


@router.post("/clear-cache/", summary="Очистить кеш изображений")
async def clear_image_cache(current_admin: AdminUser = Depends(get_current_admin_user)):
    """Очищает кеш изображений (если используется CDN с кешированием)"""
    logger.info(f"Админ {current_admin.username} очищает кеш изображений")
    
    try:
        # TODO: Реализовать очистку кеша CDN
        return {
            "success": True,
            "message": "Команда на очистку кеша отправлена",
            "cleared_by": current_admin.username
        }
    except Exception as e:
        logger.error(f"Ошибка очистки кеша: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка очистки кеша: {str(e)}")