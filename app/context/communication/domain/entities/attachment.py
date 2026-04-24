from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.shared.domain.value_objects.url_vo import Url
from app.context.communication.domain.value_objects.attachment_type import AttachmentType


@dataclass
class Attachment(BaseEntity):
    """
    Сущность вложения в комментарии/сообщении.

    Ссылка на файл в FileStorage BC.

    Атрибуты:
        file_id: Opaque ID файла (из FileStorage BC).
        url: URL файла.
        attachment_type: Тип вложения.
        name: Имя файла.
        size_bytes: Размер в байтах.
        preview_url: URL превью.
        created_at: Время создания.
    """

    file_id: Id = field(default_factory=Id.generate)
    url: Url | None = None
    attachment_type: AttachmentType = AttachmentType.FILE
    name: str = ""
    size_bytes: int = 0
    preview_url: Url | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
