from __future__ import annotations

from datetime import datetime

from app.shared.application.base_dto import BaseDTO


class StorageIntegrationDTO(BaseDTO):
    """
    DTO хранилища организации (Organization BC).

    Атрибуты:
        id: Идентификатор хранилища.
        org_id: ID организации.
        provider: Провайдер хранилища.
        endpoint: URL эндпоинта.
        bucket: Имя бакета.
        region: Регион.
        max_bytes: Максимальный объём.
        used_bytes: Использованный объём.
        max_file_size_bytes: Максимальный размер файла.
        allowed_extensions: Разрешённые расширения.
        created_at: Время создания.
        updated_at: Время последнего обновления.
    """

    id: str
    org_id: str
    provider: str = "LOCAL"
    endpoint: str | None = None
    bucket: str = ""
    region: str = ""
    max_bytes: int = 0
    used_bytes: int = 0
    max_file_size_bytes: int | None = None
    allowed_extensions: list[str] | None = None
    created_at: datetime
    updated_at: datetime
