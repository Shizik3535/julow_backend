from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects.id_vo import Id
from app.context.filestorage.domain.value_objects.file_access_level import FileAccessLevel


@dataclass
class PublicShareLink(BaseEntity):
    """
    Сущность публичной ссылки на файл.

    Принадлежит агрегату File.

    Атрибуты:
        token: Уникальный токен ссылки.
        password_hash: Хеш пароля (None — без пароля).
        expires_at: Срок действия (None — бессрочно).
        access_level: Уровень доступа по ссылке.
        allow_download: Разрешено ли скачивание.
        max_uses: Макс. количество использований (None — без лимита).
        current_uses: Текущее количество использований.
        created_by: ID создавшего ссылку.
        created_at: Время создания.
    """

    token: str = ""
    password_hash: str | None = None
    expires_at: datetime | None = None
    access_level: FileAccessLevel = FileAccessLevel.VIEW
    allow_download: bool = True
    max_uses: int | None = None
    current_uses: int = 0
    created_by: Id = field(default_factory=Id.generate)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
