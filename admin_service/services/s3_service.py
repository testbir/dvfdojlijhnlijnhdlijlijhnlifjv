# admin_service/services/s3_service.py

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
import uuid
import logging
from typing import Optional
from admin_service.core.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.client = None
        if settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY:
            self.client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name='ru-1'
            )
        else:
            logger.warning("S3 credentials not configured")
    
    async def upload_image(
        self, 
        file: UploadFile, 
        folder: str = "images"
    ) -> str:
        """
        Загружает изображение в S3 и возвращает публичный URL
        
        Args:
            file: Загруженный файл
            folder: Папка в бакете для сохранения
            
        Returns:
            Публичный URL загруженного файла
        """
        if not self.client:
            raise HTTPException(
                status_code=500,
                detail="S3 storage not configured"
            )
        
        # Проверяем тип файла
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Генерируем уникальное имя файла
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        file_name = f"{folder}/{uuid.uuid4()}.{file_extension}"
        
        try:
            # Читаем содержимое файла
            file_content = await file.read()
            
            # Загружаем в S3
            self.client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_name,
                Body=file_content,
                ContentType=file.content_type,
                ACL='public-read'  # Делаем файл публично доступным
            )
            
            # Возвращаем публичный URL
            public_url = f"{settings.S3_PUBLIC_URL}/{file_name}"
            logger.info(f"Successfully uploaded image to S3: {public_url}")
            return public_url
            
        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload image to storage"
            )
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to process image upload"
            )
    
    async def delete_image(self, image_url: str) -> bool:
        """
        Удаляет изображение из S3
        
        Args:
            image_url: URL изображения для удаления
            
        Returns:
            True если успешно удалено
        """
        if not self.client:
            logger.warning("S3 not configured, skipping deletion")
            return False
        
        try:
            # Извлекаем ключ из URL
            if settings.S3_PUBLIC_URL in image_url:
                key = image_url.replace(f"{settings.S3_PUBLIC_URL}/", "")
            else:
                logger.warning(f"Unknown image URL format: {image_url}")
                return False
            
            # Удаляем объект
            self.client.delete_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=key
            )
            
            logger.info(f"Successfully deleted image from S3: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 deletion error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during deletion: {str(e)}")
            return False

# Создаем синглтон для использования в приложении
s3_service = S3Service()