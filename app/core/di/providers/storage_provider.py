from aiobotocore.session import AioSession

from app.core.config.s3_settings import S3Settings
from app.shared.infrastructure.file_storage.s3_file_storage_adapter import S3FileStorageAdapter


def create_s3_session() -> AioSession:
    """Создать AioSession для S3 клиента."""
    return AioSession()


def get_s3_client_kwargs(settings: S3Settings) -> dict:
    """Сформировать параметры для создания S3 клиента."""
    return {
        "endpoint_url": settings.endpoint_url,
        "aws_access_key_id": settings.access_key,
        "aws_secret_access_key": settings.secret_key,
        "region_name": settings.region,
    }
