from __future__ import annotations

from typing import Any

from aiobotocore.session import AioSession
from botocore.exceptions import ClientError

from app.core.logging import get_logger
from app.shared.application.ports.file_storage.file_storage_dto import FileInfo
from app.shared.application.ports.file_storage.file_storage_port import FileStoragePort

logger = get_logger(__name__)


class S3FileStorageAdapter(FileStoragePort):
    """
    Реализация FileStoragePort на основе aiobotocore (S3 / MinIO).

    Поддерживает загрузку, скачивание, удаление файлов,
    получение метаинформации и генерацию presigned URL.

    Аргументы конструктора:
        session: AioSession для создания S3 клиента.
        client_kwargs: Параметры для создания клиента (endpoint, credentials).
        bucket_name: Имя бакета.
        public_url_base: Базовый URL для публичных ссылок (для expires_in=None).
    """

    def __init__(
        self,
        session: AioSession,
        client_kwargs: dict[str, Any],
        bucket_name: str,
        public_url_base: str = "",
        presigned_url_base: str = "",
    ) -> None:
        self._session = session
        self._client_kwargs = client_kwargs
        self._bucket_name = bucket_name
        self._public_url_base = public_url_base
        self._presigned_url_base = presigned_url_base
        self._internal_endpoint = client_kwargs.get("endpoint_url", "")

    async def ensure_bucket(self) -> None:
        """Создать бакет, если он не существует."""
        async with self._session.create_client("s3", **self._client_kwargs) as client:
            try:
                await client.head_bucket(Bucket=self._bucket_name)
                logger.debug("Bucket already exists", bucket=self._bucket_name)
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "")
                if error_code in ("404", "NoSuchBucket"):
                    await client.create_bucket(Bucket=self._bucket_name)
                    logger.info("Bucket created", bucket=self._bucket_name)
                else:
                    raise

    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> FileInfo:
        async with self._session.create_client("s3", **self._client_kwargs) as client:
            await client.put_object(
                Bucket=self._bucket_name,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
            logger.info("File uploaded", key=key, size=len(data), content_type=content_type)
            return FileInfo(key=key, size=len(data), content_type=content_type)

    async def download(self, key: str) -> bytes:
        async with self._session.create_client("s3", **self._client_kwargs) as client:
            response = await client.get_object(Bucket=self._bucket_name, Key=key)
            body = await response["Body"].read()
            logger.debug("File downloaded", key=key, size=len(body))
            return body

    async def delete(self, key: str) -> None:
        async with self._session.create_client("s3", **self._client_kwargs) as client:
            await client.delete_object(Bucket=self._bucket_name, Key=key)
            logger.info("File deleted", key=key)

    async def get_info(self, key: str) -> FileInfo | None:
        async with self._session.create_client("s3", **self._client_kwargs) as client:
            try:
                response = await client.head_object(Bucket=self._bucket_name, Key=key)
                return FileInfo(
                    key=key,
                    size=response.get("ContentLength", 0),
                    content_type=response.get("ContentType", "application/octet-stream"),
                )
            except client.exceptions.NoSuchKey:
                logger.debug("File not found", key=key)
                return None
            except Exception as e:
                if "404" in str(e) or "Not Found" in str(e):
                    logger.debug("File not found", key=key)
                    return None
                raise

    async def get_url(self, key: str, expires_in: int | None = 3600) -> str:
        if expires_in is None:
            url = f"{self._public_url_base}/{self._bucket_name}/{key}"
            logger.debug("Public URL generated", key=key)
            return url

        async with self._session.create_client("s3", **self._client_kwargs) as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
            if self._presigned_url_base and self._internal_endpoint:
                url = url.replace(self._internal_endpoint, self._presigned_url_base, 1)
            logger.debug("Presigned URL generated", key=key, expires_in=expires_in)
            return url
