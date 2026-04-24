from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class FileVersion(BaseEntity):
    """
    Сущность версии файла.

    Принадлежит агрегату File.

    Атрибуты:
        version_number: Номер версии.
        storage_path: Путь к файлу в хранилище.
        size_bytes: Размер в байтах.
        uploader_id: ID загрузившего.
        change_summary: Описание изменений.
        uploaded_at: Время загрузки.
    """

    version_number: int = 1
    storage_path: str = ""
    size_bytes: int = 0
    uploader_id: Id = field(default_factory=Id.generate)
    change_summary: str | None = None
    uploaded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
