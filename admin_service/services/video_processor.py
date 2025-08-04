# admin_service/services/video_processor.py

import subprocess
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import asyncio
import uuid
import json
from core.config import settings
from services.s3_client import S3Client


class VideoProcessingError(Exception):
    """Кастомное исключение для ошибок обработки видео"""
    pass


class VideoProcessor:
    """
    Основной процессор видео для ПРИВАТНОГО контента (курсы)
    Загружает в S3_CONTENT_BUCKET
    """
    def __init__(self):
        self.s3_client = S3Client(bucket_name=settings.S3_CONTENT_BUCKET)
        
    async def process_video_to_hls(
        self, 
        input_video_path: str, 
        video_id: str,
        timeout: int = 3600
    ) -> Dict[str, str]:
        """
        Обрабатывает видео и создает HLS-стрим с разными качествами
        
        Args:
            input_video_path: Путь к входному видео
            video_id: ID видео для создания уникальной папки
            timeout: Максимальное время обработки в секундах
            
        Returns:
            Dict с информацией о результате обработки
        """
        try:
            # Применяем таймаут ко всей операции
            result = await asyncio.wait_for(
                self._process_video_internal(input_video_path, video_id),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            raise VideoProcessingError(
                f"Обработка видео превысила лимит времени: {timeout} секунд"
            )
    
    async def _process_video_internal(
        self, 
        input_video_path: str, 
        video_id: str
    ) -> Dict[str, str]:
        """Внутренняя логика обработки видео"""
        temp_dir = None
        
        try:
            # Создаем временную директорию
            temp_dir = tempfile.mkdtemp(prefix=f"video_{video_id}_")
            output_dir = os.path.join(temp_dir, video_id)
            os.makedirs(output_dir, exist_ok=True)
            
            # Определяем качества для создания
            qualities = [
                {"name": "360p", "width": 640, "height": 360, "bitrate": "800k"},
                {"name": "480p", "width": 854, "height": 480, "bitrate": "1200k"},
                {"name": "720p", "width": 1280, "height": 720, "bitrate": "2500k"},
                {"name": "1080p", "width": 1920, "height": 1080, "bitrate": "4500k"}
            ]
            
            # Получаем информацию о видео
            video_info = await self._get_video_info(input_video_path)
            input_width = video_info.get('width', 1920)
            input_height = video_info.get('height', 1080)
            
            # Фильтруем качества, которые не превышают исходное разрешение
            available_qualities = [
                q for q in qualities 
                if q['width'] <= input_width and q['height'] <= input_height
            ]
            
            if not available_qualities:
                # Если исходное видео очень маленькое, берем минимальное качество
                available_qualities = [qualities[0]]
            
            # Создаем плейлисты для каждого качества
            playlist_info = []
            tasks = []
            
            for quality in available_qualities:
                task = self._create_quality_playlist(
                    input_video_path, 
                    output_dir, 
                    quality, 
                    video_id
                )
                tasks.append(task)
            
            # Запускаем все задачи параллельно
            results = await asyncio.gather(*tasks)
            playlist_info.extend(results)
            
            # Создаем мастер-плейлист
            master_playlist_path = await self._create_master_playlist(
                output_dir, 
                playlist_info, 
                video_id
            )
            
            # Загружаем все файлы в S3
            master_url = await self._upload_hls_files(output_dir, video_id)
            
            return {
                "master_playlist_url": f"{master_url}/master.m3u8",
                "base_url": master_url,
                "qualities": [info['quality'] for info in playlist_info],
                "duration": video_info.get('duration', 0),
                "width": input_width,
                "height": input_height
            }
            
        except Exception as e:
            raise VideoProcessingError(f"Ошибка обработки видео: {str(e)}")
        finally:
            # Очистка временных файлов
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def _create_quality_playlist(
        self, 
        input_path: str, 
        output_dir: str, 
        quality: Dict, 
        video_id: str
    ) -> Dict:
        """Создает плейлист для конкретного качества"""
        playlist_name = f"{quality['name']}.m3u8"
        segment_pattern = f"{quality['name']}_%03d.ts"
        
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:v', quality['bitrate'],
            '-b:a', '128k',
            '-vf', f"scale={quality['width']}:{quality['height']}",
            '-g', '48',  # GOP size
            '-keyint_min', '48',
            '-sc_threshold', '0',
            '-hls_time', '10',
            '-hls_list_size', '0',
            '-hls_segment_filename', os.path.join(output_dir, segment_pattern),
            '-preset', 'medium',  # Баланс между скоростью и качеством
            '-movflags', '+faststart',
            '-f', 'hls',
            os.path.join(output_dir, playlist_name)
        ]
        
        # Выполняем команду
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode()}")
            
        return {
            'quality': quality['name'],
            'playlist': playlist_name,
            'bandwidth': int(quality['bitrate'].replace('k', '')) * 1000,
            'width': quality['width'],             
            'height': quality['height']            
        }
    
    async def _get_video_info(self, video_path: str) -> Dict:
        """Получает информацию о видео"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_streams', '-show_format', video_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            info = json.loads(stdout.decode())
            video_stream = next(
                (stream for stream in info.get('streams', []) 
                 if stream.get('codec_type') == 'video'),
                {}
            )
            
            # Получаем длительность из format или stream
            duration = 0
            if 'format' in info and 'duration' in info['format']:
                duration = float(info['format']['duration'])
            elif 'duration' in video_stream:
                duration = float(video_stream['duration'])
            
            return {
                'width': video_stream.get('width', 1920),
                'height': video_stream.get('height', 1080),
                'duration': duration
            }
        else:
            # Если не удалось получить информацию, возвращаем значения по умолчанию
            return {'width': 1920, 'height': 1080, 'duration': 0}
    
    async def _create_master_playlist(
        self, 
        output_dir: str, 
        playlist_info: List[Dict], 
        video_id: str
    ) -> str:
        """Создает мастер-плейлист для HLS"""
        master_path = os.path.join(output_dir, "master.m3u8")
        
        with open(master_path, 'w') as f:
            f.write('#EXTM3U\n')
            f.write('#EXT-X-VERSION:3\n\n')
            
            for info in sorted(playlist_info, key=lambda x: x['bandwidth']):
                f.write(f'#EXT-X-STREAM-INF:BANDWIDTH={info["bandwidth"]},')
                f.write(f'RESOLUTION={info["width"]}x{info["height"]}\n')
                f.write(f'{info["playlist"]}\n\n')
        
        return master_path
    
    async def _upload_hls_files(self, local_dir: str, video_id: str) -> str:
        """Загружает все HLS файлы в S3 и возвращает базовый URL"""
        base_path = f"hls/{video_id}"
        upload_tasks = []
        
        # Собираем все файлы для загрузки
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_file_path, local_dir)
                s3_key = f"{base_path}/{relative_path}"
                
                # Определяем Content-Type
                if file.endswith('.m3u8'):
                    content_type = 'application/vnd.apple.mpegurl'
                elif file.endswith('.ts'):
                    content_type = 'video/mp2t'
                else:
                    content_type = 'application/octet-stream'
                
                # Добавляем задачу загрузки
                task = self._upload_file_to_s3(
                    local_file_path, 
                    s3_key, 
                    content_type
                )
                upload_tasks.append(task)
        
        # Загружаем все файлы параллельно
        await asyncio.gather(*upload_tasks)
        
        return f"{self.s3_client.cdn_url}/{base_path}"
    
    async def _upload_file_to_s3(
        self, 
        local_path: str, 
        s3_key: str, 
        content_type: str
    ):
        """Загружает один файл в S3"""
        async with self.s3_client.get_client() as client:
            with open(local_path, 'rb') as file:
                await client.put_object(
                    Bucket=self.s3_client.bucket_name,
                    Key=s3_key,
                    Body=file,
                    ContentType=content_type,
                    CacheControl='max-age=31536000, public'  # Кеш на год для сегментов
                )


class PublicVideoProcessor(VideoProcessor):
    """
    Видео процессор для ПУБЛИЧНЫХ видео (страница "О курсе")
    Загружает в публичный S3 контейнер
    """
    def __init__(self):
        # ВАЖНО: Используем PUBLIC bucket вместо CONTENT
        self.s3_client = S3Client(bucket_name=settings.S3_PUBLIC_BUCKET)
        
    async def _upload_hls_files(self, local_dir: str, video_id: str) -> str:
        """
        Загружает все HLS файлы в ПУБЛИЧНЫЙ S3 контейнер
        Переопределяем метод для использования публичного CDN
        """
        base_path = f"hls/{video_id}"
        upload_tasks = []
        
        # Собираем все файлы для загрузки
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_file_path, local_dir)
                s3_key = f"{base_path}/{relative_path}"
                
                # Определяем Content-Type
                if file.endswith('.m3u8'):
                    content_type = 'application/vnd.apple.mpegurl'
                elif file.endswith('.ts'):
                    content_type = 'video/mp2t'
                else:
                    content_type = 'application/octet-stream'
                
                # Используем метод _upload_file_to_s3 как в родительском классе
                upload_tasks.append(
                    self._upload_file_to_s3(
                        local_file_path, 
                        s3_key, 
                        content_type
                    )
                )
        
        # Загружаем все файлы параллельно
        await asyncio.gather(*upload_tasks)
        
        # Возвращаем базовый URL для ПУБЛИЧНОГО CDN
        return f"{settings.S3_PUBLIC_CDN_URL}/{base_path}"
    
    async def _upload_file_to_s3(
        self, 
        local_path: str, 
        s3_key: str, 
        content_type: str
    ):
        """Загружает один файл в ПУБЛИЧНЫЙ S3"""
        async with self.s3_client.get_client() as client:
            with open(local_path, 'rb') as file:
                await client.put_object(
                    Bucket=self.s3_client.bucket_name,
                    Key=s3_key,
                    Body=file,
                    ContentType=content_type,
                    CacheControl='max-age=31536000, public'  # Кеш на год для сегментов
                )


# ============= ГЛОБАЛЬНЫЕ ЭКЗЕМПЛЯРЫ =============

# Глобальный экземпляр для переиспользования
video_processor = VideoProcessor()
public_video_processor = PublicVideoProcessor()


# ============= ПУБЛИЧНЫЕ ФУНКЦИИ =============

async def process_uploaded_video(
    file_path: str, 
    video_id: str,
    timeout: int = 3600
) -> Dict[str, str]:
    """
    Основная функция для обработки ПРИВАТНОГО видео (курсы)
    
    Args:
        file_path: Путь к загруженному видео
        video_id: Уникальный ID для видео
        timeout: Максимальное время обработки
        
    Returns:
        Dict с результатами обработки
    """
    return await video_processor.process_video_to_hls(file_path, video_id, timeout)


async def process_public_uploaded_video(
    input_video_path: str, 
    video_id: str,
    timeout: int = 3600
) -> Dict[str, str]:
    """
    Обрабатывает видео для ПУБЛИЧНОГО доступа (страница О курсе)
    
    Args:
        input_video_path: Путь к входному видео файлу
        video_id: Уникальный ID для видео
        timeout: Максимальное время обработки
        
    Returns:
        Dict с информацией о результате обработки
    """
    return await public_video_processor.process_video_to_hls(input_video_path, video_id, timeout)