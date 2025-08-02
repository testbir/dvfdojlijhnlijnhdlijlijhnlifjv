
#admin_service/services/s3_client.py


from aiobotocore.session import get_session
from contextlib import asynccontextmanager
from core.config import settings
import os


class S3Client:
    def __init__(self, bucket_name: str):
        self.config = {
            "aws_access_key_id": settings.S3_ACCESS_KEY,
            "aws_secret_access_key": settings.S3_SECRET_KEY,
            "endpoint_url": f"https://{settings.S3_ENDPOINT_HOST}",
        }
        self.bucket_name = bucket_name
        self.session = get_session()

        # Выбор CDN-домена в зависимости от контейнера
        if bucket_name == settings.S3_PUBLIC_BUCKET:
            self.cdn_url = settings.S3_PUBLIC_CDN_URL
        elif bucket_name == settings.S3_CONTENT_BUCKET:
            self.cdn_url = settings.S3_CONTENT_CDN_URL
        else:
            self.cdn_url = f"https://{bucket_name}.{settings.S3_ENDPOINT_HOST}"

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file_path: str, object_name: str):
        content_type = self.guess_content_type(object_name)
        key = object_name


        extra_args = {
            "ContentType": content_type,
            "ContentDisposition": "inline",  # Чтобы не скачивалось принудительно
        }

        async with self.get_client() as client:
            with open(file_path, "rb") as file:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file,
                    **extra_args,
                )

        return f"{self.cdn_url}/{key}"

    def guess_content_type(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext in [".jpg", ".jpeg"]:
            return "image/jpeg"
        if ext == ".png":
            return "image/png"
        if ext == ".webp":
            return "image/webp"
        if ext == ".mp4":
            return "video/mp4"
        if ext == ".webm":
            return "video/webm"
        if ext == ".mkv":
            return "video/x-matroska"
        return "application/octet-stream"

    def get_folder(self, filename: str) -> str:
        ext = os.path.splitext(filename)[1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            return "images"
        if ext in [".mp4", ".webm", ".mkv"]:
            return "videos"
        return "other"
