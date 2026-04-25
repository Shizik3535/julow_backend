from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UpdateOrgStorageRequest(BaseModel):
    """
    Тело запроса обновления хранилища организации.

    Атрибуты:
        provider: Новый провайдер.
        endpoint: Новый URL эндпоинта.
        bucket: Новое имя бакета.
        region: Новый регион.
        access_key: Новый ключ доступа (открытый текст).
        max_bytes: Новый максимальный объём.
        max_file_size_bytes: Новый максимальный размер файла.
        allowed_extensions: Новые разрешённые расширения.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "max_bytes": 21474836480,
                "allowed_extensions": [".png", ".jpg", ".pdf", ".docx"],
            },
        },
    )

    provider: str | None = Field(default=None, max_length=50, description="Новый провайдер")
    endpoint: str | None = Field(default=None, max_length=2048, description="Новый URL эндпоинта")
    bucket: str | None = Field(default=None, max_length=255, description="Новое имя бакета")
    region: str | None = Field(default=None, max_length=100, description="Новый регион")
    access_key: str | None = Field(default=None, description="Новый ключ доступа (открытый текст)")
    max_bytes: int | None = Field(default=None, ge=0, description="Новый максимальный объём (байты)")
    max_file_size_bytes: int | None = Field(default=None, ge=0, description="Новый максимальный размер файла (байты)")
    allowed_extensions: list[str] | None = Field(default=None, description="Новые разрешённые расширения")
