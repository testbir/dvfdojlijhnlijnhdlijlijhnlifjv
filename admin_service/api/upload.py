# admin_service/api/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from services.s3_client import S3Client
from services.video_processor import process_uploaded_video, VideoProcessingError
from core.config import settings
import uuid
import os
import tempfile
from utils.auth import get_current_admin_user
from models.admin import AdminUser
from typing import Dict, Optional
from datetime import datetime
from services.video_status import (
    set_video_status, get_video_status, update_video_status, 
    delete_video_status, get_all_statuses
)
import logging

router = APIRouter(prefix="/admin", tags=["Upload"])
logger = logging.getLogger(__name__)

# Константы
MAX_VIDEO_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
CHUNK_SIZE = 1024 * 1024  # 1MB для потоковой записи


async def save_temp_file(file: UploadFile, max_size: Optional[int] = None) -> tuple[str, str]:
    """
    Сохраняет файл во временное хранилище с потоковой записью
    
    Args:
        file: Загруженный файл
        max_size: Максимальный размер файла в байтах
        
    Returns:
        Кортеж (путь_к_файлу, имя_файла)
    """
    # Проверяем расширение
    ext = os.path.splitext(file.filename)[1].lower()
    if not ext:
        raise HTTPException(status_code=400, detail="Файл должен иметь расширение")
    
    # Генерируем уникальное имя
    filename = f"{uuid.uuid4()}{ext}"
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)
    
    # Потоковая запись с проверкой размера
    total_size = 0
    try:
        with open(temp_path, 'wb') as f:
            while chunk := await file.read(CHUNK_SIZE):
                total_size += len(chunk)
                
                # Проверяем размер
                if max_size and total_size > max_size:
                    # Удаляем частично записанный файл
                    f.close()
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"Файл слишком большой. Максимум: {max_size // (1024*1024)} MB"
                    )
                f.write(chunk)
        
        return temp_path, filename
        
    except Exception as e:
        # Убираем временный файл при ошибке
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e


async def upload_to_s3(
    file: UploadFile, 
    bucket_name: str, 
    allowed_extensions: set, 
    max_size: int
) -> Dict[str, str]:
    """
    Универсальная функция загрузки в S3
    
    Args:
        file: Загруженный файл
        bucket_name: Имя S3 bucket
        allowed_extensions: Разрешенные расширения
        max_size: Максимальный размер в байтах
        
    Returns:
        Словарь с данными о загруженном файле
    """
    # Валидация расширения
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
        )
    
    # Сохраняем временно
    temp_path, filename = await save_temp_file(file, max_size)
    
    try:
        # Загружаем в S3
        s3 = S3Client(bucket_name=bucket_name)
        folder = s3.get_folder(filename)
        object_name = f"{folder}/{filename}"
        
        cdn_url = await s3.upload_file(temp_path, object_name)
        
        # Получаем размер файла
        file_size = os.path.getsize(temp_path)
        
        return {
            "success": True,
            "filename": filename,
            "original_name": file.filename,
            "url": cdn_url,
            "size": file_size,
            "content_type": file.content_type,
            "folder": folder
        }
        
    except Exception as e:
        logger.error(f"Ошибка загрузки в S3: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка загрузки файла: {str(e)}"
        )
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/upload/public", summary="Загрузить публичное изображение")
async def upload_public_file(
    file: UploadFile = File(...),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Загружает изображения для публичного доступа"""
    logger.info(f"Админ {current_admin.username} загружает публичное изображение: {file.filename}")
    
    try:
        return await upload_to_s3(
            file, 
            settings.S3_PUBLIC_BUCKET,
            ALLOWED_IMAGE_EXTENSIONS,
            MAX_IMAGE_SIZE
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPLOAD ERROR (public): {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")


@router.post("/upload/content", summary="Загрузить курс-контент (изображения, документы)")
async def upload_content_file(
    file: UploadFile = File(...),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Загружает контент для курсов"""
    logger.info(f"Админ {current_admin.username} загружает контент: {file.filename}")
    
    try:
        # Для контента разрешаем и изображения, и документы
        allowed_extensions = ALLOWED_IMAGE_EXTENSIONS | {'.pdf', '.doc', '.docx'}
        return await upload_to_s3(
            file, 
            settings.S3_CONTENT_BUCKET,
            allowed_extensions,
            MAX_IMAGE_SIZE * 5  # 50MB для документов
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"UPLOAD ERROR (content): {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")


@router.post("/upload/video", summary="Загрузить и обработать видео для курса")
async def upload_video_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Загружает видео и запускает его обработку в фоне
    Возвращает video_id для отслеживания статуса
    """
    logger.info(f"Админ {current_admin.username} загружает видео: {file.filename}")
    
    # Валидация
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Файл должен быть видео")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат видео. Разрешены: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )
    
    # Генерируем уникальный ID для отслеживания
    video_id = str(uuid.uuid4())
    
    try:
        # Сохраняем временно
        temp_path, filename = await save_temp_file(file, MAX_VIDEO_SIZE)
        
        # Устанавливаем начальный статус
        await set_video_status(video_id, {
            "status": "uploading",
            "filename": filename,
            "original_name": file.filename,
            "temp_path": temp_path,
            "uploaded_by": current_admin.username,
            "started_at": datetime.utcnow().isoformat(),
            "progress": 0
        })
        
        # Запускаем обработку в фоне
        background_tasks.add_task(process_video_background, video_id, temp_path, filename)
        
        return {
            "success": True,
            "video_id": video_id,
            "message": "Видео загружено и поставлено в очередь на обработку",
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка при загрузке видео {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки видео: {str(e)}")


async def process_video_background(video_id: str, temp_path: str, filename: str):
    """
    Фоновая обработка видео
    """
    try:
        # Обновляем статус на "в очереди"
        await update_video_status(video_id, {
            "status": "queued",
            "message": "Видео в очереди на обработку"
        })
        
        # Обновляем статус на "обрабатывается"
        await update_video_status(video_id, {
            "status": "processing",
            "message": "Обработка видео началась",
            "processing_started_at": datetime.utcnow().isoformat()
        })
        
        # Запускаем обработку
        result = await process_uploaded_video(temp_path, filename)
        
        # Успешное завершение
        await update_video_status(video_id, {
            "status": "completed",
            "message": "Видео успешно обработано",
            "result": result,
            "completed_at": datetime.utcnow().isoformat(),
            "progress": 100
        })
        
        logger.info(f"✅ Видео {filename} успешно обработано. video_id: {video_id}")
        
    except VideoProcessingError as e:
        # Специфичная ошибка обработки
        await update_video_status(video_id, {
            "status": "failed",
            "message": f"Ошибка обработки: {str(e)}",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })
        logger.error(f"❌ Ошибка обработки видео {filename}: {str(e)}")
        
    except Exception as e:
        # Общая ошибка
        await update_video_status(video_id, {
            "status": "failed",
            "message": "Неизвестная ошибка при обработке видео",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })
        logger.error(f"❌ Критическая ошибка при обработке видео {filename}: {str(e)}")
    
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        # Удаляем временный путь из статуса
        current_status = await get_video_status(video_id)
        if current_status and "temp_path" in current_status:
            del current_status["temp_path"]
            await set_video_status(video_id, current_status)


@router.get("/video-status/{video_id}", summary="Проверить статус обработки видео")
async def check_video_status(
    video_id: str,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Возвращает текущий статус обработки видео
    
    Возможные статусы:
    - uploading: Видео загружается
    - queued: В очереди на обработку
    - processing: Обрабатывается
    - completed: Успешно обработано
    - failed: Ошибка обработки
    """
    status = await get_video_status(video_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail="Статус видео не найден"
        )
    
    return status


@router.get("/video-statuses/", summary="Получить все статусы обработки видео")
async def get_all_video_statuses(
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Возвращает все активные статусы обработки видео"""
    statuses = await get_all_statuses()
    return {"statuses": statuses}


@router.delete("/video-status/{video_id}", summary="Удалить статус обработки видео")
async def delete_video_status_endpoint(
    video_id: str,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удаляет статус обработки видео из хранилища"""
    logger.info(f"Админ {current_admin.username} удаляет статус видео: {video_id}")
    
    success = await delete_video_status(video_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Статус видео не найден"
        )
    
    return {"success": True, "message": "Статус удален"}