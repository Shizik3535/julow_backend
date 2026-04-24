from __future__ import annotations

from enum import Enum


class StorageProvider(Enum):
    """
    Провайдер хранилища.

    Новые провайдеры = значение enum.

    Значения:
        S3: Amazon S3
        LOCAL: Локальное хранилище
        MINIO: MinIO
        GCS: Google Cloud Storage
        AZURE_BLOB: Azure Blob Storage
    """

    S3 = "s3"
    LOCAL = "local"
    MINIO = "minio"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"
