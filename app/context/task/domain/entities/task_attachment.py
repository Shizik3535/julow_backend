from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id


@dataclass
class TaskAttachment(BaseEntity):
    """
    Сущность вложения задачи.

    Принадлежит агрегату Task. Ссылка на файл в FileStorage BC.

    Атрибуты:
        file_id: Opaque ID файла (из FileStorage BC).
        filename: Имя файла.
        size_bytes: Размер файла в байтах.
        uploaded_by: ID загрузившего.
        uploaded_at: Время загрузки.
    """

    file_id: Id = field(default_factory=Id.generate)
    filename: str = ""
    size_bytes: int = 0
    uploaded_by: Id = field(default_factory=Id.generate)
    uploaded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
