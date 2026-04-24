from __future__ import annotations

from enum import Enum


class StorageProvider(Enum):
    """
    Провайдер хранилища.

    Значения:
        AWS_S3: Amazon S3
        MINIO: MinIO
        LOCAL: Локальное хранилище
        AZURE_BLOB: Azure Blob Storage
        GCS: Google Cloud Storage
    """

    AWS_S3 = "aws_s3"
    MINIO = "minio"
    LOCAL = "local"
    AZURE_BLOB = "azure_blob"
    GCS = "gcs"
