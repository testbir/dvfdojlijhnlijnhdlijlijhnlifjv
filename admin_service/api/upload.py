# admin_service/api/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from services.s3_client import S3Client
from services.video_processor import process_uploaded_video, VideoProcessingError
from utils.auth import get_current_user
from core.config import settings
import uuid
import os
import tempfile
import aiofiles
from utils.auth import get_current_admin_user
from models.admin import AdminUser
from typing import Dict, Optional
from datetime import datetime
from utils.auth import get_current_admin_user
from models.admin import AdminUser
from services.video_status import (
    set_video_status, get_video_status, update_video_status, 
    delete_video_status, get_all_statuses
)


router = APIRouter(prefix="/admin", tags=["Upload"])

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
        async with aiofiles.open(temp_path, 'wb') as f:
            while chunk := await file.read(CHUNK_SIZE):
                total_size += len(chunk)
                
                # Проверяем размер
                if max_size and total_size > max_size:
                    # Удаляем частично записанный файл
                    await f.close()
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"Файл слишком большой. Максимум: {max_size // (1024**2)}MB"
                    )
                
                await f.write(chunk)
                
    except Exception as e:
        # Очистка при ошибке
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        raise

    return temp_path, filename


async def upload_to_s3(
    file: UploadFile, 
    bucket_name: str,
    allowed_extensions: set,
    max_size: int
) -> dict:
    """Загружает файл в S3 с валидацией"""
    # Проверяем расширение
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
        )
    
    # Сохраняем временный файл
    temp_path, raw_filename = await save_temp_file(file, max_size)
    
    try:
        s3 = S3Client(bucket_name=bucket_name)
        folder = s3.get_folder(raw_filename)
        object_name = f"{folder}/{raw_filename}"
        file_url = await s3.upload_file(temp_path, object_name)
        content_type = s3.guess_content_type(raw_filename)
        
        return {
            "url": file_url,
            "folder": folder,
            "filename": raw_filename,
            "content_type": content_type,
            "size": os.path.getsize(temp_path)
        }
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


@router.post("/upload/public", summary="Загрузить публичный файл (аватар, постер и т.п.)")
async def upload_public_file(
    file: UploadFile = File(...),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Загружает изображения для публичного доступа"""
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
        print(f"UPLOAD ERROR (public): {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")


@router.post("/upload/content", summary="Загрузить курс-контент (изображения, документы)")
async def upload_content_file(
    file: UploadFile = File(...),
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Загружает контент для курсов"""
    try:
        # Для контента разрешаем и изображения
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
        print(f"UPLOAD ERROR (content): {repr(e)}")
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
    # Валидация
    if not file.content_type or not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Файл должен быть видео")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат видео. Разрешены: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )
    
    video_id = None
    try:
        # Генерируем ID для видео
        video_id = str(uuid.uuid4())
        
        # Инициализируем статус в Redis
        initial_status = {
            "status": "uploading",
            "message": "Загрузка видео...",
            "progress": 0,
            "created_at": datetime.utcnow().isoformat(),
            "filename": file.filename
        }
        await set_video_status(video_id, initial_status)
        
        # Сохраняем временный файл
        temp_path, filename = await save_temp_file(file, MAX_VIDEO_SIZE)
        
        # Обновляем статус
        await update_video_status(video_id, {
            "status": "queued",
            "message": "Видео в очереди на обработку",
            "temp_path": temp_path
        })
        
        # Запускаем обработку в фоне
        background_tasks.add_task(
            process_video_background, 
            temp_path, 
            filename, 
            video_id,
            user_id
        )
        
        return {
            "video_id": video_id,
            "status": "queued",
            "message": "Видео загружено и поставлено в очередь на обработку",
            "check_status_url": f"/admin/video-status/{video_id}"
        }
        
    except HTTPException:
        # Очищаем статус при ошибке
        if video_id:
            await delete_video_status(video_id)
        raise
    except Exception as e:
        print(f"VIDEO UPLOAD ERROR: {repr(e)}")
        if video_id:
            await delete_video_status(video_id)
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки видео: {str(e)}")


async def process_video_background(
    temp_path: str, 
    filename: str, 
    video_id: str,
    user_id: str
):
    """Фоновая обработка видео с обновлением статуса"""
    try:
        # Обновляем статус
        await update_video_status(video_id, {
            "status": "processing",
            "message": "Обработка видео началась...",
            "progress": 10
        })
        
        # Обрабатываем видео
        result = await process_uploaded_video(temp_path, video_id)
        
        # Обновляем статус на успешный
        await update_video_status(video_id, {
            "status": "completed",
            "message": "Видео успешно обработано",
            "progress": 100,
            "completed_at": datetime.utcnow().isoformat(),
            "result": {
                "master_playlist_url": result['master_playlist_url'],
                "qualities": result['qualities'],
                "duration": result.get('duration', 0),
                "resolution": result.get('resolution', 'unknown')
            }
        })
        
        print(f"✅ Видео {filename} (ID: {video_id}) успешно обработано")
        print(f"   Мастер-плейлист: {result['master_playlist_url']}")
        print(f"   Доступные качества: {', '.join(result['qualities'])}")
        
        # TODO: Здесь можно сохранить результат в базу данных
        # await save_video_to_database(video_id, user_id, result)
        
        # TODO: Отправить уведомление пользователю
        # await notify_user(user_id, video_id, "completed")
        
    except VideoProcessingError as e:
        # Специфичная ошибка обработки
        await update_video_status(video_id, {
            "status": "failed",
            "message": f"Ошибка обработки: {str(e)}",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })
        print(f"❌ Ошибка обработки видео {filename}: {str(e)}")
        
    except Exception as e:
        # Общая ошибка
        await update_video_status(video_id, {
            "status": "failed",
            "message": "Неизвестная ошибка при обработке видео",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })
        print(f"❌ Критическая ошибка при обработке видео {filename}: {str(e)}")
    
    finally:
        # Удаляем временный путь из статуса (если он там есть)
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
            detail="Видео с таким ID не найдено"
        )
    
    # Убираем служебную информацию
    response = {k: v for k, v in status.items() if k != "temp_path"}
    
    return response


@router.delete("/video-status/{video_id}", summary="Удалить статус обработки видео")
async def remove_video_status(
    video_id: str,
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Удаляет статус обработки видео из памяти"""
    status = await get_video_status(video_id)
    
    if status:
        await delete_video_status(video_id)
        return {"message": "Статус удален"}
    
    raise HTTPException(
        status_code=404,
        detail="Видео с таким ID не найдено"
    )


@router.get("/video-processing-queue", summary="Получить очередь обработки видео")
async def get_processing_queue(
    current_admin: AdminUser = Depends(get_current_admin_user)
):
    """Возвращает список всех видео в обработке"""
    # Получаем все статусы из Redis
    all_statuses = await get_all_statuses()
    
    # Фильтруем только активные задачи
    active_statuses = {
        vid: status for vid, status in all_statuses.items()
        if status.get("status") in ["uploading", "queued", "processing"]
    }
    
    return {
        "total": len(all_statuses),
        "active": len(active_statuses),
        "videos": [
            {
                "video_id": vid,
                **{k: v for k, v in status.items() if k != "temp_path"}
            }
            for vid, status in all_statuses.items()
        ]
    }


# Функция cleanup_old_statuses больше не нужна - Redis TTL автоматически удаляет старые записи